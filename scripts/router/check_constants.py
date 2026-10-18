# -*- coding: utf-8 -*-
"""For the types whose name states a concrete number, show how that number varies over the questions of the type."""
import collections
import re

from common import load_questions, norm

old, rows = load_questions()


def by(label):
    return [norm(r["text"]) for r in rows if r["label"] == label]


def show(label, pattern, group_names=None, top=6):
    c = collections.Counter()
    miss = 0
    for t in by(label):
        m = re.search(pattern, t)
        if not m:
            miss += 1
            continue
        c[m.groups() if m.groups() else m.group(0)] += 1
    print(f"{label}: {sum(c.values())} matched, {miss} not matched, {len(c)} distinct -> {c.most_common(top)}")


# constants in names
show("ML_D93", r"(\(\d+\^b-\d+\)\(a\\cdot\d+\^b-\d+\)<0)")
show("ML_D88", r"(\[\\log_\d+\(x\^2\+\d+\)-\\log_\d+\(x\+\d+\)\]\(\d+-\d+\^\{x-\d+\}\)\\ge0)")
show("ML_D79", r"(\\log_\d+\(x\^2\+y\)\\ge\\log_\d+\(x\+y\))")
show("ML_D79", r"(không quá \d+|khôngquá\d+)")
show("ML_D56", r"(\\log_\d+\\frac\{x\^2-\d+\}\{\d+\}<\\log_\d+\\frac\{x\^2-\d+\}\{\d+\})")
show("ML_D75", r"(\\sqrt\{\(?\d+\)?\^x-m\})")
show("ML_D75", r"(\(\d*\\log_\d+\^2x[+-]\d*\\log_\d+x[+-]\d+\))")
show("ML_D94", r"(a\^\{\d+x-\\log_\d+\(?a\^2\)?\}\\le\d+\^\{\d+-y\^2\})")
show("ML_D94", r"(P=x\^2\+y\^2[^b]*)bằng")
show("ML_D68", r"(\\log_\{[^}]*\}\([^$]*\))")
show("ML_D65", r"(=\d*xy[+-]\d*x[+-]\d*y-\d+)")
show("ML_D65", r"(\\log_\d+\\frac\{[^}]*\}\{[^}]*\})")
show("ML_D22", r"(\\log_ab=[^.]*)\.")
show("ML_D41", r"(\\log_\d+\(\d+x\+\d+\)\+x=\d*y\+\d+\^y)")
show("ML_D35", r"(\\log_\d+\(\d+-\d+\^x\)=\d+-x)")
show("ML_D69", r"(\d+\^x\+m=\\log_\d+\(x-m\))")
show("ML_D45", r"(\d+\^x[+-]\d+\\cdot\d+\^x[+-]\d+>0)")
show("ML_D84", r"(\d+\^\{\d+x\^2\+xy\}=\(\d+\+xy\)\d+\^\{\d+x\})")
show("ML_D28", r"(\\log_\d+x\.\\log_\d+x\.\\log_\d+x\.\\log_\d+x=)")
show("ML_D25", r"(\\log\(mx\)=\d+\\log\(x\+\d+\))")
show("ML_D55", r"(\\ln\^2x[^=]*=0)")
show("ML_D63", r"(\\log_\d+\^2x-m\\log_\d+x[^=]*=0)")
show("ML_D08", r"(Đặta=\\log_.*?,\\?b=\\log_.*?\.)")
show("ML_D17", r"(\\log\^2_\\frac\{a\}\{b\}\([^)]*\)|\\log\^2_\\frac\{a\}\{b\}a)")
show("ML_D46", r"(a\^x=b\^y=.*?\.)Giá")
show("SP_D54", r"(\|z_1\|=\|z_2\|=\d*\|z_3\|=.*?và)")
show("SP_D54", r"(\(z_1\+z_2\)z_3=.*?\\frac\{\d+\}\{\d+\}z_1z_2|\(z_1\+z_2\)z_3=-?\d*z_1z_2)")
show("SP_D51", r"(\|z_1-z_2\|=[^,]*)")
show("SP_D52", r"(\|z\^2[^|]*\|=[^|]*\|z\|)")
show("SP_D37", r"(\|z\|=\\frac\{[^}]*\}\{z\})")
show("SP_D38", r"(\|z\|\(z[^)]*\)[+-][^=]*=)")
