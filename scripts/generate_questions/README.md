# `generate_questions/` (Exponential and Logarithm)

Generates numerical variants of the Mu-Logarit source questions using SymPy.
For each source question, a template function samples new parameters,
builds the question text and four answer choices, computes the correct
answer, and an independent verifier recomputes the answer via a **different**
method than the one used to build the question (`sp.solve`, `sp.diff`,
`sp.solve_univariate_inequality`, direct numeric substitution for
"always-true" identities, or brute-force integer enumeration for
counting problems) to catch bugs in the generator itself. After every batch,
a repo-wide scan also checks that no question's four answer choices collide
after rendering — this caught several real bugs (see commit history).

**Current coverage: 65 of 91 problem types** (454 generated variants; 112
source questions + 454 variants = 566 rows in
`Mu_Logarit_bien_the_full.csv`/`.xlsx`). The remaining 26 problem types are
listed below — **not yet implemented**, not silently skipped.

A first pass marked ~35 problem types as "too fragile to parametrize
safely." On review, most of that call was too conservative: a problem
type is genuinely unsafe only when the **final displayed answer** must be
a clean closed-form value that depends on an accidental numeric
coincidence in the source question (e.g. a "find min/max" question whose
clean answer only appears because the original author picked matching
coefficients). Problem types whose final answer is an **integer count** or
a **sum/product of roots via Vieta's formulas** stay safe to vary even
when the intermediate algebra is ugly or irrational, because the checker
can re-derive that final integer independently (by brute-force
enumeration, or by using Vieta's formulas directly instead of solving for
each root). Round 2 below reclaimed 9 problem types this way.

| Script | Covers |
|---|---|
| `10_common_utils.py` | Shared LaTeX formatting and answer-choice utilities (`render_mc`, `bump_until_distinct`, etc.) |
| `11_generate_D01.py`–`14_generate_D53.py` | Pilot batch: D01, D12, D18, D53 |
| `15_generate_identities_A.py` | Pure logarithm identities: D06, D13, D30, D36, D54, D59, D60, D66, D76, D81, D90 |
| `16_generate_identities_B.py` | "Derive a relation between variables from a log identity": D32, D37, D44, D50, D64, D72, D77, D87 |
| `17_generate_basic_eq.py` | Basic equations/inequalities/derivatives/domains: D02, D04, D07, D14, D19, D21, D27, D28, D31, D33, D34, D38, D42, D43, D48, D55, D58, D61, D62, D63, D71, D73, D80, D82, D85, D86, D91 |
| `18_generate_counting.py` | Integer-counting problems (brute-force-verified): D25, D41, D74, D92 |
| `19_generate_identities_C.py` | D49, D20 |
| `23_generate_round2.py` | Reclaimed from the original skip list: D05, D15, D16, D35, D40, D45, D51, D67, D69 |
| `22_export_all.py` | Combine every batch + the 112 source questions into the final CSV/Excel |

### Example

```bash
cd scripts/generate_questions
python 11_generate_D01.py   # ... through 23_generate_round2.py
python 22_export_all.py
```

### Not yet covered (26 problem types)

These still need either a clean closed-form answer that depends on an
accidental numeric coincidence in the original question (so varying the
numbers breaks the "nice" answer), a two-variable inequality argument
(Cauchy-Schwarz/AM-GM equality case, geometric distance-to-line bound), or
a case-heavy bảng biến thiên that doesn't reduce to a Vieta-style
shortcut:

D08, D09, D10, D11, D17, D22, D23, D24, D29, D39, D46, D47, D52, D56, D57,
D65, D68, D75, D78, D79, D83, D84, D88, D89, D93, D94.

D09 and D11 are a different kind of "not covered": their correct answer is
a fully general symbolic relationship (e.g. "$\ln(ab)=\ln a+\ln b$ for any
positive $a,b$") with no concrete number in the question to vary in the
first place — there's no numeric variant to generate, not a hard one.
