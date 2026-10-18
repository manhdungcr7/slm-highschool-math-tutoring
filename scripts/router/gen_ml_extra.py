# -*- coding: utf-8 -*-
"""Extra Mũ-Logarit variants for the types whose original parameter range is used up.

The existing generators (scripts/generate_questions) and their independent verifiers are reused unchanged; only the range
of the numeric parameters is widened (larger bases, wider intervals), and every question must pass the same checks as the
original ones: four distinct options A-D, the type's own verifier, and a key that is new for the whole project.

python gen_ml_extra.py D02 D42 ...        (codes without the ML_ prefix; no argument = every type in SPECS)
Output: data/router_train/_work/ml_extra_<code>.json
"""
import importlib.util
import inspect
import json
import os
import random
import re
import sys
from fractions import Fraction

import sympy as sp

from collect_new import question_key
from common import REPO, load_questions

GEN_DIR = os.path.join(REPO, "scripts", "generate_questions")
OUT_DIR = os.path.join(REPO, "data", "router_train", "_work")
os.chdir(REPO)                                  # the generators use paths relative to the repository root
sys.path.insert(0, GEN_DIR)

_modules = {}


SOURCE_PATCHES = {
    # D84: the generator and its verifier only restrict U to 3..93 by choice; the proof inside is valid for any U >= 3
    "30_generate_round9.py": [("3 <= U <= 93", "3 <= U <= 600")],
}


