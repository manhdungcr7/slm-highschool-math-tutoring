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

**Exponential and Logarithm**: 112 questions extracted, transcribed, and
classified into 94 problem types (Mã dạng). From the 123 originally selected
candidates, 2 exact duplicates and 9 real-world application questions
(compound interest, loan repayment, bacterial/population growth,
ad-campaign and forest-area growth models) were removed to keep the scope
to exponential/logarithmic equations and inequalities. Zero-shot
model-solving results on these 112 questions: ChatGPT 92 correct / 18
incorrect / 2 undetermined, Gemini 111 correct / 1 incorrect, Qwen3-4B
102 correct / 10 undetermined.

Evaluation-variant generation has started as a pilot covering 4 of the 94
problem types (D01, D12, D18, D53 — 15 source questions), producing 90
SymPy-generated variants, each checked by an independent verifier. The
remaining 90 problem types still need their own generator.
