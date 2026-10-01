# Qwen3-4B zero-shot — Mũ-Logarit (91 dạng, 8.190 biến thể)

10 notebook, mỗi notebook phụ trách ~9 dạng (riêng group1 có 10 dạng),
để chia chạy trên 10 tài khoản Kaggle GPU khác nhau. Prompt, tham số sinh
(`temperature=0.6, top_p=0.95, top_k=20, seed=42, presence_penalty=1.2,
max_new_tokens=9216, enable_thinking=True`), cách chấm điểm (regex lấy
chữ cái sau "Đáp án đúng"/`\boxed{}`), và cấu trúc cell đều giữ nguyên
như bản Qwen3-4B zero-shot đã dùng cho bộ Số phức — không đổi gì ngoài
tên model, đường dẫn dữ liệu, và việc gộp theo `ma_dang` thay vì `loai_so`.

## Chuẩn bị dữ liệu (chạy 1 lần, ở máy local)

```bash
python scripts/experiments/10_prepare_zeroshot_data.py
python scripts/experiments/11_build_zeroshot_notebooks.py
```

Lệnh đầu tạo `scripts/experiments/plan_solve_prompts_mulogarit_merged.json`
(8.190 câu, gộp theo `ma_dang`, chỉ lấy biến thể — không lấy câu gốc) và
`mulogarit_group_split.json` (danh sách dạng theo từng group). Lệnh sau
sinh 10 file `.ipynb` trong thư mục này.

## Upload lên Kaggle

Tạo 1 Kaggle Dataset chứa `plan_solve_prompts_mulogarit_merged.json`,
đặt tên sao cho đường dẫn khớp với biến `KAGGLE_DATA_PATH` đầu mỗi
notebook:

```
/kaggle/input/datasets/ggducky/mulogarit-full/plan_solve_prompts_mulogarit_merged.json
```

Nếu dùng tên dataset khác, sửa dòng `MERGED_DATA_PATH = '...'  # SUA NEU KHAC`
ở ô code đầu tiên của mỗi dạng trong notebook (tìm-thay toàn bộ 1 lần).

## Chạy trên 10 tài khoản

Mỗi notebook độc lập, không phụ thuộc lẫn nhau — tải lên 10 tài khoản
Kaggle khác nhau, bật GPU (khuyến nghị 2×T4 để vLLM dùng tensor-parallel),
chạy "Run All". Mỗi notebook tự nạp model 1 lần ở dạng đầu tiên rồi dùng
lại cho các dạng còn lại trong cùng notebook (tránh nạp lại nhiều lần gây
hết bộ nhớ GPU, giống cách bản Số phục đã làm).

| Notebook | Dạng |
|---|---|
| group1 | D01–D13 (10 dạng) |
| group2 | D14–D22 |
| group3 | D23–D32 |
| group4 | D33–D42 |
| group5 | D43–D52 |
| group6 | D53–D61 |
| group7 | D62–D71 |
| group8 | D72–D80 |
| group9 | D81–D89 |
| group10 | D90, D91, D92, D93, D94, D36a, D36b, D50a, D50b |

Mỗi dạng ghi ra 1 file CSV riêng tại `/kaggle/working/<ma_dang>_zeroshot_full90_Qwen3-4B.csv`
(viết thường, ví dụ `d01_zeroshot_full90_Qwen3-4B.csv`), chứa `STT`,
`ma_dang`, `dap_an_dung`, `model_chon`, `DUNG` (đúng/sai), `token`,
`het_ngan_sach` (có chạm giới hạn 9.216 token không), và văn bản suy
luận đầy đủ (`think`, `after`). Tải toàn bộ các CSV này về và gộp lại để
tính kết quả tổng (ví dụ nối theo `ma_dang`, nhóm theo dạng rồi theo
toàn bộ 91 dạng).
