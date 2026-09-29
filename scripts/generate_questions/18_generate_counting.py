# -*- coding: utf-8 -*-
"""
Nhom "dem so nguyen" (D25, D41, D74, D92). Sinh de bai theo dung phuong
phap cua loi giai goc (bien doi ve dieu kien tren tham so/bien). Kiem tra
DOC LAP bang brute-force: liet ke truc tiep tung gia tri nguyen trong mot
khoang an toan va DEM lai so gia tri thoa man dinh nghia goc (khong dung
cong thuc dong dang da suy luan luc sinh), roi so sanh voi so luong da
cong bo trong de bai.
"""
import json
import sys
from importlib import import_module

sys.path.insert(0, "scripts/generate_questions")
utils = import_module("10_common_utils")
latex = utils.latex
render_mc = utils.render_mc
bump_until_distinct = utils.bump_until_distinct

import sympy as sp

ROWS = []


def add_row(ma_dang, ten_dang, id_goc, de_bai, dap_an, loi_giai, params):
    ROWS.append({
        "id_goc": id_goc, "ma_dang": ma_dang, "ten_dang": ten_dang,
        "nguon": "Nhân bản", "loai_bien_the": "chuan",
        "de_bai": de_bai, "dap_an": dap_an, "loi_giai": loi_giai, "params": params,
    })


def try_add(ma_dang, ten_dang, id_goc, gen_fn, verify_fn, args_list):
    fails = []
    for args in args_list:
        try:
            de_bai, dap_an, loi_giai, params = gen_fn(*args)
        except AssertionError:
            continue
        if verify_fn(params):
            add_row(ma_dang, ten_dang, id_goc, de_bai, dap_an, loi_giai, params)
        else:
            fails.append((ma_dang, params))
    return fails


# ===================== D25: log(mx)=2log(x+p) co nghiem duy nhat ===========
def gen_D25(p, M):
    p, M = sp.Integer(p), sp.Integer(M)
    threshold = 4 * p
    count = M + (M - threshold + 1) if threshold <= M else 2 * M + 1  # so nguyen m<0 (M cai) + {threshold} neu <=M
    # so nguyen trong [-M;M]: am (M gia tri: -M..-1) luon nhan, cong them 1 neu threshold in [-M,M]
    count = M + (1 if -M <= threshold <= M else 0)
    vals = bump_until_distinct([sp.Integer(count), 2 * M + 1, M, M + 2])
    correct, wrong1, wrong2, wrong3 = (str(v) for v in vals)
    de_bai = (
        f"Hỏi có bao nhiêu giá trị $m$ nguyên trong đoạn $[-{M};{M}]$ để phương trình "
        f"$\\log(mx)=2\\log(x+{p})$ có nghiệm duy nhất?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện $x>-{p}, x\\ne0$. $\\log(mx)=2\\log(x+{p})\\Leftrightarrow mx=(x+{p})^2 "
        f"\\Leftrightarrow m=\\dfrac{{(x+{p})^2}}{{x}}=f(x)$.\n"
        f"$f'(x)=\\dfrac{{x^2-{p**2}}}{{x^2}}=0\\Leftrightarrow x=\\pm{p}$ (chỉ nhận $x={p}$ do điều kiện). "
        f"$f({p})={threshold}$, $f\\to-\\infty$ khi $x\\to-{p}^+$, $f\\to+\\infty$ khi $x\\to0^-$ hoặc $x\\to+\\infty$.\n"
        f"Phương trình có nghiệm duy nhất khi $m={threshold}$ hoặc $m<0$. Với $m\\in[-{M};{M}]\\cap\\mathbb{{Z}}$, "
        f"có ${M}$ giá trị âm" + (f" cộng thêm $m={threshold}$" if -M <= threshold <= M else "") +
        f", tổng cộng ${count}$ giá trị."
    )
    return de_bai, dap_an, loi_giai, dict(p=str(p), M=str(M))


def verify_D25(params):
    p, M = sp.sympify(params["p"]), sp.sympify(params["M"])
    xv = sp.Symbol("xv", real=True)
    count = 0
    for m in range(-int(M), int(M) + 1):
        sols = sp.solve(sp.Eq(m * xv, (xv + p) ** 2), xv)
        valid = [s for s in sols if s.is_real and s > -p and s != 0]
        if len(valid) == 1:
            count += 1
    de_bai_correct = int(str(params.get("_expected_count", count)))
    return True  # so sanh thuc hien o main() vi can gia tri count da sinh


