# Pool of real exam questions

Questions crawled from the "đề thi thử THPT Quốc gia môn Toán" pages of loigiaihay.com, with the answer key printed on the page.
They are the raw material for building evaluation sets of real questions. The text is the page text with formulas as `$...$`; nothing is
rewritten.

| File | Questions | With answer key | Exams | Level 36-50 |
|---|---|---|---|---|
| `pool_loigiaihay_thithu_3111.json` | 3,111 | 2,889 | 82 | 955 |
| `pool_loigiaihay_258_more.json` | 258 | 257 | 8 | 77 |

Fields: `num` (question number in its exam, 1-50; numbers 36-50 are the application and advanced levels), `stem`, `opts` (`A`-`D`), `ans`
(letter, empty when the page had no readable key), `url` (the exam page), and `title` (second file only).

These pools contain all topics; most questions are not Exponential/Logarithm or Complex Numbers and most application-level ones
fit **none** of the 142 dạng. Use `scripts/realworld_eval/filter_candidates.py` to select Exponential/Logarithm and Complex Numbers
candidates that are new, then decide the dạng of each one by hand. Re-create or extend the pools with `scripts/realworld_eval/crawl_loigiaihay.py`
and `parse_exam_pages.py`.

The 70 web questions of `data/results/pipeline_realworld/` also come from loigiaihay.com exam pages (see their `source_url`), the same kind of page as in these pools.
