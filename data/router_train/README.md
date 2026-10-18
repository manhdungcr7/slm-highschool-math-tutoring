# Dữ liệu huấn luyện bộ định tuyến dạng bài

Bộ dữ liệu mới để fine-tune mô hình nhận ra **dạng bài** của một đề. Bộ dữ liệu hiện có (8010 đề Mũ-Logarit và 4860 đề Số phức)
được giữ nguyên làm **tập kiểm tra**; thư mục này là **tập huấn luyện** gồm các đề sinh mới, không trùng với tập kiểm tra.

## Nội dung

| File | Nội dung |
|---|---|
| `bien_the_moi_142_dang.csv`, `.jsonl` | 12780 đề mới: đúng 90 đề cho mỗi dạng trong 142 dạng (88 dạng Mũ-Logarit, 54 dạng Số phức), kèm đáp án đúng và lời giải |
| `finetune_router.jsonl`, `.csv` | 12780 cặp đầu vào, đầu ra để fine-tune (đã xáo trộn thứ tự) |
| `assemble_report.json` | Với mỗi dạng: số đề ứng viên, số đề đạt, số đề bị loại và lý do |

Cột của `bien_the_moi_142_dang`: `ten_goi` (ví dụ "Dạng 17"), `so_dang`, `ma_cu` (mã cũ, ví dụ ML_D20), `chu_de`, `stt`, `nguon_sinh`
(`pass` = bộ sinh gốc với hạt giống mới, `sp` = bộ sinh Số phức, `extra` = bộ sinh gốc với khoảng tham số rộng hơn), `id_goc`,
`de_bai`, `dap_an_dung`, `loi_giai`, `mo_ta_dang`.

## Định dạng fine-tune

Đầu vào là lời yêu cầu cộng với đề bài, đầu ra là tên dạng và mô tả dạng (đúng văn bản trong `data/catalogue/danh_muc_trong_prompt.txt`):

```
Đầu vào : Hãy xác định dạng bài của đề bài sau. Chỉ trả lời đúng một dòng theo mẫu "Dạng N: mô tả dạng bài",
          trong đó N là số thứ tự của dạng.

          Đề bài:
          <đề bài và bốn phương án>
Đầu ra  : Dạng 38: Giải bất phương trình lôgarit thập phân: log x lớn hơn hoặc bằng một số (...)
```

Mỗi dòng của `finetune_router.jsonl` có `prompt`, `completion` và `messages` (hai lượt user, assistant). Loss chỉ tính trên đầu ra.

## Cách sinh

* Mũ-Logarit: chạy lại các bộ sinh gốc (`scripts/generate_questions`) nhiều lần với hạt giống dịch đi (`scripts/router/ml_passes`);
  các dạng mà khoảng tham số gốc đã dùng hết (ví dụ D02, D18, D80, D84, D43) được sinh thêm bằng `scripts/router/gen_ml_extra.py`
  với khoảng tham số rộng hơn (cơ số lớn hơn, khoảng rộng hơn), vẫn dùng đúng hàm sinh và hàm kiểm tra của dạng đó.
* Số phức: `scripts/router/gen_sp_new.py` dùng lại các hàm sinh `so_phuc_generators/cau_XX.py` với hạt giống mới, giữ đúng số đề
  của từng câu gốc và từng loại số (nguyên, hữu tỉ, vô tỉ) như bộ hiện có.
* Ghép và chọn: `scripts/router/assemble_train.py`; kiểm tra cuối: `scripts/router/audit_train.py`.

## Kiểm tra đã làm (đều đạt)

1. Mỗi dạng đúng 90 đề; tổng 12780.
2. Không đề nào trùng một đề của tập kiểm tra (so theo câu dẫn, và theo cả bộ phương án với bốn dạng có câu dẫn giống nhau), không đề nào lặp trong tập mới.
3. Mỗi đề có đúng bốn phương án A đến D khác nhau và đáp án đúng là một trong chúng; không lỗi mã hóa.
4. Mỗi đề khớp dấu hiệu nhận dạng của đúng dạng của nó và của không dạng nào khác (cùng bộ kiểm tra đã dùng cho danh mục tên dạng).
5. Đáp án: hàm kiểm tra riêng của từng bộ sinh đã đạt với mọi đề giữ lại. Kiểm tra độc lập lần hai:
   * 31 trong 32 dạng Mũ-Logarit có chương trình Calculator (ReAct): phát lại trên 2790 đề mới, **2788 trùng đáp án**; 2 đề còn lại
     (Dạng 69, mã cũ ML_D75, lôgarit cơ số 3) chương trình phát lại không xét được vì chỉ biết cơ số 2, đã tự đếm lại và đáp án đúng.
     Dạng ML_D79 không có chương trình phát lại nên không kiểm tra được bằng cách này.
   * Số phức: hai script kiểm tra độc lập của bộ sinh gốc chỉ có checker cho khoảng 14% số câu (khoảng 690 trên 4977); các câu còn lại
     chỉ dựa vào hàm kiểm tra riêng của từng câu. Các "FAIL" còn lại (87 và 9 câu) là giới hạn của chính script kiểm tra (so chuỗi `\dfrac` với `\frac`;
     đường tròn đi qua gốc tọa độ) và xuất hiện cùng tỉ lệ trên bộ dữ liệu hiện có.

## Lưu ý

* Với các dạng có khoảng tham số nhỏ, một phần đề mới dùng số lớn hơn bộ hiện có (ví dụ cơ số 93 đến 600 thay cho 2 đến 92). Mục đích là nhận dạng,
  không phụ thuộc độ lớn của số.
* Dạng ML_D59 đã bị bỏ (trùng ML_D20), nên không có trong 142 dạng.
