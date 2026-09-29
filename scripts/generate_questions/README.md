# `generate_questions/` (Exponential and Logarithm)

Generates numerical variants of the Mu-Logarit source questions using SymPy,
following the same methodology as `so_phuc/scripts/generate_questions/`:
for each source question, a template function samples new parameters,
builds the question text and four answer choices, computes the correct
answer symbolically, and an independent verifier recomputes the answer via
a different symbolic path (`sp.solve`, `sp.diff`, or
`sp.solve_univariate_inequality` rather than the closed-form arithmetic used
to generate the question) to catch bugs in the generator itself.

This is currently a **pilot covering 4 of the 94 problem types** (the ones
with the most source questions): D01, D12, D18, D53 (15 source questions,
90 generated variants). The remaining 90 problem types have not been
covered yet.

| Script | Purpose |
|---|---|
| `10_common_utils.py` | Shared LaTeX formatting and answer-choice utilities |
| `11_generate_D01.py` | log_a(mx+c)=k (5 source questions) |
| `12_generate_D12.py` | a^(mx+c)=a^k (4 source questions) |
| `13_generate_D18.py` | derivative of y=log_a(x) (3 source questions) |
| `14_generate_D53.py` | log_a(mx+c)>k (3 source questions) |
| `20_verify_pilot.py` | Independent re-derivation and check for every generated variant |
| `21_export_pilot.py` | Combine source questions + variants into the final CSV/Excel, aborting if any variant fails verification |

### Example

```bash
cd scripts/generate_questions
python 11_generate_D01.py
python 12_generate_D12.py
python 13_generate_D18.py
python 14_generate_D53.py
python 21_export_pilot.py
```

Each generator produces 2 variants x 3 parameter buckets = 6 variants per
source question. The buckets vary by problem type but generally cover: a
coefficient of 1 on x, a coefficient greater than 1, and a case where the
answer is a fraction (rather than being split by "loại số" nguyên/hữu
tỉ/vô tỉ the way Complex Numbers was, since these problems don't have an
a+bi structure).
