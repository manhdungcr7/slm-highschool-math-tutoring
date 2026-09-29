# Applying Small Language Models in High-School Mathematics Tutoring

This repository accompanies an undergraduate thesis studying whether a small
language model (SLM) can be guided to answer every multiple-choice
high-school mathematics question correctly, across more than one topic.

The first topic studied, Complex Numbers, was published as a separate paper
submitted to SoICT 2026; its code and data are in a dedicated repository:
[react-calculator-complex-numbers](https://github.com/manhdungcr7/react-calculator-complex-numbers).

This repository holds the data and scripts for the **second topic**,
**Exponential and Logarithm** equations and inequalities, extracted from the
same source review document.

## Repository structure

| Directory | Contents |
|---|---|
| [`scripts/pdf_to_markdown/`](scripts/pdf_to_markdown/) | Script that extracts candidate questions from the source PDF |
| [`data/questions/mu_logarit_extraction/`](data/questions/mu_logarit_extraction/) | The extracted and transcribed question set |

Each directory has its own README with further details.

## Status

This is early-stage data: 116 questions have been extracted and transcribed.
From the 123 originally selected candidates, 2 exact duplicates (the same
question appearing in two different source exams within the document) and 5
real-world application questions (compound-interest problems) were removed
to keep the scope to exponential/logarithmic equations and inequalities. The
remaining questions have not yet been expanded into evaluation variants (the
next step, following the same process used for the Complex Numbers topic).
