# Temporary staging helper for the requested round-8 work. Run from the
# slm-highschool-math-tutoring repository with --preview or --write.
import json
import random
import math
import re
import subprocess
import sys
from pathlib import Path
from importlib import import_module

REPO = Path(__file__).resolve().parents[2]
GEN_PATH = REPO / "scripts/generate_questions/29_generate_round8.py"
sys.path.insert(0, str(REPO / "scripts/generate_questions"))
utils = import_module("10_common_utils")
latex, render_mc, bump_until_distinct = utils.latex, utils.render_mc, utils.bump_until_distinct
import sympy as sp

ROWS = []


def add_row(code, name, source, prompt, answer, solution, params):
    ROWS.append({
        "id_goc": source, "ma_dang": code, "ten_dang": name,
        "nguon": "NhÃ¢n báº£n", "loai_bien_the": "chuan",
        "de_bai": prompt, "dap_an": answer, "loi_giai": solution,
        "params": {k: str(v) for k, v in params.items()},
    })


def mc_count_prompt(question, count):
    vals = bump_until_distinct([sp.Integer(count), count + 1, count - 1, count + 2])
    opts = [str(v) for v in vals]
    lines, answer = render_mc(opts, 0)
    return question + "\n\n" + "\n".join(lines), answer


# D08: use a=log_p(C), b=log_r(C), and derive the target by change of base.
def gen_D08(p, C, r, s, i, j):
    p, C, r, s, i, j = map(sp.Integer, (p, C, r, s, i, j))
    assert min(p, C, r) > 1 and p != C and r != C and p != r
    assert s > 0 and i > 0 and j > 0
    a, b = sp.symbols("a b", positive=True)
    correct = sp.factor(a * (i * b + j) / (b * (1 + s * a)))
    vals = bump_until_distinct([correct, correct + 1, correct - 1, -correct])
    opts = [latex(v) for v in vals]
    pow_c = str(C) if i == 1 else f"{C}^{{{i}}}"
    pow_r = str(r) if j == 1 else f"{r}^{{{j}}}"
    pow_den = str(C) if s == 1 else f"{C}^{{{s}}}"
    target = f"{p}\\cdot {pow_den}"
    argument = f"{pow_c}\\cdot {pow_r}"
    sa = "a" if s == 1 else f"{s}a"
    ilogc = r"\ln C" if i == 1 else f"{i}\\ln C"
    jlogr = r"\ln r" if j == 1 else f"{j}\\ln r"
    slogc = r"\ln C" if s == 1 else f"{s}\\ln C"
    question = (
        f"Äáº·t $a=\\log_{{{p}}}{C},\\ b=\\log_{{{r}}}{C}$. HÃ£y biá»ƒu diá»…n "
        f"$\\log_{{{target}}}({argument})$ theo $a,b$.\n\n"
    )
    lines, answer = render_mc(opts, 0, prefix=f"\\log_{{{target}}}({argument})=")
    prompt = question + "\n".join(lines)
    solution = (
        f"Äá»•i cÆ¡ sá»‘ theo $\\ln C$: $\\ln p=\\dfrac{{\\ln C}}a$ vÃ  "
        f"$\\ln r=\\dfrac{{\\ln C}}b$. Do Ä‘Ã³ giÃ¡ trá»‹ cáº§n tÃ¬m báº±ng "
        f"$\\dfrac{{{ilogc}+{jlogr}}}{{\\ln p+{slogc}}}="
        f"\\dfrac{{a({i}b+{j})}}{{b(1+{sa})}}={latex(correct)}$."
    )
    return prompt, answer, solution, dict(p=p, C=C, r=r, s=s, i=i, j=j)


def verify_D08(params):
    p, C, r, s, i, j = [int(params[k]) for k in ("p", "C", "r", "s", "i", "j")]
    a, b = math.log(C, p), math.log(C, r)
    via_formula = a * (i * b + j) / (b * (1 + s * a))
    via_direct_log = math.log((C ** i) * (r ** j)) / math.log(p * (C ** s))
    return abs(via_formula - via_direct_log) < 1e-11


