# ReAct + Calculator (Qwen3-4B), chuyên đề Mũ-Logarit

Cấu trúc prompt và thiết lập giống bộ Số phức (`so_phuc/experiments/Qwen3-4B`): prompt 5 phần,
ép mở đầu `<think>\nThought:`, vòng lặp ReAct chạy theo lô bằng vLLM, tool `Calculator` bằng sympy có
bộ nhớ biến. Tham số sinh: `temperature=0.3, top_p=0.95, top_k=20, seed=42, presence_penalty=1.2,
max_new_tokens=9216`.

## Các file

| File | Vai trò |
|---|---|
| `KLTN_D79_ReAct_Calculator_1cau.ipynb` | Notebook chạy thử **từng câu** (giống các file `*_1cau` của Số phức) |
| `KLTN_D79_ReAct_Calculator_full90.ipynb` | Notebook Kaggle chạy 90 câu của dạng D79 |
| `prompt_D79.txt` | Prompt đầy đủ mà mô hình nhìn thấy (để đọc/kiểm tra, `{de_bai}` thay bằng `<DE_BAI_HERE>`) |
| `Mau_3_dang_kho_nhat_Qwen3-4B.xlsx` | 15 câu mẫu (D84, D89, D79) dùng để chọn dạng và viết hướng dẫn giải |

Mã nguồn dựng notebook nằm ở `scripts/experiments/react/`:

| File | Nội dung |
|---|---|
| `part_tool.py` | `PART_TOOL`: cách dùng Calculator, **dùng chung mọi dạng** |
| `part_kienthuc.py` | `PART_KIENTHUC`: kiến thức nền Mũ-Logarit, **dùng chung cả chuyên đề** (33 mục; mục 31-33 thêm sau D79 cho 31 dạng còn lại) |
| `calculator_backend.py` | Backend Calculator (nhúng nguyên văn vào notebook) |
| `dang_D79.py` | Phần riêng của D79: `PART_HUONGGIAI`, ví dụ `FEWSHOT`, `PART_NHIEMVU` |
| `build_react_notebook.py` | Dựng notebook |
| `test_notebook_loop.py` | Chạy thử vòng lặp của notebook bằng "mô hình giả" (không cần GPU) |

## 10 notebook cho 31 dạng còn lại (`KLTN_G01` ... `KLTN_G10`)

Mỗi notebook nạp model **một lần** rồi chạy lần lượt 3 dạng (G10 có 4 dạng), mỗi dạng đủ 90 câu, ghi
`<mã dạng>_react_calculator_full90.csv` và `summary_<nhóm>.csv` vào `/kaggle/working`. Chỉ cần gắn Dataset có
`plan_solve_prompts_mulogarit_merged.json` rồi **Save & Run All**.

| Notebook | Các dạng |
|---|---|
| G01 | D89, D84, D47 |
| G02 | D75, D69, D57 |
| G03 | D93, D52, D65 |
| G04 | D78, D68, D56 |
| G05 | D28, D46, D23 |
| G06 | D88, D41, D16 |
| G07 | D24, D25, D94 |
| G08 | D83, D71, D29 |
| G09 | D22, D40, D51 |
| G10 | D45, D08, D17, D10 |

Mã dựng: `scripts/experiments/react/dang_Dxx.py` (mỗi dạng: `PART_HUONGGIAI` theo lời giải mẫu của câu gốc, ví dụ,
`program()` là dãy lệnh Calculator của phương pháp), `framework.py`, `build_multi_notebook.py <nhóm> <dạng>...`,
`test_multi_loop.py <nhóm>` (chạy thử vòng lặp bằng mô hình giả), `check_notebooks.py`. Trước khi ghi notebook,
bộ dựng chạy lại phương pháp trên cả 90 câu và câu gốc (không dùng mô hình) và buộc ra đúng khóa; ví dụ trong prompt
được kiểm chứng độc lập bằng cách tính vét cạn/số học khác. Backend có thêm hàm đếm `Count(điều kiện, (n, thấp, cao))`
(cho phép lồng nhau).

### Kết quả lần chạy 1 (2880 câu) và lần chạy lại 14 dạng (`KLTN_H01` ... `KLTN_H05`)

