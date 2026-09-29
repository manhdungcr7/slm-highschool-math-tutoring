# -*- coding: utf-8 -*-
"""Generate and independently verify numerical variants for D84."""
import json
import mpmath as mp
import re
import sys
from pathlib import Path
from importlib import import_module

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts/generate_questions"))
utils = import_module("10_common_utils")
render_mc = utils.render_mc

SOURCE_ID = "p216_q45"
TYPE_NAME = "Đếm số nguyên một biến sao cho tồn tại biến kia thỏa phương trình mũ bằng xét hàm đơn điệu"


def gen_D84(U):
    U = int(U)
    assert 3 <= U <= 7 and U != 4
    C = 3 * U
    # h(y)=y-log_3(1+y/3) is increasing. For 3<=U<=7,
    # h(3U)<3U-1<h(3U+1), so positive solutions are y=1,...,3U.
    positive_count = 3 * U
    count = positive_count + 2  # y=-1,-2 work; y=0 does not.
    choices = [str(count), str(count + 1), str(count - 1), str(count + 2)]
    choice_lines, answer = render_mc(choices, 0)
    question = (
        f"Có bao nhiêu số nguyên $y$ tồn tại sao cho "
        f"$x\\in\\left(\\dfrac{{1}}{{3}};{U}\\right)$ thỏa mãn "
        f"$27^{{3x^2+xy}}=(1+xy)27^{{{C}x}}$?\n\n" + "\n".join(choice_lines)
    )
    solution = (
        f"Đặt $g_y(x)=3x-{C}-\\dfrac{{\\log_{{27}}(1+xy)}}x+y$. Với $y\\ge1$, "
        "phương trình tương đương $g_y(x)=0$. Ta có "
        "$g_y'(x)=3+\\dfrac{\\ln(1+xy)}{x^2\\ln27}-"
        "\\dfrac{y}{x(1+xy)\\ln27}>3-\\dfrac1{x^2\\ln27}"
        ">=3-\\dfrac3{\\ln3}>0$, nên $g_y$ đồng biến trên "
        f"$[1/3;{U}]$. Tại $x={U}$, $g_y(U)=y-"
        f"\\dfrac{{\\log_{{27}}(1+{U}y)}}{{{U}}}>0$, vì "
        "$\\ln(1+u)<u$ và $\\ln27>1$. Do đó phương trình có nghiệm "
        f"trong khoảng mở khi và chỉ khi $g_y(1/3)<0$, tức là "
        f"$h(y)=y-\\log_3(1+y/3)<{C-1}$. Hàm $h$ đồng biến với $y\\ge1$ vì $h'(y)=1-1/((y+3)\\ln3)>0$. "
        f"Với $U\\in\\{{3,5,6,7\\}}$, ta có $h(3U)<3U-1$ và "
        f"$h(3U+1)>3U-1$; vì vậy các giá trị nguyên dương phù hợp là "
        f"$y=1,\\ldots,{3*U}$, gồm ${positive_count}$ giá trị.\n\n"
        "Nếu $y\\le-3$ thì $x>1/3$ kéo theo $1+xy<0$, không thể thỏa mãn. "
        "Với $y=0$, phương trình tương đương $3x(x-U)=0$, chỉ có $x=0$ "
        f"hoặc $x={U}$, đều không thuộc khoảng mở. Với $y=-1$ và $y=-2$, "
        "xét $F_y(x)=27^{3x^2+(y-"
        f"{C})x}}-(1+xy)$ trên $(1/3,-1/y)$. Tại $x=1/3$, $F_y(x)<0$; "
        "khi $x$ tiến đến $-1/y$ từ bên trái, $F_y(x)$ tiến đến một giá trị "
        "dương. Theo định lý giá trị trung gian, mỗi giá trị $y=-1,-2$ đều "
        f"cho một nghiệm. Tổng cộng có $3U+2={count}$ giá trị nguyên của $y$."
    )
    return question, answer, solution, {"U": U, "C": C, "count": count}


def verify_D84(params):
    """Enumerate endpoint sign conditions at high precision, independently of 3U+2."""
    mp.mp.dps = 80
    U, C, expected = (int(params[k]) for k in ("U", "C", "count"))
    if C != 3 * U or not (3 <= U <= 7 and U != 4):
        return False
    left = mp.mpf(1) / 3
    log27 = mp.log(27)

    def g(x, y):
        return 3*x - C - mp.log(1+x*y)/log27/x + y

    # The proof gives strict monotonicity in x and in the endpoint threshold h(y).
    # Check the whole finite transition region independently by high-precision signs.
    if not (g(left, 1) < 0 and g(left, C+1) > 0 and g(U, 1) > 0):
        return False
    positive_y = [y for y in range(1, C+2) if g(left, y) < 0 < g(U, y)]

    # Test y=-1,-2 using signs of the original equation after division by 27^(C*x).
    negative_y = []
    for y in (-1, -2):
        x_right = mp.mpf(-1) / y
        exponent_left = 3*left**2 + (y-C)*left
        f_left = mp.power(27, exponent_left) - (1+left*y)
        exponent_right = 3*x_right**2 + (y-C)*x_right
        f_right_limit = mp.power(27, exponent_right)
        if f_left < 0 < f_right_limit:
            negative_y.append(y)

    # For y=0 the only roots are x=0 and x=C/3=U, outside the open interval.
    zero_y_has_solution = any(left < root < U for root in (mp.mpf(0), mp.mpf(C)/3))
    return len(positive_y) + len(negative_y) + int(zero_y_has_solution) == expected


def audit_choices(rows):
    for row in rows:
        choices = re.findall(r"(?m)^([A-D])\.\s*(.+)$", row["de_bai"])
        if len(choices) != 4 or {letter for letter, _ in choices} != set("ABCD"):
            raise AssertionError("Each question must have one choice A-D")
        normalized = [re.sub(r"[\s$.,]", "", value) for _, value in choices]
        if len(set(normalized)) != 4:
            raise AssertionError("Duplicate answer choices")


def main():
    rows = []
    for U in (3, 5, 6, 7):
        question, answer, solution, params = gen_D84(U)
        if not verify_D84(params):
            raise AssertionError(f"Independent check failed: {params}")
        rows.append({
            "id_goc": SOURCE_ID,
            "ma_dang": "D84",
            "ten_dang": TYPE_NAME,
            "nguon": "Nhân bản",
            "loai_bien_the": "chuan",
            "de_bai": question,
            "dap_an": answer,
            "loi_giai": solution,
            "params": {k: str(v) for k, v in params.items()},
        })
    audit_choices(rows)
    path = REPO / "data/questions/mu_logarit_extraction/bien_the/batch_round9.json"
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated and independently verified {len(rows)} D84 variants")


if __name__ == "__main__":
    main()