# D23: ln((x+1)^m) is written explicitly to avoid ambiguity in the source's
# compact notation ln(x+1)^3. Generation uses exact critical-point values;
# verification independently counts sign-changing roots by bisection.
def gen_D23(A, B, m, C):
    A, B, m, C = map(sp.Integer, (A, B, m, C))
    assert A > 0 and m > 0
    A, B, m, C = int(A), int(B), int(m), int(C)
    x = sp.symbols("x", real=True)
    f = A * x**2 + B * x + m * sp.log(x + 1) + C
    deriv_num = sp.together(sp.diff(f, x)).as_numer_denom()[0]
    critical = sorted(
        [z for z in sp.solve(deriv_num, x) if z.is_real and z > -1],
        key=lambda z: float(z),
    )
    assert len(critical) == 2
    vals = [sp.N(f.subs(x, z), 40) for z in critical]
    assert vals[0] > 0 and vals[1] < 0
    linear, constant = 2*A + B, B + m
    deriv_num = f"{2*A}x^2"
    if linear:
        deriv_num += f"{'+' if linear > 0 else '-'}{abs(linear)}x"
    if constant:
        deriv_num += f"{'+' if constant > 0 else '-'}{abs(constant)}"
    question, answer = mc_count_prompt(
        f"PhÆ°Æ¡ng trÃ¬nh ${A}x^2{B:+d}x+\\ln((x+1)^{{{m}}}){C:+d}=0$ "
        "cÃ³ bao nhiÃªu nghiá»‡m phÃ¢n biá»‡t?", 3
    )
    solution = (
        f"\u0110i\u1ec1u ki\u1ec7n $x>-1$. X\u00e9t $f(x)={A}x^2{B:+d}x+{m}\\ln(x+1){C:+d}$. "
        f"Ta c\u00f3 $f'(x)=\\dfrac{{{deriv_num}}}{{x+1}}$. D\u1ea5u c\u1ee7a \u0111\u1ea1o h\u00e0m l\u1ea7n l\u01b0\u1ee3t l\u00e0 $+,-,+$; "
        f"t\u1ea1i $x={sp.latex(critical[0])}$, f \u0111\u1ea1t c\u1ef1c \u0111\u1ea1i x\u1ea5p x\u1ec9 {float(vals[0]):.3f}>0, "
        f"c\u00f2n t\u1ea1i $x={sp.latex(critical[1])}$, f \u0111\u1ea1t c\u1ef1c ti\u1ec3u x\u1ea5p x\u1ec9 {float(vals[1]):.3f}<0. "
        "K\u1ebft h\u1ee3p $\\lim_{x\\to-1^+}f(x)=-\\infty$ v\u00e0 "
        "$\\lim_{x\\to+\\infty}f(x)=+\\infty$, ph\u01b0\u01a1ng tr\u00ecnh c\u00f3 \u0111\u00fang 3 nghi\u1ec7m ph\u00e2n bi\u1ec7t."
    )
    return question, answer, solution, dict(A=A, B=B, m=m, C=C)


def verify_D23(params):
    import numpy as np
    A, B, m, C = [int(params[k]) for k in ("A", "B", "m", "C")]
    def fz(z):
        xv = math.exp(z) - 1.0
        return A * xv * xv + B * xv + m * z + C
    # x=exp(z)-1 maps the full domain (-1,+infinity) to the real line.
    zlo = -35.0
    zhi = math.log(max(30.0, abs(B) + abs(C) + 30.0) + 1.0)
    while fz(zhi) <= 0:
        zhi *= 1.5
    grid = np.linspace(zlo, zhi, 50001)
    vals = [fz(float(z)) for z in grid]
    roots = 0
    for k in range(len(grid) - 1):
        if vals[k] * vals[k + 1] < 0:
            lo, hi = float(grid[k]), float(grid[k + 1])
            flo = vals[k]
            for _ in range(70):
                mid = (lo + hi) / 2
                fm = fz(mid)
                if flo * fm <= 0:
                    hi = mid
                else:
                    lo, flo = mid, fm
            roots += 1
    return roots == 3


