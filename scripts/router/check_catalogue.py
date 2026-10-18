# -*- coding: utf-8 -*-
"""Check a catalogue against every question of its topic.

For every question: the signature of its own type must match (coverage) and no other signature may match (exclusivity).
Also checks that codes and names are unique.

python check_catalogue.py SP        python check_catalogue.py ML        python check_catalogue.py ALL
"""
import collections
import importlib
import re
import sys

from common import load_questions, norm


def entries_for(topic):
    out = []
    for t in (("SP", "ML") if topic == "ALL" else (topic,)):
        out += importlib.import_module("catalogue_" + t.lower()).ENTRIES
    return out


def main(topic):
    old_names, rows = load_questions()
    entries = entries_for(topic)
    rows = [r for r in rows if topic == "ALL" or r["topic"] == topic]
    ok = True

    codes = [e["code"] for e in entries]
    dup = [c for c, n in collections.Counter(codes).items() if n > 1]
    names = [e["name"] for e in entries]
    dupn = [n for n, k in collections.Counter(names).items() if k > 1]
    # keep the comparison and inequality signs, they can be the only thing that separates two names
    low = collections.Counter(re.sub(r"[^\w<>≤≥=]+", "", n.lower().replace("lớn hơn", ">").replace("nhỏ hơn", "<")) for n in names)
    dupl = [n for n, k in low.items() if k > 1]
    print(f"{len(entries)} entries; duplicate codes: {dup}; duplicate names: {dupn}; duplicate after normalising: {dupl}")
    data_codes = {r["label"] for r in rows}
    print("types in data but not in catalogue:", sorted(data_codes - set(codes)),
          "| in catalogue but not in data:", sorted(set(codes) - data_codes))
    ok &= not (dup or dupn or dupl or (data_codes ^ set(codes)))

    pats = {e["code"]: re.compile(e["pattern"]) for e in entries}
    normed = [norm(r["text"]) for r in rows]
    miss = collections.defaultdict(list)
    extra = collections.defaultdict(list)
    for r, t in zip(rows, normed):
        hits = [c for c, p in pats.items() if p.search(t)]
        if r["label"] not in hits:
            miss[r["label"]].append((r, t))
        for c in hits:
            if c != r["label"]:
                extra[c].append((r, t))

    n_total = len(rows)
    n_ok = sum(1 for r, t in zip(rows, normed)
               if [c for c, p in pats.items() if p.search(t)] == [r["label"]])
    print(f"questions matched by exactly their own signature: {n_ok}/{n_total}")
    for c in sorted(miss):
        n_c = sum(1 for r in rows if r["label"] == c)
        print(f"\n[MISS] {c}: {len(miss[c])}/{n_c} questions not matched by its own signature")
        for r, t in miss[c][:3]:
            print("    ", r["source"], "|", t[:230])
        ok = False
    for c in sorted(extra):
        by = collections.Counter(r["label"] for r, t in extra[c])
        print(f"\n[EXTRA] signature of {c} also matches {len(extra[c])} questions of: {dict(by)}")
        for r, t in extra[c][:2]:
            print("    ", r["label"], "|", t[:200])
        ok = False
    print("\nRESULT:", "all consistent" if ok else "problems found")
    return ok


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ALL")