def verify_D25_full(params, expected_count):
    p, M = sp.sympify(params["p"]), sp.sympify(params["M"])
    xv = sp.Symbol("xv", real=True)
    count = 0
    for m in range(-int(M), int(M) + 1):
        sols = sp.solve(sp.Eq(m * xv, (xv + p) ** 2), xv)
        valid = [s for s in sols if s.is_real and s > -p and s != 0]
        if len(valid) == 1:
            count += 1
    return count == expected_count


# ===================== D41: log_b(b x+b)+x = 2y+b^(2y), dem cap (x,y) =====
def gen_D41(b, N):
    b, N = sp.Integer(b), sp.Integer(N)
    ub = sp.log(N + 1, b) / 2
    y_max = int(sp.floor(ub))
    count = y_max + 1  # y=0..y_max
    correct = str(count)
    wrong1 = str(N)
    wrong2 = str(y_max)
    wrong3 = str(count + 1)
    de_bai = (
        f"Có bao nhiêu cặp số nguyên $(x;y)$ thỏa mãn $0\\le x\\le {N}$ và "
        f"$\\log_{{{b}}}({b}x+{b})+x=2y+{b**2}^y$?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"$\\log_{{{b}}}({b}x+{b})+x=2y+{b}^{{2y}} \\Leftrightarrow 1+\\log_{{{b}}}(x+1)+x=2y+{b}^{{2y}}$. "
        f"Đặt $t=\\log_{{{b}}}(x+1)$ suy ra $t+{b}^t=2y+{b}^{{2y}}$. Xét $f(h)=h+{b}^h$ đồng biến trên $\\mathbb{{R}}$ "
        f"nên $t=2y \\Leftrightarrow x+1={b}^{{2y}}$. Do $0\\le x\\le{N}$ nên $0\\le y\\le\\log_{{{b}}}({N+1})/2\\approx{float(ub):.2f}$, "
        f"suy ra $y\\in\\{{0,1,\\ldots,{y_max}\\}}$, có ${count}$ cặp."
    )
    return de_bai, dap_an, loi_giai, dict(b=str(b), N=str(N))


def verify_D41_full(params, expected_count):
    b, N = sp.sympify(params["b"]), sp.sympify(params["N"])
    count = 0
    for xv in range(0, int(N) + 1):
        rhs_needed = sp.log(xv + 1, b) + 1 + xv  # gia tri f(t) can dat duoc = 2y + b^2y voi t=log_b(x+1)
    # brute force truc tiep tren x: voi moi x nguyen trong [0,N], kiem tra co ton tai y nguyen thoa dang thuc khong
    count = 0
    for xv in range(0, int(N) + 1):
        lhs = sp.log(b * xv + b, b) + xv
        # tim y nguyen sao cho 2y + b^(2y) = lhs, do ham dong bien nen y duy nhat neu co
        found = False
        for y_try in range(-5, 30):
            val = 2 * y_try + b ** (2 * y_try)
            if abs(float(val - lhs)) < 1e-6:
                found = True
                break
        if found:
            count += 1
    return count == expected_count


# ===================== D74: log_{b^2} x^2 - log_b(qx-1) = -log_b m, dem m ==
def gen_D74(b, q):
    b, q = sp.Integer(b), sp.Integer(q)
    count = q - 1
    correct = str(count)
    wrong1 = str(q)
    wrong2 = "Vô số"
    wrong3 = str(count + 2)
    de_bai = (
        f"Cho phương trình $\\log_{{{b**2}}}x^2-\\log_{{{b}}}({q}x-1)=-\\log_{{{b}}}m$ ($m$ là tham số thực). "
        f"Có tất cả bao nhiêu giá trị nguyên của $m$ để phương trình đã cho có nghiệm?\n\n"
    )
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện $x>\\dfrac1{{{q}}}, m>0$. $\\log_{{{b}}}x+\\log_{{{b}}}m=\\log_{{{b}}}({q}x-1)\\Leftrightarrow mx={q}x-1"
        f"\\Leftrightarrow x({q}-m)=1$. Với $m\\ne{q}$: $x=\\dfrac1{{{q}-m}}>\\dfrac1{{{q}}}\\Leftrightarrow 0<m<{q}$. "
        f"Vậy $m\\in\\{{1,\\ldots,{q-1}\\}}$, có ${count}$ giá trị."
    )
    return de_bai, dap_an, loi_giai, dict(b=str(b), q=str(q))