Lần chạy 1: 17 dạng đạt 90/90, 14 dạng còn sai 1 đến 16 câu (tổng 53 câu sai). Đọc lại các câu sai, nguyên nhân đều nằm ở prompt:

| Nguyên nhân (trong prompt) | Dạng bị ảnh hưởng | Cách sửa |
|---|---|---|
| Phương án được chép lại **sau khi đã biết đáp án** nên mô hình sắp xếp lại / chép sai (đưa phương án đúng lên A, sắp tăng dần, bịa số) | D23, D25, D29, D52, D57, D68, D71, D75, D83 | Lưu bốn phương án vào bộ nhớ Calculator **trước khi tính** (`option_a` ... `option_d`, mỗi phương án một lệnh), rồi chỉ so sánh `Eq(answer, option_a)` |
| Phải **đọc dấu ngoặc** `[`, `(` của từng phương án khoảng bằng chữ, mô hình gán lệnh đúng cho phương án A | D40 (16 sai), D45 (7), D10 (3) | Calculator làm việc đó: kết quả là `Interval...`, mỗi phương án dịch máy móc sang `Interval(...)`, `Interval.open`, `Interval.Ropen`, `Interval.Lopen`, và `Eq` so sánh cả hai đầu lẫn dấu ngoặc |
| Mẫu lệnh dùng chữ `A`, `B` làm chỗ điền số nên mô hình coi chúng là tên biến và lặp lệnh lỗi 24 lần | D17 (4 sai) | Lưu `coef_first`, `coef_second` bằng lệnh riêng; backend nói rõ tên nào chưa được lưu; vòng lặp nhắc khi lệnh lỗi bị gửi lại y nguyên |
| Câu "hệ số của $x^2$ trong ngoặc" không nói rõ dấu, mô hình viết `- (-11)*x**2` | D89 (3 sai) | Nói rõ $B$, $C$ là số đứng sau dấu trừ, không kèm dấu trừ |
| Ví dụ mẫu có đáp án A (D40, D10) làm mô hình thiên về chọn A | D40, D10 | Đổi vị trí đáp án của ví dụ sang C hoặc D |