# D47: choose log bases with log_p(q)=m/n. Substituting x+y=u^n
# turns the equation into an integer polynomial; Sturm root counts give the
# generated answer. Verification searches the original continuous variable t.
def _d47_exact_x_values(m, n):
    u = sp.symbols("u")
    r = sp.Rational(m, n)
    tmax = 2 ** sp.Rational(n, 2 * n - m)
    tmax_f = float(tmax)
    bound = (tmax_f + math.sqrt(2 * tmax_f ** float(r))) / 2
    edge = math.ceil(bound) + 1
    values = []
    for xv in range(-edge, edge + 1):
        expr = u ** (2 * n) - u ** m - 2 * xv * u**n + 2 * xv*xv
        poly = sp.Poly(expr, u)
        while poly.eval(0) == 0:
            poly = poly.exquo(sp.Poly(u, u))
        if poly.count_roots(0, sp.oo) > 0:
            values.append(xv)
    return values, bound


def gen_D47(m, n):
    m, n = int(m), int(n)
    assert 1 < m / n < 2 and math.gcd(m, n) == 1
    p, q = 2**n, 2**m
    xs, _ = _d47_exact_x_values(m, n)
    count = len(xs)
    assert count > 0
    question, answer = mc_count_prompt(
        f"CÃ³ bao nhiÃªu sá»‘ nguyÃªn $x$ Ä‘á»ƒ tá»“n táº¡i sá»‘ thá»±c $y$ thá»a mÃ£n "
        f"$\\log_{{{p}}}(x+y)=\\log_{{{q}}}(x^2+y^2)$?", count
    )
    solution = (
        f"Äáº·t $t=x+y>0$. Khi Ä‘Ã³ phÆ°Æ¡ng trÃ¬nh tÆ°Æ¡ng Ä‘Æ°Æ¡ng $x^2+(t-x)^2=t^{{{m}/{n}}}$. "
        f"Thay $t=u^{{{n}}}$ ($u>0$), ta Ä‘Æ°á»£c $u^{{{2*n}}}-u^{{{m}}}-2xu^{{{n}}}+2x^2=0$. "
        f"Äáº¿m cÃ¡c giÃ¡ trá»‹ nguyÃªn $x$ cÃ³ nghiá»‡m dÆ°Æ¡ng, thu Ä‘Æ°á»£c $x\\in"
        f"\\{{{','.join(map(str, xs))}\\}}$, cÃ³ {count} giÃ¡ trá»‹."
    )
    return question, answer, solution, dict(m=m, n=n, p=p, q=q, xs=xs)


def verify_D47(params):
    m, n = int(params["m"]), int(params["n"])
    r = m / n
    tmax = 2.0 ** (1.0 / (2.0 - r))
    bound = (tmax + math.sqrt(2.0 * tmax**r)) / 2.0
    edge = math.ceil(bound) + 1
    samples = [tmax * k / 12000 for k in range(1, 12001)]
    samples.append(1.0)
    found = []
    for xv in range(-edge, edge + 1):
        peak = max(t**r - (xv*xv + (t-xv)**2) for t in samples)
        # x=0 and x=1 have the exact solution t=1 for every allowed exponent.
        if peak > 1e-7 or xv in (0, 1):
            found.append(xv)
    return len(found) == len(params["xs"]) and found == [int(x) for x in params["xs"]]


# D52: enumerate exact rational inequalities for each a in a proven finite
# interval. The separate verifier checks in log space with high precision and
# uses a wider interval; the tail cutoff follows from the quadratic exponent.
def _d52_holds_exact(p, q, C, a, b):
    from fractions import Fraction
    return Fraction(p) ** (a*a+b) <= Fraction(q) ** (b-a) + C


def _d52_scan(p, q, C, N, k):
    bs = range(-N + 1, N)
    for M in range(2, 250):
        tails_fail = all(
            not _d52_holds_exact(p, q, C, M, b)
            and not _d52_holds_exact(p, q, C, -M, b)
            for b in bs
        )
        if tails_fail and p ** (2*M + 1) - 1 >= q - 1:
            break
    else:
        raise AssertionError("Could not establish a finite a-range")
    good = [a for a in range(-M, M + 1)
            if sum(_d52_holds_exact(p, q, C, a, b) for b in bs) >= k]
    return M, good


