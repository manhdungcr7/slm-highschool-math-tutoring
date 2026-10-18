# -*- coding: utf-8 -*-
"""Dạng 49 (bất phương trình lôgarit  log_a(px+q) > c  with the sign '>'): the generator never produced the base-10 logarithm
written without a base, which is how textbooks write it (log(x-2) > 0). These questions are generated here, exactly in the shape of
the generator's own questions: a stem 'Tập nghiệm của bất phương trình $log(px+q)>c$ là' and four intervals, one of them correct.

  log(px+q) > c   <=>   px+q > 10^c   <=>   x > (10^c - q) / p        (p > 0)
"""
import random
from fractions import Fraction


def num(v):
    v = Fraction(v)
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v.denominator == 1:
        return f"{sign}{v.numerator}"
    return f"{sign}\\dfrac{{{v.numerator}}}{{{v.denominator}}}"


def right(v):
    return f"\\left({num(v)};+\\infty\\right)"


def left(v):
    return f"\\left(-\\infty;{num(v)}\\right)"


def linear(p, q):
    head = "x" if p == 1 else f"{p}x"
    if q == 0:
        return head
    return f"{head}+{q}" if q > 0 else f"{head}{q}"


def make(rnd, blank):
    while True:
        p = rnd.choice([1, 1, 2, 3, 4, 5])
        q = rnd.choice([0, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 8])
        c = rnd.choice([1, 2, 3])
        t = Fraction(10 ** c - q, p)
        wrong = []
        for cand in (Fraction(10 ** c, p), Fraction(10 ** c + q, p), Fraction(-q, p) if q else Fraction(10 ** c - 1, p), t + 1):
            if cand != t and cand not in wrong:
                wrong.append(cand)
        if len(wrong) < 2:
            continue
        options = [right(t), left(t), right(wrong[0]), right(wrong[1])]
        if len(set(options)) < 4:
            continue
        rnd.shuffle(options)
        stem = f"Tập nghiệm của bất phương trình $\\log({linear(p, q)})>{c}$ là"
        body = stem + ("\n\n" if blank else "\n") + "\n".join(f"{'ABCD'[i]}. ${o}$." for i, o in enumerate(options))
        return body


if __name__ == "__main__":
    rnd = random.Random(1)
    for _ in range(3):
        print(make(rnd, blank=False))
        print()
