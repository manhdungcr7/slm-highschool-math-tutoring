# -*- coding: utf-8 -*-
"""
Calculator tool backend for the ReAct + Calculator experiments on
Exponential and Logarithm problems.

One SymPy based calculator with variable memory per question:
  - "name = expression" stores the exact result under that name.
  - "Eq(a, b)" returns True or False, decided exactly.
  - Inequalities such as "a < b" return True or False, decided numerically
    to 50 digits when both sides are constant expressions.
  - free unknowns (for example x) may be used without prior assignment.

This file is embedded verbatim into the Kaggle notebook by
build_react_notebook.py, and it is also imported locally to produce the
real Observation lines of the worked example and to run the regression
check, so the notebook and the checks can never drift apart.
"""
import re

import sympy as sp

ASSIGN_RE = re.compile(r'^([A-Za-z_]\w*)\s*=\s*(.+)$', re.S)
# Names that already mean something to the Calculator (functions such as N, Min, floor and
# constants such as E, I, S). Storing a value under one of them would silently replace it,
# for example "N = 94" would make the later call N(...) fail for the rest of the question.
RESERVED_NAMES = {n for n in dir(sp) if not n.startswith('_')}
RELATIONAL = (sp.StrictLessThan, sp.LessThan, sp.StrictGreaterThan, sp.GreaterThan, sp.Unequality)


class Calculator:
    """SymPy calculator with variable memory (one fresh instance per question)."""

    def __init__(self, free_unknowns=()):
        self.free_unknowns = set(free_unknowns)
        # Free unknowns are registered up front as REAL symbols; letting
        # sympify create them lazily would make them generic complex symbols.
        self.ns = {name: sp.Symbol(name, real=True) for name in self.free_unknowns}

    def _undefined_names(self, expr):
        free = getattr(expr, 'free_symbols', set())
        missing = {str(s) for s in free} - self.free_unknowns
        if not missing:
            return None
        unknown = ', '.join(sorted(missing))
        in_memory = ', '.join(sorted(self.ns)) or '(nothing stored yet)'
        allowed = ', '.join(sorted(self.free_unknowns)) or '(none)'
        return (f'undefined name(s): {unknown}. You used a name that is not in '
                f'calculator memory and is not a declared free unknown. Names '
                f'currently in memory: {in_memory}. Declared free unknowns '
                f'(allowed without prior assignment): {allowed}. Either compute '
                'and store that name first (with "name = expression"), or '
                'rewrite the expression without it.')

    def _unknown_functions(self, parsed):
        """Names used as functions that the Calculator does not know (ceil, log10, int, ...).

        SymPy accepts any unknown name followed by parentheses and silently keeps it as an
        unevaluated symbol, so "count = ceil(115.36) - 1" would be stored as if it were a
        result. Refuse it with a message that says what to write instead."""
        items = parsed if isinstance(parsed, (list, tuple, sp.FiniteSet)) else [parsed]
        names = set()
        for item in items:
            for node in getattr(item, 'atoms', lambda *a: set())(sp.core.function.AppliedUndef):
                names.add(type(node).__name__)
        if not names:
            return None
        return (f'unknown function(s): {", ".join(sorted(names))}. The Calculator does not know '
                'these names, so nothing was computed. Use only: log, exp, sqrt, floor, '
                'ceiling, Abs, Min, Max, N, solve, expand, factor, diff, nroots, Eq. '
                'For example: round up with ceiling(u), round down with floor(u), a logarithm '
                'to base b as log(u)/log(b).')

    def _decide_relational(self, rel):
        """True or False for an inequality between constant expressions."""
        err = self._undefined_names(rel.lhs - rel.rhs)
        if err:
            return None, err
        if rel.lhs.free_symbols or rel.rhs.free_symbols:
            return None, ('cannot decide an inequality that still contains an '
                          'unknown. Substitute numbers first.')
        diff = sp.N(rel.lhs - rel.rhs, 50)
        if abs(diff) < sp.Float('1e-40'):
            diff = sp.Integer(0)
        table = {sp.StrictLessThan: diff < 0, sp.LessThan: diff <= 0,
                 sp.StrictGreaterThan: diff > 0, sp.GreaterThan: diff >= 0,
                 sp.Unequality: diff != 0}
        return ('True' if table[type(rel)] else 'False'), None

    def _boolean_result(self, name, truth):
        """Format a True/False answer; store it when it was assigned to a name."""
        text = 'True' if truth else 'False'
        if name:
            self.ns[name] = sp.true if truth else sp.false
            return f'{name} = {text}', None
        return text, None

    def evaluate(self, expression):
        """Return (result_text, error_text). Exactly one of them is None."""
        s = expression.strip()
        if not s:
            return None, 'empty expression'
        if '==' in s:
            return None, ('"==" is not supported. To compare two expressions '
                          'exactly, write Eq(left, right) instead.')

        name = None
        m = ASSIGN_RE.match(s)
        # "x = Eq(...)" is an assignment; a bare "Eq(a, b)" has no top level "=".
        if m and not s.lstrip().startswith('Eq('):
            name, s = m.group(1), m.group(2)
            if name in self.free_unknowns:
                return None, (f'"{name}" is a declared unknown used by solve(...) and cannot be '
                              'a variable name. Choose another name and store the value again.')
            if name in RESERVED_NAMES:
                return None, (f'"{name}" cannot be used as a variable name because it is the name '
                              'of a Calculator function or constant (for example N(expression, '
                              'digits) computes a decimal value). Choose another name, such as a '
                              'descriptive word, and store the value again.')

        try:
            parsed = sp.sympify(s, locals=self.ns)
        except Exception as e:
            return None, f'{type(e).__name__}: {e}'

        err = self._unknown_functions(parsed)
        if err:
            return None, err

        try:
            if isinstance(parsed, sp.Equality):
                err = self._undefined_names(parsed.lhs - parsed.rhs)
                if err:
                    return None, err
                same = sp.simplify(parsed.lhs - parsed.rhs) == 0
                return self._boolean_result(name, same)

            if isinstance(parsed, RELATIONAL):
                text, err = self._decide_relational(parsed)
                if err:
                    return None, err
                return self._boolean_result(name, text == 'True')

            if isinstance(parsed, (sp.logic.boolalg.BooleanTrue, sp.logic.boolalg.BooleanFalse)):
                return self._boolean_result(name, bool(parsed))

            if isinstance(parsed, (list, tuple, sp.FiniteSet)):
                # Result of solve(...): a list of solutions. Check each element
                # separately instead of simplifying the list as a whole.
                items = list(parsed)
                for item in items:
                    err = self._undefined_names(item)
                    if err:
                        return None, err
                if name:
                    self.ns[name] = items
                    return f'{name} = {items}', None
                return str(items), None

            value = sp.expand(sp.simplify(parsed))
            err = self._undefined_names(value)
            if err:
                return None, err
            if name:
                self.ns[name] = value
                return f'{name} = {value}', None
            return str(value), None
        except Exception as e:
            return None, f'{type(e).__name__}: {e}'
