# `generate_questions/` (Exponential and Logarithm)

Generates numerical variants of the Exponential and Logarithm source questions.
Each generator computes the answer and then verifies it independently with a
different method. A repository-wide scan also checks that every generated
question has exactly four distinct answer choices labeled A-D.

**Current coverage: all 89 retained problem types**: 87 types have 90 variants
each, while D43 has 21 and D51 has 35 (7,886 generated variants; 110 retained
source questions + 7,886 variants = 7,996 rows in the combined CSV/XLSX). D09
and D11 are excluded because they have no numeric inputs to vary. D43 and D51
stay below 90 because their valid parameter domains are genuinely narrow —
both were tried with much wider sampling ranges first, and widening further
only produced parameter combinations that fail the "clean answer" assertion
already used to keep every generated question well-posed, so the honest
counts were kept instead of forcing 90 by relaxing that condition.

**Note on a data-integrity bug found and fixed after the initial expansion
to 90/type**: several batches (`batch_round2.json`, `batch_round8.json`,
`D01_bien_the.json`) picked up a Windows console/tool encoding bug where
UTF-8 text got mis-decoded as Windows-1252 (mojibake), corrupting Vietnamese
diacritics in thousands of rows while the Vietnamese-looking garbled text
still passed the answer-choice and duplicate-question scans (those scans
check structure, not spelling). Caught by a manual spot-check of the actual
rendered question text, not by the automated checks. Fixed by restoring the
two files with clean git history (`23_generate_round2.py`, `11_generate_D01.py`)
from the commit before the bug was introduced and regenerating from those,
and by a byte-level Windows-1252 reversal for `batch_round8.json` (which had
no clean baseline to restore). Every row across all batches was re-scanned
afterward and confirmed to contain no mojibake or lost characters. The
lesson: structural checks (duplicate options, unique questions) do not catch
character-encoding corruption — spelling/rendering needs a direct look.

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
| `31_fix_and_expand.py` | Fixed the encoding bug in D01/round2, and expanded D01/round2/D51/D67 to (near-)90 variants using fast algebraic re-implementations of the slow sympy verifiers |
| `24_generate_round3.py` | D10, D46, D68, D94; parameters designed from equality/critical points |
| `25_generate_round4.py` | D29, D56, D83, D88; algebraic and direct-count verifiers |
| `26_generate_round5.py` | D22, D24, D39, D75, D93; symbolic and brute-force checks |
| `27_generate_round6.py` | D79, D89; endpoint signs and continuity (IVT), checked against direct evaluations |
| `28_generate_round7.py` | D17, D65; numeric minimization checks independent of the derived formulas |
| `29_generate_round8.py` | D08 (direct change-of-base evaluation), D23 (numerical root bracketing), D47 (continuous-variable search), D52 (high-precision log comparison), D57 (direct integer-pair enumeration), D78 (dense grid in the original feasible region) |
| `30_generate_round9.py` | D84; independent endpoint-sign enumeration at 80-digit precision |

### Example

```bash
python scripts/generate_questions/30_generate_round9.py
python scripts/generate_questions/22_export_all.py
```

D09 and D11 are excluded from the retained source set because they are general
symbolic questions without numbers to vary. All other retained types have 90
variants except D43 (21) and D51 (35), both genuinely narrow parameter
domains rather than incomplete runs. For each type, generation changes
numeric values within the original question form; an independent verifier
checks the resulting answer using a different computation method. A final
repository-wide audit checks that question statements are unique within
each type and that all four answer choices are distinct. D84's 90 variants
vary endpoint parameter U over the verified range, with the linked exponent
coefficient 3U; an independent 80-digit endpoint-sign verifier checks the
count.
