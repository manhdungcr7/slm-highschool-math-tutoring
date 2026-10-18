# Source documents

## `DAP AN.pdf`

"Tuyển tập đề thi TNTHPT môn Toán 2016-2023" (247 pages), by Nguyễn Ngọc Nguyên, Tổ Toán, Trường THPT Chuyên Bình Long
(school year 2022-2023). It collects the official and sample exam papers from 2016-2017 on, with solutions and an answer key for each
paper. It is the review document the thesis questions were taken from.

* `scripts/pdf_to_markdown/20_extract_mu_logarit.py` extracts the candidate Exponential/Logarithm questions from it and renders their
  pages for transcription (`--pdf` defaults to this file). The transcribed questions are in
  `data/questions/mu_logarit_extraction/`.
* The Complex Numbers questions (65 source questions) come from the same kind of review document; see `so_phuc/data/README.md`.

This is a third-party teaching document. It is kept here only so that the extraction and the audit of the transcription can be
repeated. Credit the author when you use it, and check that you may redistribute it before publishing this repository more widely.