`KLTN_H01` (D40, D45, D10), `H02` (D75, D23, D17), `H03` (D89, D29, D83), `H04` (D52, D57, D68), `H05` (D25, D71)
chỉ chứa 14 dạng đó, prompt mới ghi ở `prompt_Dxx_v2.txt`. 17 dạng đạt 90/90 ở lần 1 giữ nguyên prompt cũ. Kết quả lần
chạy 1 nằm ở `F:\Math\ReAct_Calculator_CD2\`; `scripts/experiments/react/summarize_results.py` và `show_fail.py` tóm tắt và in các câu sai.

**Lần chạy lại H01 đến H05 (1260 câu):** 1250 câu đúng; 12 dạng đạt 90/90, D40 đúng 81/90 và D68 đúng 89/90.
Câu sai còn lại có cùng một kiểu: mô hình mở đầu bằng một Thought viết cả kế hoạch bằng chữ ("I need to follow the
solution method exactly...", có tính nhẩm và đoán luôn chữ cái đáp án), rồi mới viết lại một lượt Thought/Action; có câu
không gọi Calculator lần nào, có câu bỏ bước lưu phương án nên mọi `test_X` đều `False`. Thought đọc đề đứng riêng (không có Action)
là chỗ để mô hình kể trước các bước. Với D40 và D68, Thought đọc đề được ghép vào Thought đầu tiên và kết thúc bằng Action đầu tiên
(`MERGE_READING`); notebook chạy lại là `KLTN_R01_ReAct_Calculator.ipynb` (D40, D68), prompt ở `prompt_D40_v3.txt`, `prompt_D68_v3.txt`.
Kết quả H nằm ở `F:\Math\ReAct_Calculator_CD2\H_run2\`.

**Lần chạy R01 (D40, D68):** D68 đạt 90/90; D40 chỉ đúng 79/90. Ở D40, 25/90 phản hồi bắt đầu bằng lệnh của phương pháp (`shift = ...`)
thay vì lưu phương án trước, rồi lưu phương án SAU khi đã biết đáp án và dịch sai dấu ngoặc (ví dụ `[26;27)` thành `Interval(26, 27)`,
đưa `Interval.Ropen` vào phương án D). Nguyên nhân: ở bản R01 Thought đọc đề (nói về `shift`, `last_constant`) đứng trước lệnh lưu phương án A
nên mô hình đi tiếp bằng lệnh đầu tiên của phương pháp. Bản R02 (`KLTN_R02_ReAct_Calculator.ipynb`, chỉ D40, `prompt_D40_v4.txt`) đặt **bốn lệnh lưu
phương án lên đầu tiên**, Thought đọc đề nằm ở đầu Thought của lệnh `shift` đầu tiên (vẫn không có Thought nào thiếu Action).

**Bản R03 (D40, viết lại toàn bộ prompt):** chỉ cần hằng số cuối phương trình $c_0$ (vì luôn có $c_0=s-4$), nên phần Calculator còn bốn lệnh (`last_constant`, `lower_end`, `upper_end`, `answer`) sau bốn lệnh lưu phương án; hướng giải viết lại theo năm bước có chứng minh; `KLTN_R03_ReAct_Calculator.ipynb`, `prompt_D40_v5.txt`. Kết quả R03: 88/90; hai câu sai đều tính đúng nhưng hoán đổi phương án B và D lúc lưu (`[a;b]` thành `[a;b)`), do mô hình chép phương án theo mẫu của ví dụ. Bản R04 (`KLTN_R04_ReAct_Calculator.ipynb`, `prompt_D40_v6.txt`): mỗi phương án được chép đúng nguyên văn rồi gọi tên dấu ngoặc trái, phải (vuông hay tròn) trước khi viết `Interval...`.

## Chạy thử từng câu trước (bản 1 câu, chỉ có cho D79)

Cấu trúc y như các file `KLTN_Dxx_ReAct_Calculator_1cau.ipynb` của Số phức: Cell 1 → 3 nạp model (chạy **1 lần**),
Cell 4 chứa `DE_BAI` / `DAP_AN_DUNG` (chuỗi thô `r'''...'''`, các phương án nằm trên các dòng thật, không dùng `
`)
cùng prompt, backend và vòng lặp. Muốn thử câu khác: sửa `DE_BAI`, `DAP_AN_DUNG` rồi chạy lại **chỉ Cell 4**.
Câu mặc định là câu gốc `p204_q49` (đáp án D). Kết quả in ra: đáp án đúng/chọn, số token, số lượt gọi Calculator,
số lỗi cú pháp, nhật ký từng lượt gọi tool và toàn bộ lời giải; file đầy đủ ghi ở `/kaggle/working/full_response.txt`.
Một GPU là đủ (`tensor_parallel_size=1`); `MAX_MODEL_LEN=18432`, Cell 4 tự báo lỗi nếu prompt không còn đủ chỗ cho 9.216 token sinh.

## Chạy cả 90 câu trên Kaggle

1. Gắn Dataset chứa `plan_solve_prompts_mulogarit_merged.json` (cùng file đã dùng cho zero-shot) vào notebook.
   Notebook tự dò đường dẫn bằng `glob`.
2. Bật GPU (khuyến nghị 2×T4), "Run All". Kết quả: `/kaggle/working/d79_react_calculator_full90.csv`.
3. Muốn thử vài câu trong notebook này: đặt `RUN_STT = [1, 2, 3]` ở ô cấu hình (nhưng nên thử bằng bản 1 câu trước).

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

## Lỗi thường gặp trên Kaggle

- `RuntimeError: Detected that PyTorch and TorchAudio were compiled with different CUDA versions` khi chạy
  `from vllm import LLM, SamplingParams`: lệnh `pip install -U vllm` kéo PyTorch CUDA 13.0 còn `torchaudio` có sẵn của
  Kaggle là CUDA 12.8. Cell 2 đã gỡ `torchaudio` cùng `torchcodec` (`!pip uninstall -y -q torchcodec torchaudio`),
  nên `transformers` bỏ qua phần âm thanh. Nếu thấy lỗi này ở notebook cũ, thêm `torchaudio` vào lệnh uninstall rồi
  khởi động lại phiên (Restart session) trước khi chạy lại từ Cell 1.
