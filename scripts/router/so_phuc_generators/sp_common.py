# -*- coding: utf-8 -*-
"""Thư viện dùng chung cho các hàm sinh câu (mỗi câu gốc 1 file riêng).

Gồm 2 phần:
  1) TRÌNH BÀY (latex, z_string, signed_term…) — bảo đảm viết đúng dấu, vd
     "-13" chứ không phải "+-13"; hệ số 1 của i thì bỏ (viết "+i" thay "+1i");
     phân số viết 5/2, căn viết đúng dạng √2 (không phải số thập phân).
  2) SINH SỐ theo 3 loại: số nguyên, số hữu tỉ, số vô tỉ — kèm cơ chế lọc điều
     kiện (cond) và khử trùng lặp để mỗi câu tự khai báo điều kiện đầu vào.
"""
import hashlib
import random
import sympy as sp


# ============================ TRÌNH BÀY ====================================
def latex(expr):
    expr = sp.sympify(expr)
    s = sp.latex(sp.radsimp(sp.sqrtdenest(expr)) if expr.has(sp.sqrt) else expr)
    return s.replace(r"\frac", r"\dfrac")


def latex_sq(expr):
    return f"\\left({latex(expr)}\\right)"


def _is_compound(expr):
    """True nếu expr là tổng nhiều hạng tử (vd 2-4√11) → cần bọc ngoặc khi ghép."""
    return isinstance(expr, sp.Add)


def signed_term(coef, symbol="i", show_one=None):
    """Trả về ' +ki ' hoặc ' -ki ' viết ĐÚNG DẤU và gọn:
    coef=1 → '+i', coef=-1 → '-i', coef=0 → '', coef=-13 → '-13i' (không '+-13i').
    Nếu symbol rỗng (số thực trần, không phải hệ số của i/biến), LUÔN hiện số
    (show_one mặc định True khi symbol=='') vì '+' một mình không có nghĩa gì."""
    if coef == 0:
        return ""
    if show_one is None:
        show_one = (symbol == "")
    if coef < 0:
        sign, mag = "-", sp.expand_mul(-coef)
    else:
        sign, mag = "+", sp.expand_mul(coef)
    # expand_mul tránh trường hợp mag = Mul(-1, Add(...)) khiến sp.latex tự in
    # thêm dấu "-" ở đầu chuỗi (vd mag dương nhưng latex(mag) = "-...") gây "--".
    if mag == 1 and not show_one:
        mag_str = ""
    elif _is_compound(mag):
        mag_str = f"\\left({latex(mag)}\\right)"
    else:
        mag_str = latex(mag)
    return f"{sign}{mag_str}{symbol}"


def num_bare(coef):
    """Số hạng đứng đầu (phần thực): bọc ngoặc nếu là tổng nhiều hạng tử."""
    if _is_compound(coef):
        return f"\\left({latex(coef)}\\right)"
    return latex(coef)


def z_string(a, b):
    """Viết số phức a+bi đúng dấu, gọn: z_string(3,-2) -> '3-2i'."""
    return f"{num_bare(a)}{signed_term(b)}"


def join_plus(s):
    """Ghép '+ s' vào 1 chuỗi latex, tránh '+-9' khi s tự mang dấu âm."""
    s = str(s)
    return s if s.startswith("-") else f"+{s}"


def diem(x, y):
    """Toạ độ điểm (x;y)."""
    return f"({latex(x)};{latex(y)})"


def neq(x, y):
    """True nếu x ≠ y (so sánh chắc chắn kể cả biểu thức căn/hữu tỉ)."""
    return sp.simplify(x - y) != 0


def bump_distinct(vals):
    """Giữ NGUYÊN vals[0] (đáp án đúng), cộng thêm 1 vào các phương án nhiễu cho
    tới khi cả 4 giá trị khác nhau từng đôi. Trả về danh sách đã tách biệt."""
    vals = list(vals)
    for i in range(1, len(vals)):
        while any(sp.simplify(vals[i] - vals[j]) == 0 for j in range(i)):
            vals[i] = vals[i] + 1
    return vals


def _pos_key(*vals):
    """Số nguyên ổn định (không phụ thuộc lần chạy) suy từ tham số — dùng để đặt
    vị trí đáp án đúng khác nhau giữa các câu."""
    s = "|".join(str(v) for v in vals)
    return int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16)


def mc_num(correct, raw_distractors, key_vals, fmt=None):
    """MCQ cho đáp án là GIÁ TRỊ SỐ: khử trùng phương án nhiễu (giữ nguyên đáp án),
    render mỗi giá trị, rồi đặt đáp án vào vị trí thay đổi. Trả về (khối, đáp_án)."""
    if fmt is None:
        fmt = lambda v: f"${latex(v)}$."
    vals = bump_distinct([correct, *raw_distractors])
    strs = [fmt(v) for v in vals]
    return assemble(strs[0], strs[1:], key_vals)


def assemble(correct, distractors, key_vals):
    """Ghép 4 phương án đã render (chuỗi), đặt ĐÁP ÁN ĐÚNG vào vị trí thay đổi
    theo key_vals (để không phải lúc nào cũng cùng 1 chữ cái). Trả về
    (khối_ABCD, dòng_đáp_án). Báo lỗi nếu 4 phương án trùng nhau."""
    if len(set([correct, *distractors])) != 4:
        raise ValueError(f"Phương án trùng: {[correct, *distractors]}")
    pos = _pos_key(*key_vals) % 4
    ordered = list(distractors)
    ordered.insert(pos, correct)
    letters = "ABCD"
    block = "\n".join(f"{letters[i]}. {ordered[i]}" for i in range(4))
    return block, f"{letters[pos]}. {correct}"