def gen_D52(p, q, C, N, k):
    p, q, C, N, k = map(int, (p, q, C, N, k))
    assert p > 1 and q > 1 and C > 0 and N > 1 and k > 0
    M, good = _d52_scan(p, q, C, N, k)
    count = len(good)
    assert 0 < count < 100
    question, answer = mc_count_prompt(
        f"CÃ³ bao nhiÃªu sá»‘ nguyÃªn $a$ sao cho cÃ³ Ã­t nháº¥t {k} sá»‘ nguyÃªn "
        f"$b\\in(-{N};{N})$ thá»a mÃ£n ${p}^{{a^2+b}}\\le {q}^{{b-a}}+{C}$?", count
    )
    solution = (
        f"Vá»›i má»—i sá»‘ nguyÃªn $a$, Ä‘áº¿m trá»±c tiáº¿p cÃ¡c sá»‘ nguyÃªn $b\\in"
        f"\\{{{-N+1},\\ldots,{N-1}\\}}$ thá»a báº¥t Ä‘áº³ng thá»©c. "
        f"Äiá»u kiá»‡n cÃ³ Ã­t nháº¥t {k} giÃ¡ trá»‹ $b$ Ä‘Ãºng vá»›i $a\\in"
        f"\\{{{','.join(map(str, good))}\\}}$. Vá»›i $a\\ge{M}$, váº¿ trÃ¡i tÄƒng cÃ²n "
        f"váº¿ pháº£i giáº£m theo $a$; vá»›i $a\\le-{M}$, pháº§n mÅ© báº­c hai lÃ m váº¿ trÃ¡i "
        "tÄƒng nhanh hÆ¡n váº¿ pháº£i. Kiá»ƒm tra biÃªn cho tháº¥y ngoÃ i khoáº£ng nÃ y khÃ´ng cÃ³ giÃ¡ trá»‹ phÃ¹ há»£p."
    )
    return question, answer, solution, dict(p=p, q=q, C=C, N=N, k=k, M=M, good=good)


def verify_D52(params):
    import mpmath as mp
    mp.mp.dps = 80
    p, q, C, N, k, M = [int(params[x]) for x in ("p", "q", "C", "N", "k", "M")]
    bs = range(-N + 1, N)
    lp, lq, lc = mp.log(p), mp.log(q), mp.log(C)
    found = []
    for a in range(-M - 4, M + 5):
        hits = 0
        for b in bs:
            lhs_log = mp.mpf(a*a+b) * lp
            q_log = mp.mpf(b-a) * lq
            peak = max(q_log, lc)
            rhs_log = peak + mp.log(mp.exp(q_log-peak) + mp.exp(lc-peak))
            if lhs_log <= rhs_log:
                hits += 1
        if hits >= k:
            found.append(a)
    if p ** (2*M + 1) - 1 < q - 1:
        return False
    # On the negative tail, the ratio of the two exponential terms grows
    # each step once a<=-M; at both boundary values every b already fails.
    for a in (M, -M):
        if any(sum(_d52_holds_exact(p, q, C, a, b) for b in bs) >= k for _ in [0]):
            return False
    return found == [int(v) for v in params["good"]]


# D57: choose bases 2 and 4 and set C=T^2(T+2). The logarithmic threshold
# is exactly T; generation counts lattice points in a circle, verification
# checks the original logarithmic inequality directly for all possible pairs.
def gen_D57(T):
    T = int(T)
    assert T >= 2
    C = T*T*(T+2)
    count = sum(2*math.isqrt(x*(T-x)) + 1 for x in range(1, T+1))
    question, answer = mc_count_prompt(
        f"CÃ³ bao nhiÃªu cáº·p sá»‘ nguyÃªn $(x;y)$ thá»a mÃ£n $x>0$ vÃ \n"
        f"$\\log_2(x^2+y^2+x)+\\log_4(x^2+y^2)"
        f"\\le\\log_2 x+\\log_4(x^2+y^2+{C}x)$?", count
    )
    solution = (
        f"Äáº·t $Q=x^2+y^2$ vÃ  $t=Q/x>0$. Báº¥t Ä‘áº³ng thá»©c tÆ°Æ¡ng Ä‘Æ°Æ¡ng "
        f"$\\log_2(1+t)\\le\\log_4(1+{C}/t)$. Váº¿ trÃ¡i tÄƒng, váº¿ pháº£i giáº£m; "
        f"hai váº¿ báº±ng nhau táº¡i $t={T}$ vÃ¬ $1+{C}/{T}=({T}+1)^2$. Do Ä‘Ã³ $t\\le{T}$, "
        f"hay $x^2+y^2\\le{T}x$. Vá»›i má»—i $x=1,\\ldots,{T}$, sá»‘ giÃ¡ trá»‹ $y$ lÃ  "
        f"$2\\lfloor\\sqrt{{x({T}-x)}}\\rfloor+1$; tá»•ng báº±ng {count}."
    )
    return question, answer, solution, dict(T=T, C=C, count=count)


