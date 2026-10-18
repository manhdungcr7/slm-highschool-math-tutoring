# -*- coding: utf-8 -*-
"""Collect freshly generated variants and keep only the ones that are really new.

A new question is kept when
  * its key is not the key of any question already in the project (source questions and the 90 existing variants), and
  * its key is not repeated inside the new set.
The key is the stem (question without options) for types whose stems differ from question to question, and the stem
together with the SET of options for the four types whose stem is the same sentence every time (ML_D06, ML_D13,
ML_D36a, SP_D10), because there the content sits in the options.
Same stem with the options in another order or with other wrong options counts as the SAME question.
"""
import json
import re

from common import options, stem

GENERIC_STEM_TYPES = {"ML_D06", "ML_D13", "ML_D36a", "SP_D10"}


def squash(text):
    s = text.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    s = re.sub(r"\\left|\\right", "", s)
    s = s.replace("$", "")
    s = re.sub(r"\s+", "", s)
    return s


def question_key(label, text):
    st = squash(stem(text))
    if label in GENERIC_STEM_TYPES:
        opts = sorted(squash(v) for v in options(text).values())
        return st + "||" + "|".join(opts)
    return st


def load_json_rows(path):
    return json.load(open(path, encoding="utf-8"))