def assert_distinct(*vals):
    """Bảo đảm 4 phương án A/B/C/D không trùng nhau (bẫy lỗi trùng đáp án)."""
    seen = []
    for v in vals:
        for s in seen:
            if sp.simplify(v - s) == 0:
                raise ValueError(f"Trùng phương án: {v} == {s}")
        seen.append(v)


# ============================ SINH SỐ ======================================
_RADICANDS = [2, 3, 5, 6, 7, 10, 11]


def rand_val(loai_so, rng, lo=-9, hi=9):
    """Một số ngẫu nhiên (khác 0) theo loại: 'Số nguyên' | 'Số hữu tỉ' | 'Số vô tỉ'.
    - Số hữu tỉ: p/q rút gọn, KHÔNG nguyên (q ∈ {2,3,4,5}).
    - Số vô tỉ: k·√r (k nguyên khác 0, r ∈ {2,3,5,6,7,10,11})."""
    if loai_so == "Số nguyên":
        return sp.Integer(rng.choice([x for x in range(lo, hi + 1) if x != 0]))
    if loai_so == "Số hữu tỉ":
        q = rng.choice([2, 3, 4, 5])
        p = rng.choice([x for x in range(lo * q, hi * q + 1) if x % q != 0])
        return sp.Rational(p, q)
    if loai_so == "Số vô tỉ":
        k = rng.choice([x for x in range(-4, 5) if x != 0])
        return k * sp.sqrt(rng.choice(_RADICANDS))
    raise ValueError(f"loai_so không hợp lệ: {loai_so}")


def gen_pair(loai_so, rng, lo=-9, hi=9):
    """Một cặp (a,b) theo loại số, dùng cho số phức z=a+bi.
    Với số vô tỉ: một hoặc cả hai phần là số vô tỉ (phần còn lại có thể là số nguyên)."""
    if loai_so != "Số vô tỉ":
        return rand_val(loai_so, rng, lo, hi), rand_val(loai_so, rng, lo, hi)
    which = rng.choice(["a", "b", "both"])
    if which == "a":
        return rand_val("Số vô tỉ", rng), rand_val("Số nguyên", rng, lo, hi)
    if which == "b":
        return rand_val("Số nguyên", rng, lo, hi), rand_val("Số vô tỉ", rng)
    return rand_val("Số vô tỉ", rng), rand_val("Số vô tỉ", rng)


def gen_pairs(loai_so, n, seed, cond=None, max_tries=20000, lo=-9, hi=9):
    """Sinh n cặp (a,b) PHÂN BIỆT theo loại số, mỗi cặp thoả cond(a,b) (nếu có).
    cond: hàm (a,b)->bool. Báo lỗi nếu không đủ n cặp sau max_tries."""
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < max_tries:
        tries += 1
        a, b = gen_pair(loai_so, rng, lo, hi)
        if cond is not None and not cond(a, b):
            continue
        key = (str(a), str(b))
        if key in seen:
            continue
        seen.add(key)
        out.append((a, b))
    if len(out) < n:
        raise RuntimeError(f"gen_pairs: chỉ sinh {len(out)}/{n} cặp (loai={loai_so})")
    return out


def gen_quads(loai_so, n, seed, cond=None, max_tries=40000, lo=-9, hi=9):
    """Sinh n bộ (a,b,c,d) PHÂN BIỆT — dùng cho bài có HAI số phức z1=a+bi, z2=c+di.
    cond: hàm (a,b,c,d)->bool."""
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < max_tries:
        tries += 1
        a, b = gen_pair(loai_so, rng, lo, hi)
        c, d = gen_pair(loai_so, rng, lo, hi)
        if cond is not None and not cond(a, b, c, d):
            continue
        key = (str(a), str(b), str(c), str(d))
        if key in seen:
            continue
        seen.add(key)
        out.append((a, b, c, d))
    if len(out) < n:
        raise RuntimeError(f"gen_quads: chỉ sinh {len(out)}/{n} bộ (loai={loai_so})")
    return out


def gen_tuples(loai_so, n, seed, k, cond=None, max_tries=80000, lo=-9, hi=9):
    """Sinh n bộ k giá trị PHÂN BIỆT theo loại số, thoả cond(*t) (nếu có)."""
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < max_tries:
        tries += 1
        t = tuple(rand_val(loai_so, rng, lo, hi) for _ in range(k))
        if cond is not None and not cond(*t):
            continue
        key = tuple(str(x) for x in t)
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    if len(out) < n:
        raise RuntimeError(f"gen_tuples: chỉ sinh {len(out)}/{n} bộ (loai={loai_so})")
    return out


def gen_vals(loai_so, n, seed, cond=None, lo=-9, hi=9, max_tries=20000):
    """Sinh n GIÁ TRỊ đơn phân biệt theo loại số, thoả cond(v) (nếu có)."""
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < max_tries:
        tries += 1
        v = rand_val(loai_so, rng, lo, hi)
        if cond is not None and not cond(v):
            continue
        if str(v) in seen:
            continue
        seen.add(str(v))
        out.append(v)
    if len(out) < n:
        raise RuntimeError(f"gen_vals: chỉ sinh {len(out)}/{n} giá trị (loai={loai_so})")
    return out