def verify_D57(params):
    T, C, expected = int(params["T"]), int(params["C"]), int(params["count"])
    direct = 0
    for x in range(1, T + 1):
        for y in range(-T, T + 1):
            q = x*x + y*y
            lhs = math.log(q+x, 2) + math.log(q, 4)
            rhs = math.log(x, 2) + math.log(q+C*x, 4)
            if lhs <= rhs + 1e-12:
                direct += 1
    return direct == expected


# D78: the original constraint is equivalent to x+y>=3/2. Keep the constant
# 3 and the linked coefficients 2,4 fixed; vary only the objective's linear
# coefficients. Formula is checked against a dense grid in the original set.
def gen_D78(a, b):
    a, b = int(a), int(b)
    assert a > 0 and b > 0
    K = sp.Integer(3)
    x0 = sp.Rational(K + b - a, 4)
    assert 0 <= x0 < K/2
    p2 = sp.simplify(2*x0**2 + (a-b-K)*x0 + sp.Rational(K**2, 4) + sp.Rational(b*K, 2))
    p1 = sp.Rational(K**2, 4) + sp.Rational(a*K, 2)
    assert p1 > p2
    vals = bump_until_distinct([p2, p2+1, p2-1, 2*p2])
    opts = [latex(v) for v in vals]
    lines, answer = render_mc(opts, 0, prefix="P_{\\min}=")
    ax = "x" if a == 1 else f"{a}x"
    by = "y" if b == 1 else f"{b}y"
    prompt = (
        f"XÃ©t cÃ¡c sá»‘ thá»±c khÃ´ng Ã¢m $x,y$ thá»a mÃ£n $2x+y\\cdot4^{{x+y-1}}\\ge3$. "
        f"GiÃ¡ trá»‹ nhá» nháº¥t cá»§a $P=x^2+y^2+{ax}+{by}$ báº±ng\n\n" + "\n".join(lines)
    )
    solution = (
        "\u0110\u1eb7t $s=x+y$. N\u1ebfu $s<3/2$ th\u00ec $4^{s-1}<2$, n\u00ean $2x+y4^{s-1}<2x+2y<3$, tr\u00e1i \u0111i\u1ec1u ki\u1ec7n. "
        "N\u1ebfu $s\\ge3/2$ th\u00ec $4^{s-1}\\ge2$ v\u00e0 \u0111i\u1ec1u ki\u1ec7n \u0111\u01b0\u1ee3c th\u1ecfa m\u00e3n. V\u1eady mi\u1ec1n kh\u1ea3 thi l\u00e0 "
        "$x,y\\ge0$, $x+y\\ge3/2$. "
        f"V\u1edbi $x\\ge3/2$, $P\\ge(3/2)^2+{a}(3/2)={latex(p1)}$. "
        f"V\u1edbi $0\\le x<3/2$, ta c\u00f3 $y\\ge3/2-x$; do $y^2+{b}y$ t\u0103ng theo $y\\ge0$, "
        f"P kh\u00f4ng nh\u1ecf h\u01a1n gi\u00e1 tr\u1ecb tr\u00ean bi\u00ean $y=3/2-x$. Gi\u00e1 tr\u1ecb n\u00e0y nh\u1ecf nh\u1ea5t t\u1ea1i "
        f"$x={latex(x0)}$, b\u1eb1ng $P_{{\\min}}={latex(p2)}<{latex(p1)}$. \u0110\u00e2y l\u00e0 GTNN."
    )
    return prompt, answer, solution, dict(a=a, b=b, x0=str(x0), p2=str(p2), p1=str(p1))


