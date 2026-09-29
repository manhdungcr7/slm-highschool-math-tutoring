# `generate_questions/` (Exponential and Logarithm)

Generates numerical variants of the Exponential and Logarithm source questions.
Each generator computes the answer and then verifies it independently with a
different method. A repository-wide scan also checks that every generated
question has exactly four distinct answer choices labeled A-D.

**Current coverage: 88 of 91 problem types** (607 generated
variants; 112 source questions + 607 variants = 719 rows in the
combined CSV/XLSX). The remaining three types are explained below.

An initial pass treated many types as unsafe to vary. Later rounds recovered
types by deriving only the final answer independently, designing parameters
backwards from an equality point, using exact endpoint/continuity arguments,
or finding a general symbolic relation that does not depend on particular
numbers.

| Script | Coverage and independent check |
|---|---|
| `10_common_utils.py` | Shared LaTeX formatting and answer-choice utilities (`render_mc`, `bump_until_distinct`, etc.) |
| `11_generate_D01.py`-`14_generate_D53.py` | Pilot batch: D01, D12, D18, D53 |
| `15_generate_identities_A.py` | D06, D13, D30, D36, D54, D59, D60, D66, D76, D81, D90 |
| `16_generate_identities_B.py` | D32, D37, D44, D50, D64, D72, D77, D87 |
| `17_generate_basic_eq.py` | D02, D04, D07, D14, D19, D21, D27, D28, D31, D33, D34, D38, D42, D43, D48, D55, D58, D61, D62, D63, D71, D73, D80, D82, D85, D86, D91 |
| `18_generate_counting.py` | D25, D41, D74, D92; brute-force verified |
| `19_generate_identities_C.py` | D49, D20 |
| `22_export_all.py` | Combines source questions and every listed variant batch into CSV/XLSX |
| `23_generate_round2.py` | D05, D15, D16, D35, D40, D45, D51, D67, D69; Vieta/counting checks |
| `24_generate_round3.py` | D10, D46, D68, D94; parameters designed from equality/critical points |
| `25_generate_round4.py` | D29, D56, D83, D88; algebraic and direct-count verifiers |
| `26_generate_round5.py` | D22, D24, D39, D75, D93; symbolic and brute-force checks |
| `27_generate_round6.py` | D79, D89; endpoint signs and continuity (IVT), checked against direct evaluations |
| `28_generate_round7.py` | D17, D65; numeric minimization checks independent of the derived formulas |
| `29_generate_round8.py` | D08 (direct change-of-base evaluation), D23 (numerical root bracketing), D47 (continuous-variable search), D52 (high-precision log comparison), D57 (direct integer-pair enumeration), D78 (dense grid in the original feasible region) |

### Example

```bash
python scripts/generate_questions/29_generate_round8.py
python scripts/generate_questions/22_export_all.py
```

### Not yet covered (3 problem types)

D09, D11, D84.

- **D09 and D11:** their answers are general symbolic relationships, with no
  concrete numerical values to change into variants.
- **D84:** the source question's stated answer appears inconsistent with the
  equation. The source page must be checked before generating variants.
