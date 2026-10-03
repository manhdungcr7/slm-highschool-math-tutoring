# ReAct + Calculator (Qwen3-4B), chuyên đề Mũ-Logarit

Cấu trúc prompt và thiết lập giống bộ Số phức (`so_phuc/experiments/Qwen3-4B`): prompt 5 phần,
ép mở đầu `<think>\nThought:`, vòng lặp ReAct chạy theo lô bằng vLLM, tool `Calculator` bằng sympy có
bộ nhớ biến. Tham số sinh: `temperature=0.3, top_p=0.95, top_k=20, seed=42, presence_penalty=1.2,
max_new_tokens=9216`.

## Các file

| File | Vai trò |
|---|---|
| `KLTN_D79_ReAct_Calculator_full90.ipynb` | Notebook Kaggle chạy 90 câu của dạng D79 |
| `prompt_D79.txt` | Prompt đầy đủ mà mô hình nhìn thấy (để đọc/kiểm tra, `{de_bai}` thay bằng `<DE_BAI_HERE>`) |
| `Mau_3_dang_kho_nhat_Qwen3-4B.xlsx` | 15 câu mẫu (D84, D89, D79) dùng để chọn dạng và viết hướng dẫn giải |

Mã nguồn dựng notebook nằm ở `scripts/experiments/react/`:

| File | Nội dung |
|---|---|
| `part_tool.py` | `PART_TOOL`: cách dùng Calculator, **dùng chung mọi dạng** |
| `part_kienthuc.py` | `PART_KIENTHUC`: kiến thức nền Mũ-Logarit, **dùng chung cả chuyên đề** (30 mục) |
| `calculator_backend.py` | Backend Calculator (nhúng nguyên văn vào notebook) |
| `dang_D79.py` | Phần riêng của D79: `PART_HUONGGIAI`, ví dụ `FEWSHOT`, `PART_NHIEMVU` |
| `build_react_notebook.py` | Dựng notebook |
| `test_notebook_loop.py` | Chạy thử vòng lặp của notebook bằng "mô hình giả" (không cần GPU) |

## Chạy trên Kaggle

1. Gắn Dataset chứa `plan_solve_prompts_mulogarit_merged.json` (cùng file đã dùng cho zero-shot) vào notebook.
   Notebook tự dò đường dẫn bằng `glob`.
2. Bật GPU (khuyến nghị 2×T4), "Run All". Kết quả: `/kaggle/working/d79_react_calculator_full90.csv`.
3. Muốn thử vài câu trước: đặt `RUN_STT = [1, 2, 3]` ở ô cấu hình.

## Thêm một dạng mới

Tạo `scripts/experiments/react/dang_Dxx.py` (cùng các tên biến như `dang_D79.py`: `MA_DANG`, `FREE_UNKNOWNS`,
`PART_HUONGGIAI`, `EXAMPLE_*`, `PART_NHIEMVU`), rồi chạy
`python scripts/experiments/react/build_react_notebook.py Dxx`. `PART_TOOL` và `PART_KIENTHUC` giữ nguyên.
Lệnh dựng sẽ không chạy tiếp nếu ví dụ không chạy được bằng Calculator thật hoặc nếu quy trình trong
`PART_NHIEMVU` không ra đúng khoá (trên cả 90 câu). Hàm `replay_method` và `lint_identifiers` hiện viết riêng cho D79,
cần viết lại cho dạng mới.

## Khác bản Số phức

- `MAX_MODEL_LEN` được tính theo độ dài prompt (prompt Mũ-Logarit dài hơn, khoảng 6.000 token; bản Số phức đặt cố định 14336).
- `PART_TOOL` đổi phần cú pháp riêng của số phức (`I`, `conjugate`, mô-đun) sang cú pháp của Mũ-Logarit
  (`log`, `exp`, `floor`, `ceiling`, `N(...)`, so sánh `<` `>`); mọi quy tắc chung giữ nguyên văn.
- Backend bổ sung: so sánh bất đẳng thức (`a < b`), lưu kết quả `True/False` vào biến (`test_A = Eq(...)`).