def verify_D74_full(params, expected_count):
    b, q = sp.sympify(params["b"]), sp.sympify(params["q"])
    xv = sp.Symbol("xv", real=True)
    count = 0
    for m in range(-30, 30):
        if m == q:
            continue
        sols = sp.solve(sp.Eq(xv * (q - m), 1), xv)
        valid = [s for s in sols if s.is_real and s > sp.Rational(1, q) and m > 0]
        if valid:
            count += 1
    return count == expected_count


# ===================== D92: dem so nguyen thuoc TXD log[(N-x)(x+M)] ========
def gen_D92(N, M):
    N, M = sp.Integer(N), sp.Integer(M)
    count = N + M - 1
    correct = str(count)
    wrong1 = str(count + 1)
    wrong2 = str(count - 1)
    wrong3 = "Vô số"
    de_bai = f"Có bao nhiêu số nguyên thuộc tập xác định của hàm số $y=\\log[({N}-x)(x+{M})]$?\n\n"
    lines, dap_an = render_mc([correct, wrong1, wrong2, wrong3], 0)
    de_bai += "\n".join(lines)
    loi_giai = (
        f"Điều kiện $({N}-x)(x+{M})>0\\Leftrightarrow -{M}<x<{N}\\Rightarrow \\mathscr{{D}}=(-{M};{N})$. "
        f"Vậy có ${count}$ số nguyên thuộc tập xác định."
    )
    return de_bai, dap_an, loi_giai, dict(N=str(N), M=str(M))


def verify_D92_full(params, expected_count):
    N, M = sp.sympify(params["N"]), sp.sympify(params["M"])
    count = sum(1 for xv in range(-int(M) - 5, int(N) + 5) if (N - xv) * (xv + M) > 0)
    return count == expected_count


def main():
    fails = []
    for p, M in [(1, 2017), (2, 100), (1, 50), (3, 200), (1, 30), (2, 500)]:
        de_bai, dap_an, loi_giai, params = gen_D25(p, M)
        expected = int(dap_an.split("$")[1])
        if verify_D25_full(params, expected):
            add_row("D25", "Tìm số giá trị nguyên tham số để phương trình lôgarit có nghiệm duy nhất",
                     "p042_q45", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D25", params))

    for b, N in [(3, 2020), (2, 100), (3, 500), (2, 50), (5, 1000), (2, 200)]:
        de_bai, dap_an, loi_giai, params = gen_D41(b, N)
        expected = int(dap_an.split("$")[1])
        if verify_D41_full(params, expected):
            add_row("D41", "Đếm số cặp nguyên thỏa phương trình mũ-lôgarit bằng hàm đặc trưng đơn điệu",
                     "p090_q47", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D41", params))

    for b, q in [(3, 6), (2, 5), (3, 8), (5, 10), (2, 7), (3, 4)]:
        de_bai, dap_an, loi_giai, params = gen_D74(b, q)
        expected = int(dap_an.split("$")[1])
        if verify_D74_full(params, expected):
            add_row("D74", "Đếm giá trị nguyên tham số để phương trình lôgarit cùng cơ số có nghiệm",
                     "p179_q37", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D74", params))

    for N, M in [(6, 2), (10, 3), (8, 5), (15, 4), (6, 6), (20, 2)]:
        de_bai, dap_an, loi_giai, params = gen_D92(N, M)
        expected = int(dap_an.split("$")[1])
        if verify_D92_full(params, expected):
            add_row("D92", "Đếm số nguyên thuộc tập xác định của hàm số lôgarit chứa tích hai nhị thức",
                     "p240_q31", de_bai, dap_an, loi_giai, params)
        else:
            fails.append(("D92", params))

    with open("data/questions/mu_logarit_extraction/bien_the/batch_counting.json", "w", encoding="utf-8") as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=2)

    with open("scripts/generate_questions/.tmp_batchD_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Tong so hang sinh: {len(ROWS)}\n")
        f.write(f"That bai verify: {len(fails)}\n")
        for ma_dang, params in fails:
            f.write(f"  {ma_dang}: {params}\n")
        counts = {}
        for r in ROWS:
            counts[r['ma_dang']] = counts.get(r['ma_dang'], 0) + 1
        f.write("\nSo bien the theo dang:\n")
        for k, v in sorted(counts.items()):
            f.write(f"  {k}: {v}\n")


if __name__ == "__main__":
    main()
