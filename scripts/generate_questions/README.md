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

**Current coverage: 56 of 91 problem types** (56 source questions, 404
generated variants; 112 source questions + 404 variants = 516 rows in
`Mu_Logarit_bien_the_full.csv`/`.xlsx`). The remaining 35 problem types are
listed below — **not yet implemented**, not silently skipped.

| Script | Covers |
|---|---|
| `10_common_utils.py` | Shared LaTeX formatting and answer-choice utilities (`render_mc`, `bump_until_distinct`, etc.) |
| `11_generate_D01.py`–`14_generate_D53.py` | Pilot batch: D01, D12, D18, D53 |
| `15_generate_identities_A.py` | Pure logarithm identities: D06, D13, D30, D36, D54, D59, D60, D66, D76, D81, D90 |
| `16_generate_identities_B.py` | "Derive a relation between variables from a log identity": D32, D37, D44, D50, D64, D72, D77, D87 |
| `17_generate_basic_eq.py` | Basic equations/inequalities/derivatives/domains: D02, D04, D07, D14, D19, D21, D27, D28, D31, D33, D34, D38, D42, D43, D48, D55, D58, D61, D62, D63, D71, D73, D80, D82, D85, D86, D91 |
| `18_generate_counting.py` | Integer-counting problems (brute-force-verified): D25, D41, D74, D92 |
| `19_generate_identities_C.py` | D49, D20 |
| `22_export_all.py` | Combine every batch + the 112 source questions into the final CSV/Excel |

### Example

```bash
cd scripts/generate_questions
python 11_generate_D01.py   # ... through 19_generate_identities_C.py
python 22_export_all.py
```

### Not yet covered (35 problem types)

These require case-based bảng biến thiên analysis, transcendental critical
points (roots of things like `3^t = t`), multi-variable geometric arguments
(Cauchy-Schwarz/AM-GM equality cases), or other reasoning that is harder to
parametrize into a closed form safely re-derivable by an independent
checker. Rather than risk generating a subtly wrong variant (as happened
once before on the Complex Numbers topic, requiring a whole problem type to
be discarded), these were left for a follow-up pass instead of being forced
through:

D05, D08, D09, D10, D11, D15, D16, D17, D22, D23, D24, D29, D35, D39, D40,
D45, D46, D47, D51, D52, D56, D57, D65, D67, D68, D69, D75, D78, D79, D83,
D84, D88, D89, D93, D94.

A few of these (D05, D15, D24, D35, D39, D45) look tractable with more
time — they weren't skipped for being unsafe, just not yet reached.
