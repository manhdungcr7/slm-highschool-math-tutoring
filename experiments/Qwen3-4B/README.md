# Qwen3-4B zero-shot — Mũ-Logarit (89 dạng, 8.010 biến thể)

**1 notebook duy nhất** (`KLTN_mulogarit_zeroshot_full90_Qwen3-4B.ipynb`),
upload y hệt lên cả 10 tài khoản Kaggle — mỗi tài khoản chỉ đổi `GROUP_ID`
(1-10) ở ô cấu hình, không cần sửa gì khác. Prompt, tham số sinh
(`temperature=0.6, top_p=0.95, top_k=20, seed=42, presence_penalty=1.2,
max_new_tokens=9216, enable_thinking=True`), và cách chấm điểm (regex lấy
chữ cái sau "Đáp án đúng"/`\boxed{}`) giữ nguyên y hệt bản Qwen3-4B
zero-shot đã dùng cho bộ Số phức — không đổi gì ngoài tên model, đường
dẫn dữ liệu, và việc gộp theo `ma_dang` thay vì `loai_so`.

## Chuẩn bị dữ liệu (chạy 1 lần, ở máy local)

```bash
python scripts/experiments/10_prepare_zeroshot_data.py
python scripts/experiments/11_build_zeroshot_notebooks.py
```

Lệnh đầu tạo `scripts/experiments/plan_solve_prompts_mulogarit_merged.json`
(8.010 câu, gộp theo `ma_dang`, chỉ lấy biến thể — không lấy câu gốc) và
`mulogarit_group_split.json` (danh sách dạng theo từng group, nhúng sẵn
vào notebook). Lệnh sau sinh ra file `.ipynb` duy nhất trong thư mục này.

## Upload lên Kaggle

Tạo 1 Kaggle Dataset chứa `plan_solve_prompts_mulogarit_merged.json`
(tên dataset tuỳ ý — không cần giống nhau giữa các tài khoản). Notebook
**tự dò đường dẫn thật** bằng `glob.glob('/kaggle/input/**/plan_solve_prompts_mulogarit_merged.json')`
thay vì gõ cứng, nên dù mỗi tài khoản đặt tên dataset khác nhau (đường
dẫn mount dưới `/kaggle/input/` sẽ khác nhau tuỳ tên) thì vẫn chạy được
mà không cần sửa gì — chỉ cần nhớ "Add Data" gắn đúng dataset đó vào
notebook trước khi chạy.

## Chạy trên 10 tài khoản

1. Upload cùng 1 file `KLTN_mulogarit_zeroshot_full90_Qwen3-4B.ipynb` lên
   cả 10 tài khoản Kaggle (và cùng 1 Dataset chứa file JSON ở trên).
2. Ở mỗi tài khoản, mở ô cấu hình (ô thứ 2, ngay dưới dòng
   `## Cấu hình`), đổi đúng 1 dòng:
   ```python
   GROUP_ID = 1  # <-- SUA SO NAY (1-10) THEO TUNG TAI KHOAN, roi Run All
   ```
   thành số nhóm tương ứng của tài khoản đó (2, 3, ..., 10), **không sửa
   gì khác**.
3. Bật GPU (khuyến nghị 2×T4 để vLLM dùng tensor-parallel), chạy
   "Run All".

Notebook tự nạp model Qwen3-4B 1 lần rồi lặp qua các dạng được giao cho
`GROUP_ID` đó, mỗi dạng tự ghi ra 1 file CSV riêng.

| GROUP_ID | Dạng |
|---|---|
| 1 | D01–D12 (9 dạng) |
| 2 | D13–D21 (9 dạng) |
| 3 | D22–D33 (9 dạng) |
| 4 | D34–D43 (9 dạng) |
| 5 | D44–D53 (9 dạng) |
| 6 | D54–D62 (9 dạng) |
| 7 | D63–D72 (9 dạng) |
| 8 | D73–D81 (9 dạng) |
| 9 | D82–D90 (9 dạng) |
| 10 | D91, D92, D93, D94, D36a, D36b, D50a, D50b (8 dạng) |

Mỗi dạng ghi ra 1 file CSV riêng tại `/kaggle/working/<ma_dang>_zeroshot_full90_Qwen3-4B.csv`
(viết thường, ví dụ `d01_zeroshot_full90_Qwen3-4B.csv`), chứa `STT`,
`ma_dang`, `dap_an_dung`, `model_chon`, `DUNG` (đúng/sai), `token`,
`het_ngan_sach` (có chạm giới hạn 9.216 token không), và văn bản suy
luận đầy đủ (`think`, `after`). Ô cuối notebook cũng in bảng tổng kết số
câu đúng/sai theo từng dạng trong nhóm đó. Tải toàn bộ các CSV từ cả 10
tài khoản về và gộp lại để tính kết quả tổng trên cả 89 dạng.

**Lưu ý:** D31 và D32 đã bị loại khỏi bộ dữ liệu (đề có phương án trùng nghĩa), nên bộ còn 89 dạng. Lần chạy Qwen3-4B zero-shot đã thực hiện khi còn 91 dạng; kết quả đã được lọc bỏ hai dạng này (các file zip tải về giữ nguyên làm bản gốc).

## `qwen_eval_kaggle_sophuc_zeroshot.ipynb` - Complex Numbers zero-shot baseline

The notebook that gave the Qwen3-4B zero-shot baseline for the Complex Numbers topic (it is not in the Complex Numbers repository).
Same prompt as above, thinking enabled, temperature 0.6, top-p 0.95, top-k 20, seed 42, 9,216 new tokens, **no presence penalty**
(the Exponential/Logarithm notebook above uses a presence penalty of 1.2). The pipeline uses these two sets of parameters for the zero-shot dạng
of the corresponding topic (`scripts/pipeline/build_pipeline_notebook.py`, units `ZS_ML` and `ZS_SP`).