def verify_D78(params):
    a, b = int(params["a"]), int(params["b"])
    target = float(sp.Rational(params["p2"]))
    step = 0.05
    best = float("inf")
    n = 60
    for i in range(n + 1):
        x = i*step
        for j in range(n + 1):
            y = j*step
            if 2*x + y*(4**(x+y-1)) >= 3 - 1e-12:
                value = x*x + y*y + a*x + b*y
                if value < best:
                    best = value
    return best >= target - 1e-9 and abs(best-target) < 1e-8


def expand_type(code, name, source, gen, verify, sampler, seed=0, target=90, max_tries=3000):
    rng = random.Random(seed)
    current = [r for r in ROWS if r["ma_dang"] == code]
    seen = {tuple(sorted((k, str(v)) for k, v in r["params"].items())) for r in current}
    questions = {r["de_bai"] for r in current}
    args_seen = set()
    made = len(current)
    for _ in range(max_tries):
        if made >= target:
            break
        args = tuple(sampler(rng))
        if args in args_seen:
            continue
        args_seen.add(args)
        try:
            q, ans, sol, params = gen(*args)
        except (AssertionError, ValueError, TypeError, ZeroDivisionError, OverflowError):
            continue
        key = tuple(sorted((k, str(v)) for k, v in params.items()))
        if key in seen or q in questions:
            continue
        opts = re.findall(r"(?m)^([A-D])\.\s*(.+)$", q)
        norm = [re.sub(r"[\s$.,]", "", v) for _, v in opts]
        if len(opts) != 4 or {k for k,_ in opts} != set("ABCD") or len(set(norm)) != 4:
            continue
        try:
            if not verify(params):
                continue
        except Exception:
            continue
        add_row(code, name, source, q, ans, sol, params)
        seen.add(key); questions.add(q); made += 1
    print(f"{code}: {made}/{target}")
    return made


def _sample_D08(rng):
    p, C, r = rng.sample(range(2, 25), 3)
    return p, C, r, rng.randint(1, 5), rng.randint(1, 5), rng.randint(1, 5)


def _sample_D47(rng):
    import math
    while True:
        n = rng.randint(2, 30)
        m = rng.randint(n + 1, int(1.5*n))
        if math.gcd(m, n) == 1:
            return m, n


def _sample_D52(rng):
    p, q = rng.randint(2, 6), rng.randint(2, 6)
    if p == q:
        q = q % 6 + 1
    return p, q, rng.randint(1, 30), rng.randint(3, 10), rng.randint(1, 2* rng.randint(1, 10))


