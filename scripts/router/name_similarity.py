# -*- coding: utf-8 -*-
"""List the pairs of routing names that look most alike, with what is different between them.

python name_similarity.py [N]      N = number of pairs to print (default 45)
"""
import difflib
import sys

from sklearn.feature_extraction.text import TfidfVectorizer

import catalogue_ml
import catalogue_sp

ENTRIES = catalogue_sp.ENTRIES + catalogue_ml.ENTRIES


def diff_words(a, b):
    wa, wb = a.split(), b.split()
    sm = difflib.SequenceMatcher(None, wa, wb)
    only_a, only_b = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            only_a.append(" ".join(wa[i1:i2]))
        if tag in ("replace", "insert"):
            only_b.append(" ".join(wb[j1:j2]))
    return " ".join(only_a), " ".join(only_b)


def main(n):
    names = [e["name"] for e in ENTRIES]
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True)
    X = vec.fit_transform(names)
    S = (X @ X.T).toarray()
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pairs.append((S[i, j], i, j))
    pairs.sort(reverse=True)
    for s, i, j in pairs[:n]:
        a, b = ENTRIES[i], ENTRIES[j]
        da, db = diff_words(a["name"], b["name"])
        print(f"{s:.3f}  {a['code']} vs {b['code']}")
        print(f"        A: {a['name']}")
        print(f"        B: {b['name']}")
        print(f"        khác nhau -> A: [{da}]   B: [{db}]")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 45)
