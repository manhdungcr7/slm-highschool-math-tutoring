# Applying Small Language Models in High-School Mathematics Tutoring

This repository accompanies an undergraduate thesis studying whether a small
language model (SLM) can be guided to answer every multiple-choice
high-school mathematics question correctly, across more than one topic.

The canonical, actively-maintained repository for each topic's own paper
submission stays separate (see below); this repository consolidates a copy
of the data, scripts, and results from every topic in one place for
convenience.

## Topics

### 1. Complex Numbers (published as a SoICT 2026 submission)

Canonical repository:
[react-calculator-complex-numbers](https://github.com/manhdungcr7/react-calculator-complex-numbers).
A full copy of that repository's tracked files (data, scripts, experiment
results) is mirrored here under [`so_phuc/`](so_phuc/) so both topics can be
browsed side by side. `so_phuc/README.md` is that repository's own README.

### 2. Exponential and Logarithm equations and inequalities

This is the second topic, extracted from the same source review document
used for Complex Numbers. Its data and scripts live at the top level of
this repository (this is the canonical location for this topic — there is
no separate dedicated repository for it).

| Directory | Contents |
|---|---|
| [`scripts/pdf_to_markdown/`](scripts/pdf_to_markdown/) | Script that extracts candidate questions from the source PDF |
| [`scripts/generate_questions/`](scripts/generate_questions/) | Scripts that generate numerical variants of the source questions per problem type |
| [`data/questions/mu_logarit_extraction/`](data/questions/mu_logarit_extraction/) | The extracted/transcribed question set, its problem-type classification, and generated variants |
| [`data/results/`](data/results/) | Model-solving results (ChatGPT, Gemini, Qwen3-4B zero-shot) |

Each directory has its own README with further details.

## Status

**Exponential and Logarithm**: 112 questions were transcribed, then D09 and D11 were excluded because they are general symbolic questions without numeric inputs to vary. The retained set has 110 questions across 89 problem types. Classification originally yielded 94 types; D03/D53 and D26/D36/D70 were later merged because they share the same criterion. From the 123 originally selected candidates, 2 exact duplicates and 9 real-world
application questions (compound interest, loan repayment,
bacterial/population growth, ad-campaign and forest-area growth models)
were removed to keep the scope to exponential/logarithmic equations and
inequalities. On the retained 110-question set, zero-shot results are: ChatGPT 90 correct / 18 incorrect / 2 undetermined, Gemini 109 correct / 1 incorrect, and Qwen3-4B 100 correct / 10 undetermined.

Evaluation-variant generation now covers all 89 retained problem types
(611 independently verified variants; 721 retained source and
variant rows). Every batch also passes a repository-wide scan for duplicate
answer choices. D09 and D11 are excluded because they are general symbolic
relations with no numeric values to vary. D84 now has four independently
verified variants; its source answer 14 remains in the retained set. Round 8
extended coverage to D08, D23, D47, D52, D57, and D78; round 9 adds D84. See
[`scripts/generate_questions/README.md`](scripts/generate_questions/README.md)
for the generation and verification methods.
