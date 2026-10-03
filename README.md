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

**Exponential and Logarithm**: 112 questions were transcribed, then D09 and D11 were excluded because they are general symbolic questions without numeric inputs to vary. A manual audit split D36 into D36a (selecting a universally true logarithm proposition) and D36b (evaluating a logarithm of a power), and split D50 into D50a (difference-to-quotient rule) and D50b (sum-to-product rule), because the questions differ in their data, requested task, or solution method. From the 123 originally selected candidates, 2 exact duplicates and 9 real-world
application questions (compound interest, loan repayment,
bacterial/population growth, ad-campaign and forest-area growth models)
were removed to keep the scope to exponential/logarithmic equations and
inequalities. D31 (two answer options that were the same set in 9 of 90 variants) and D32 (variants whose options are numerically equal) were then dropped after a Qwen3-4B zero-shot audit and are treated as non-existent; they remain only in the archival 112-question snapshot files and in git history. The retained set therefore has 107 questions across 89 problem types. On the retained 107-question set, zero-shot results are: ChatGPT 87 correct / 18 incorrect / 2 undetermined, Gemini 106 correct / 1 incorrect, and Qwen3-4B 97 correct / 10 undetermined.

Evaluation-variant generation covers all 89 retained problem types, each with 90 independently verified variants (8,010 variants; 8,117 retained source and variant rows). D43 was expanded with exact rational thresholds in the same logarithmic inequality. D51 was expanded by choosing coefficients whose quadratic factors at integer powers of 2, preserving the original question form and solution method; every generated case was checked by direct enumeration of the original inequality. Each batch also passes repository-wide scans for duplicate question statements and answer choices.
symbolic relations with no numeric values to vary. D84 has 90 independently
verified variants; its source answer 14 remains in the retained set. A
Windows-encoding bug introduced while expanding some batches to 90
variants (UTF-8 text mis-decoded as Windows-1252, corrupting Vietnamese
diacritics in several thousand rows) was found and corrected; every row
was re-scanned afterward and is clean. See
[`scripts/generate_questions/README.md`](scripts/generate_questions/README.md)
for the generation and verification methods.
