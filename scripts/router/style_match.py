# -*- coding: utf-8 -*-
"""Make sure that every WAY OF WRITING that occurs in the test questions of a dạng also occurs in the training questions of that dạng.

For every test style (see style_gap.signature) that has fewer than K training questions, some training questions of the dạng are
rewritten into that style. Only the presentation is changed: the opening sentence (the test sentence with the training question's
own maths put in), the line break, the LaTeX brackets and spacing, the kind of options, the base of the logarithm, the right-hand side.
The mathematics, the options' values and the label do not change. No test question is copied: the result is checked against all of them.
"""
import re
from collections import Counter

from augment_train import compact, math_only, spaced_equals, t_inequality_options, t_plain_options, t_rhs_number
from style_gap import content_key, matches, signature, split

K = 3                      # training questions required for every test style


def _math_pieces(line):
    return re.findall(r"\$.+?\$", line)


def _set_kind(opts, current, target):
    stats = Counter()
    if current == target:
        return True
    if current == "dollar_int" and target == "plain_int":
        t_plain_options(opts, stats)
    elif current == "interval" and target == "inequality":
        t_inequality_options(opts, stats)
    elif current == "plain_int" and target == "dollar_int":
        for i, o in enumerate(opts):
            opts[i] = re.sub(r"^([A-D])\. (-?\d+)\.$", r"\1. $\2$.", o)
    else:
        return False
    return True


def _map_math(lines, f):
    return [math_only(f)(l) for l in lines]


def _bare(m):
    m = re.sub(r"_\{(\d)\}", r"_\1", m)
    return re.sub(r"\^\{(\d)\}", r"^\1", m)


def _braced(m):
    m = re.sub(r"_(\d)(?!\d)", r"_{\1}", m)
    return re.sub(r"\^(\d)(?!\d)", r"^{\1}", m)


def _tight(m):
    m = re.sub(r"(\d) ([a-z\\])", r"\1\2", m)
    return m.replace(" - ", "-").replace(" + ", "+")


def restyle(original, target, example, number=None):
    """original: a training question (generator style). target: a style signature. example: a test question written in that style.
       Returns the rewritten question, or None when the style cannot be reached without changing the mathematics."""
    stem, opts = split(original)
    t_stem, _ = split(example)
    tl = t_stem[-1]
    cur = signature(original)
    # 1) opening sentence: the test sentence, with the maths of the training question put in its place
    if cur[1] != target[1]:
        parts = re.split(r"(\$.+?\$)", tl)
        slots = [i for i, p in enumerate(parts) if p.startswith("$") and p.endswith("$") and len(p) > 2]
        mine = _math_pieces(stem[-1])
        if len(slots) != len(mine):
            return None
        for i, m in zip(slots, mine):
            parts[i] = m
        stem[-1] = "".join(parts)
    # 2) options
    if not _set_kind(opts, cur[5], target[5]):
        return None
    # 3) the logarithm without a base (only when the base is 10 everywhere, so the question stays the same)
    allm = "\n".join(stem + opts)
    if target[6] == "no_base" and cur[6] == "base":
        bases = set(re.findall(r"\\log_\{?(\d+)\}?", allm))
        if number == 26:                          # log(ab^n) = log a + n log b in any base: only the base is dropped
            pass
        elif number == 15 and len(bases) == 1:    # (log_B x)' = 1/(x ln B): B is free, take 10 everywhere
            b10 = next(iter(bases))
            sub = lambda t: re.sub(r"(?<!\d)" + b10 + r"(?!\d)", "10", t)
            stem, opts = [sub(l) for l in stem], [sub(o) for o in opts]
        elif bases != {"10"}:
            return None
        stem = [re.sub(r"\\log_\{?\d+\}?", r"\\log", l) for l in stem]
        opts = [re.sub(r"\\log_\{?\d+\}?", r"\\log", o) for o in opts]
    elif target[6] != cur[6] and not (cur[6] == "-" or target[6] == "-"):
        return None
    # 4) right-hand side
    if target[7] == "num" and cur[7] == "pow":
        t_rhs_number(stem, Counter())
    # 5) LaTeX brackets, operator spacing, '=' spacing
    if target[2] == "bare":
        stem, opts = _map_math(stem, _bare), _map_math(opts, _bare)
    elif target[2] == "braced":
        stem, opts = _map_math(stem, _braced), _map_math(opts, _braced)
    if target[3] == "tight":
        stem, opts = _map_math(stem, _tight), _map_math(opts, _tight)
    if target[4] == "spaced":
        stem = _map_math(stem, spaced_equals)
    elif target[4] == "tight":
        stem = _map_math(stem, lambda m: m.replace(" = ", "="))
    # 6) line break
    body = "\n".join(stem) + ("\n\n" if target[0] == "blank" else "\n") + "\n".join(opts)
    return body if matches(signature(body), target) else None


def match_styles(bodies, originals, numbers, test_by_number, forbidden, rnd):
    """bodies: current training questions (modified in place); originals: the generator's versions; numbers: dạng of each row.
       test_by_number: dạng -> list of test question bodies. forbidden: normalised keys that must not appear (test + already used)."""
    norm = content_key
    report = []
    for n in sorted(test_by_number):
        idx = [i for i, x in enumerate(numbers) if x == n]
        example = {}
        for b in test_by_number[n]:
            example.setdefault(signature(b), b)
        sigs = {i: signature(bodies[i]) for i in idx}
        covered = lambda t: sum(1 for i in idx if matches(sigs[i], t))
        locked = set()
        for tsig, ex in sorted(example.items(), key=lambda kv: covered(kv[0])):
            need = K - covered(tsig)
            if need <= 0:
                continue
            # rows whose own style is shared by many questions come first; never take the last rows of a style that is needed
            def spare(i):
                return all(covered(t) > K or not matches(sigs[i], t) for t in example)
            order = sorted((i for i in idx if i not in locked and not matches(sigs[i], tsig)), key=lambda i: rnd.random())
            order = [i for i in order if spare(i)] + [i for i in order if not spare(i)][:0]
            for i in order:
                if need <= 0:
                    break
                nb = restyle(originals[i], tsig, ex, n)
                if nb is None or (norm(nb) in forbidden and norm(nb) != norm(bodies[i])):      # same content as before is fine, new content must be new
                    continue
                forbidden.discard(norm(bodies[i]))
                forbidden.add(norm(nb))
                bodies[i] = nb
                sigs[i] = signature(nb)
                locked.add(i)
                need -= 1
            if need > 0:
                report.append((n, tsig, need))
    return report