def module(filename):
    if filename not in _modules:
        path = os.path.join(GEN_DIR, filename)
        if filename in SOURCE_PATCHES:
            text = open(path, encoding="utf-8").read()
            for a, b in SOURCE_PATCHES[filename]:
                assert a in text, a
                text = text.replace(a, b)
            patched = os.path.join(OUT_DIR, "_patched", "x", "y", filename)
            os.makedirs(os.path.dirname(patched), exist_ok=True)
            open(patched, "w", encoding="utf-8").write(text)
            path = patched
        spec = importlib.util.spec_from_file_location("gen_" + filename[:2] + filename[3:6], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _modules[filename] = mod
    return _modules[filename]


def ri(r, lo, hi):
    return r.randint(lo, hi)


def rational_thresholds():
    ks = [sp.Rational(n) for n in range(-30, 31)]
    for d in (2, 3, 4, 5, 6, 7, 8, 10):
        ks += [sp.Rational(n, d) for n in range(-12 * d, 12 * d + 1) if n % d]
    return ks


# code -> (module file, generator name, verifier name, sampler(r) -> args, source id)
SPECS = {
    "D02": ("17_generate_basic_eq.py", "gen_D02", "verify_D02", lambda r: (ri(r, 93, 600),), "p006_q13"),
    "D42": ("17_generate_basic_eq.py", "gen_D42", "verify_D42", lambda r: (ri(r, 93, 600),), "p093_q05"),
    "D80": ("17_generate_basic_eq.py", "gen_D80", "verify_D80", lambda r: (ri(r, 93, 600),), "p206_q04"),
    "D07": ("17_generate_basic_eq.py", "gen_D07", "verify_D07", lambda r: (ri(r, 1, 30), ri(r, 2, 60)), "p007_q18"),
    "D28": ("17_generate_basic_eq.py", "gen_D28", "verify_D28", lambda r: (ri(r, 2, 30), ri(r, 1, 60) ** 4, 24), "p053_q27"),
    "D34": ("17_generate_basic_eq.py", "gen_D34", "verify_D34", lambda r: (ri(r, 2, 60), ri(r, -40, 40)), "p069_q28"),
    "D73": ("17_generate_basic_eq.py", "gen_D73", "verify_D73", lambda r: (ri(r, 2, 60), ri(r, -40, 40)), "p176_q26"),
    "D85": ("17_generate_basic_eq.py", "gen_D85", "verify_D85", lambda r: (ri(r, 2, 60), ri(r, 1, 80)), "p220_q04"),
    "D86": ("17_generate_basic_eq.py", "gen_D86", "verify_D86", lambda r: (ri(r, 2, 60), ri(r, 2, 120)), "p223_q22"),
    "D82": ("17_generate_basic_eq.py", "lambda_82", "verify_D48_D82", lambda r: (ri(r, 2, 40), ri(r, 3, 400)), "p210_q26"),
    "D43": ("17_generate_basic_eq.py", "gen_D43", "verify_D43", lambda r: (r.choice(rational_thresholds()),), "p095_q16"),
    "D37": ("16_generate_identities_B.py", "gen_D37", "verify_D37", lambda r: (ri(r, 2, 30), ri(r, 2, 12)), "p081_q20"),
    "D44": ("16_generate_identities_B.py", "gen_D44", "verify_D44", lambda r: (ri(r, 2, 30), ri(r, 2, 12)), "p098_q29"),
    "D64": ("16_generate_identities_B.py", "gen_D64", "verify_D64", lambda r: (ri(r, 2, 60), ri(r, 2, 60)), "p146_q42"),
    "D77": ("16_generate_identities_B.py", "gen_D77", "verify_D77", lambda r: (ri(r, 2, 40), ri(r, 2, 40)), "p195_q30"),
    "D36a": ("15_generate_identities_A.py", "gen_D36a", "verify_D36a", lambda r: (ri(r, 2, 800),), "p063_q18"),
    "D47": ("29_generate_round8.py", "gen_D47", "verify_D47", lambda r: _sample47(r), "p106_q50"),
    "D57": ("29_generate_round8.py", "gen_D57", "verify_D57", lambda r: (ri(r, 2, 400),), "p133_q47"),
    "D75": ("26_generate_round5.py", "gen_D75", "verify_D75_full",
            lambda r: (2, sp.Rational(200 + ri(r, 1, 800), 100)), "p186_q47"),
    "D84": ("30_generate_round9.py", "gen_D84", "verify_D84", lambda r: (ri(r, 94, 400),), "p205_q35"),
    "D05": ("23_generate_round2.py", "gen_D05", "verify_D05", lambda r: (ri(r, 2, 80), ri(r, 2, 120)), "p006_q16"),
    "D15": ("23_generate_round2.py", "gen_D15", "verify_D15", lambda r: (ri(r, 0, 3000),), "p021_q18"),
    "D16": ("23_generate_round2.py", "gen_D16", "verify_D16", lambda r: (ri(r, 4, 400), ri(r, 2, 40), ri(r, 1, 80)), "p021_q20"),
    "D35": ("23_generate_round2.py", "gen_D35", "verify_D35", lambda r: (ri(r, 2, 30), ri(r, 5, 400), ri(r, 1, 60)), "p070_q31"),
    "D40": ("23_generate_round2.py", "lambda_40", "verify_D40_full", lambda r: (ri(r, 2, 40), ri(r, -80, 80), ri(r, -80, 80)), "p088_q43"),
    "D45": ("23_generate_round2.py", "gen_D45", "verify_D45", lambda r: (ri(r, 2, 40), ri(r, 1, 150), -ri(r, 1, 150)), "p099_q31"),
    "D69": ("31_fix_and_expand.py", "gen_D69", "fast_verify_D69", lambda r: (ri(r, 2, 40), -ri(r, 5, 300), ri(r, 5, 300)), "p166_q45"),
    "D51": ("31_fix_and_expand.py", "gen_D51", "fast_verify_D51", lambda r: (ri(r, 2, 3000), ri(r, 2, 5)), "p115_q39"),
    "D67": ("31_fix_and_expand.py", "gen_D67", "fast_verify_D67", lambda r: (lambda b: (b, b, ri(r, 1, 400)))(ri(r, 4, 60)), "p161_q35"),
    "D18": ("13_generate_D18.py", "mau_D18", "verify_D18", lambda r: (ri(r, 92, 600),), "p013_q10"),
}


def _sample47(r):
    import math
    while True:
        n = r.randint(2, 60)
        m = r.randint(n + 1, int(1.5 * n))
        if math.gcd(m, n) == 1:
            return m, n


def resolve(code):
    fname, gen_name, ver_name, sampler, source = SPECS[code]
    mod = module(fname)
    if gen_name == "lambda_82":
        gen = lambda a, c: mod.gen_D48_D82(a, c, "<")                     # noqa: E731
    elif gen_name == "lambda_40":
        gen = lambda a, p, q: mod.gen_D40(a, a, p, q)                      # noqa: E731
    elif code == "D51":
        def gen(F, D):
            out = mod.r2.gen_D51(2, 2, F, D)
            if int(out[3]["dk_hi"]) > 5000:
                raise AssertionError("dk_hi too large")
            return out
    elif code == "D69":
        gen = mod.r2.gen_D69
    elif code == "D67":
        gen = lambda B, k, c: mod.fast_gen_D67(B, k, c)                    # noqa: E731
    else:
        gen = getattr(mod, gen_name)
    if code == "D18":
        verifier = module("20_verify_pilot.py").verify_D18
        verify = lambda params, answer: verifier(params, answer)[0]        # noqa: E731
    else:
        verify = getattr(mod, ver_name)
    return gen, verify, sampler, source


def n_positional(fn):
    try:
        return len([p for p in inspect.signature(fn).parameters.values()
                    if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.default is p.empty])
    except (TypeError, ValueError):
        return 1


def run_d51(want=130):
    """D51: the existing variants use make_D51(u, v, F, D) of the round-10 script; here other (F, D) pairs are used."""
    m32 = module("32_generate_round10_shortfalls.py")
    label = "ML_D51"
    _, rows = load_questions()
    taken = {question_key(label, r["text"]) for r in rows if r["label"] == label}
    out = []
    combos = [(F, D) for D in (3, 4, 5, 2) for F in (2, 4, 5, 8, 10, 16, 20, 25, 32, 40, 50, 64, 80, 100, 125, 160)
              if (10 ** D) % F == 0 and 10 ** D // F >= 14]
    for F, D in combos:
        for u in range(2, 13):
            for v in range(u + 2, 15):
                if len(out) >= want:
                    break
                try:
                    row = m32.make_D51(u, v, F, D)
                except (AssertionError, ValueError):
                    continue
                k = question_key(label, row["de_bai"])
                if k in taken:
                    continue
                taken.add(k)
                row["loai_bien_the"] = "mo_rong"
                out.append(row)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "ml_extra_D51.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"D51: {len(out)} new verified questions", flush=True)
    return out


def run(code, want=130, max_tries=6000, seed=0):
    if code == "D51":
        return run_d51(want)
    gen, verify, sampler, source = resolve(code)
    label = "ML_" + code
    _, rows = load_questions()
    taken = {question_key(label, r["text"]) for r in rows if r["label"] == label}
    rng = random.Random(f"router|{code}|{seed}")
    seen_args, out = set(), []
    two_args = n_positional(verify) >= 2
    for _ in range(max_tries):
        if len(out) >= want:
            break
        args = tuple(sampler(rng))
        key_args = tuple(str(a) for a in args)
        if key_args in seen_args:
            continue
        seen_args.add(key_args)
        try:
            q, ans, sol, params = gen(*args)
        except (AssertionError, ValueError, TypeError, ZeroDivisionError, OverflowError, KeyError):
            continue
        k = question_key(label, q)
        if k in taken:
            continue
        opts = re.findall(r"(?m)^([A-D])\.\s*(.+)$", q)
        norm = [re.sub(r"[\s$.,]", "", v) for _, v in opts]
        if len(opts) != 4 or {a for a, _ in opts} != set("ABCD") or len(set(norm)) != 4:
            continue
        try:
            if code == "D18":
                ok = verify(params, ans)
            elif two_args:
                m = re.search(r"\$\s*(-?\d+)\s*\$", ans)
                ok = verify(params, int(m.group(1))) if m else False
            else:
                ok = verify(params)
        except Exception:
            ok = False
        if not ok:
            continue
        taken.add(k)
        out.append(dict(id_goc=source, ma_dang=code, nguon="Nhân bản", loai_bien_the="mo_rong", de_bai=q, dap_an=ans,
                        loi_giai=sol, params={a: str(b) for a, b in params.items()}))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"ml_extra_{code}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"{code}: {len(out)} new verified questions", flush=True)
    return out


if __name__ == "__main__":
    codes = sys.argv[1:] or list(SPECS)
    for c in codes:
        run(c)
