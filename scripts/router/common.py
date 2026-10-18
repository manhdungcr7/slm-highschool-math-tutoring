# -*- coding: utf-8 -*-
"""Load the question sets of both topics and normalise a question so that a signature can be matched on it."""
import csv
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ML_DIR = os.path.join(REPO, "data", "questions", "mu_logarit_extraction")
SP_FILE = os.path.join(REPO, "so_phuc", "data", "questions", "So_phuc_day_du.csv")


# Types removed from the router dataset because another type already covers the same problem.
# The data files are not touched, the questions are only left out here.
DROPPED = {
    "ML_D59": "Cùng một bài toán với ML_D20 (log_{ⁿ√a} a^m); ML_D20 có cả các câu với m = 1, trùng hẳn về toán.",
}


def load_questions(keep_dropped=False):
    """Return (old_names, rows). A row has: label (SP_Dxx or ML_Dxx), topic, source, text. Dropped types are left out."""
    old_names = {}
    for r in csv.DictReader(open(os.path.join(ML_DIR, "Mu_Logarit_107_cau_phan_dang.csv"), encoding="utf-8-sig")):
        old_names["ML_" + r["Ma dang"]] = r["Ten dang"]
    rows = []
    path = os.path.join(ML_DIR, "bien_the", "Mu_Logarit_bien_the_full.csv")
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        rows.append(dict(label="ML_" + r["Mã dạng"], topic="ML", source=r["Nguồn"], text=r["Đề bài"]))
    for r in csv.DictReader(open(SP_FILE, encoding="utf-8-sig")):
        label = "SP_" + r["Mã dạng"]
        old_names[label] = r["Tên dạng"]
        rows.append(dict(label=label, topic="SP", source=r["Nguồn"], text=r["Đề bài"]))
    return old_names, [r for r in rows if keep_dropped or r["label"] not in DROPPED]


def stem(text):
    """The question without its four options."""
    m = re.search(r"\n\s*A[\.\)]", text)
    return text[: m.start()] if m else text


def options(text):
    """The text of the four options, in order, as written."""
    out = {}
    for m in re.finditer(r"(?m)^\s*([ABCD])[\.\)]\s*(.*)$", text):
        out.setdefault(m.group(1), m.group(2).strip())
    return out


def norm(text):
    """Stem without whitespace and dollar signs, with the spellings that vary between questions unified."""
    s = stem(text)
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    s = re.sub(r"\\left|\\right", "", s)
    s = s.replace("\\bar{", "\\overline{")
    s = s.replace("$", "")
    s = re.sub(r"\s+", "", s)
    s = s.replace("Mô-đun", "Môđun").replace("mô-đun", "môđun")
    s = s.replace("thoả", "thỏa").replace("tuỳ", "tùy")
    s = re.sub(r"\^\{(\d+)\}", r"^\1", s)             # x^{2} -> x^2
    s = re.sub(r"_\{([^{}]*)\}", r"_\1", s)          # \log_{4} -> \log_4, z_{1} -> z_1, \log_{a^2} -> \log_a^2
    return s


_PAIR = re.compile(r"\$(z_1|z)\s*=\s*([^$]+?)\$\s*(?:và|,)\s*\$?(z_2|w)\s*=\s*([^$]+?)\$")


def has_identical_pair(text):
    """True when the question gives two complex numbers that are exactly the same (z1 = z2): legal but a poor question."""
    m = _PAIR.search(text)
    return bool(m) and re.sub(r"\s+", "", m.group(2)) == re.sub(r"\s+", "", m.group(4))