def build_rows():
    ROWS.clear()
    candidates = {
        "D08": [(2,3,5,1,2,1),(2,5,3,1,2,1),(3,2,5,1,2,1),(3,5,2,1,2,1),(2,3,7,1,3,1),(5,3,2,1,2,1)],
        "D23": [(3,-6,3,-1),(3,-6,3,0),(3,-5,3,-1),(3,-5,3,0),(4,-8,3,-2),(4,-8,3,-1),(4,-8,3,0),(4,-8,3,1),(4,-8,3,2),(3,-7,4,-1),(3,-7,4,0),(3,-7,4,1),(2,-6,3,-1),(2,-6,3,0),(2,-6,3,1)],
        "D47": [(6,5),(5,4),(7,5),(8,5),(7,4),(5,3),(3,2),(9,5)],
        "D52": [(3,2,20,8,4),(5,3,100,8,4),(3,2,50,7,4),(4,3,30,8,4),(3,5,75,9,4),(5,2,50,7,4),(2,3,100,6,3),(2,5,100,8,3)],
        "D57": [(4,),(5,),(6,),(7,),(8,),(9,),(10,),(11,)],
        "D78": [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(2,4),(3,1),(3,2),(3,3),(3,4),(3,5)],
    }
    specs = {
        "D08": (gen_D08, verify_D08, "p007_q19", "Biá»ƒu diá»…n lÃ´garit qua cÃ¡c lÃ´garit cho trÆ°á»›c báº±ng Ä‘á»•i cÆ¡ sá»‘"),
        "D23": (gen_D23, verify_D23, "p039_q35", "Biá»‡n luáº­n sá»‘ nghiá»‡m phÆ°Æ¡ng trÃ¬nh lÃ´garit báº±ng kháº£o sÃ¡t hÃ m sá»‘"),
        "D47": (gen_D47, verify_D47, "p106_q50", "Äáº¿m sá»‘ nguyÃªn thá»a mÃ£n phÆ°Æ¡ng trÃ¬nh lÃ´garit cÃ³ nghiá»‡m thá»±c"),
        "D52": (gen_D52, verify_D52, "p119_q48", "Äáº¿m tham sá»‘ nguyÃªn theo sá»‘ giÃ¡ trá»‹ nguyÃªn thá»a báº¥t Ä‘áº³ng thá»©c mÅ©"),
        "D57": (gen_D57, verify_D57, "p133_q47", "Äáº¿m cáº·p sá»‘ nguyÃªn thá»a báº¥t Ä‘áº³ng thá»©c lÃ´garit báº±ng miá»n hÃ¬nh trÃ²n"),
        "D78": (gen_D78, verify_D78, "p203_q48", "TÃ¬m GTNN biá»ƒu thá»©c hai biáº¿n vá»›i Ä‘iá»u kiá»‡n chá»©a hÃ m mÅ©"),
    }
    for code, sets in candidates.items():
        fn, verifier, source, name = specs[code]
        for args in sets:
            try:
                prompt, answer, solution, params = fn(*args)
            except AssertionError:
                continue
            if verifier(params):
                add_row(code, name, source, prompt, answer, solution, params)
            else:
                raise AssertionError(f"Independent verification failed for {code} {params}")
    names_sources = {
        "D08": ("Bi?u di?n logarit qua c?c logarit cho tr??c b?ng ??i c? s?", "p007_q19", gen_D08, verify_D08, _sample_D08),
        "D23": ("Bi?n lu?n s? nghi?m ph??ng tr?nh logarit", "p039_q35", gen_D23, verify_D23,
                lambda r: (r.randint(1, 8), -r.randint(2, 30), r.randint(1, 10), r.randint(-20, 20))),
        "D47": ("??m s? nguy?n th?a m?n ph??ng tr?nh logarit c? nghi?m th?c", "p106_q50", gen_D47, verify_D47, _sample_D47),
        "D52": ("??m tham s? nguy?n theo s? gi? tr? nguy?n th?a b?t ph??ng tr?nh m?", "p119_q48", gen_D52, verify_D52, _sample_D52),
        "D57": ("??m c?p s? nguy?n th?a b?t ??ng th?c logarit", "p133_q47", gen_D57, verify_D57, lambda r: (r.randint(2, 100),)),
        "D78": ("T?m gi? tr? nh? nh?t bi?u th?c hai bi?n v?i ?i?u ki?n m?", "p203_q48", gen_D78, verify_D78,
                lambda r: (lambda b: (r.randint(max(1, b-2), b+3), b))(r.randint(1,80))),
    }
    for code, (name, source, gen, verify, sampler) in names_sources.items():
        expand_type(code, name, source, gen, verify, sampler, seed=int(code[1:])*100+8,
                    max_tries=10000 if code in ("D52", "D78") else 3000)
    return ROWS


def audit_choice_collisions(items):
    failures = []
    for row in items:
        choices = re.findall(r"(?m)^([A-D])\.\s*(.+)$", row["de_bai"])
        if len(choices) != 4 or {letter for letter, _ in choices} != set("ABCD"):
            failures.append((row["ma_dang"], row["id_goc"], "expected one each of A-D"))
            continue
        normalized = [re.sub(r"[\s$.,]", "", choice) for _, choice in choices]
        if len(set(normalized)) != 4:
            failures.append((row["ma_dang"], row["id_goc"], "duplicate displayed choices"))
    return failures


def main():
    rows = build_rows()
    failures = audit_choice_collisions(rows)
    if failures:
        raise SystemExit(f"Answer-choice collision(s): {failures}")
    batch_path = REPO / "data/questions/mu_logarit_extraction/bien_the/batch_round8.json"
    batch_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} independently verified variants to {batch_path}")


if __name__ == "__main__":
    main()
