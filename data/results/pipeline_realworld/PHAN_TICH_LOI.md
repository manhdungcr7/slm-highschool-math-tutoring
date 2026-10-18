# Phân tích lỗi của pipeline trên 93 câu thực tế

Tài liệu ghi lại những gì quan sát được khi đọc kết quả lần chạy Kaggle ngày 2026-10-16 trên 93 câu
(phân dạng đúng 77/93, đáp án đúng 89/93). Mỗi mục tách ba phần: **quan sát** (có số liệu hoặc trích dẫn từ
kết quả), **suy luận** về nguyên nhân (chưa kiểm chứng) và **cách kiểm chứng** gợi ý. Các suy luận chưa được kiểm chứng
bằng thí nghiệm nào: chỉ có số liệu thống kê trên dữ liệu huấn luyện và đọc trực tiếp lời giải.

Mục tiêu nghiên cứu tiếp theo: tìm cách khắc phục từng vấn đề để toàn hệ thống đạt 100% từ đề bài đến đáp án.

## 0. Tóm tắt

| Câu hỏi | Trả lời ngắn |
|---|---|
| Vì sao phân dạng chưa đúng 100% (16/93 sai)? | Dữ liệu huấn luyện mỗi dạng chỉ gồm các biến thể số liệu của rất ít mẫu câu (trung vị 3 mẫu câu mỗi dạng). **Cả 16 câu sai đều có mẫu câu chưa từng xuất hiện trong dữ liệu huấn luyện của đúng dạng.** Khi mẫu câu đã có trong dữ liệu huấn luyện, bộ phân dạng đúng 17/17. Các dạng lân cận cùng mở đầu một cụm từ kéo bộ phân dạng sang dạng sai |
| Vì sao đáp án chưa đúng 100% (4/93 sai)? | Cả 4 câu sai đều là câu ReAct đã được phân đúng dạng. Hai nguyên nhân: (1) 3 câu có phương án không phải số ("Vô số"), prompt yêu cầu lưu mọi phương án vào Calculator như một số nên mô hình lặp lệnh lỗi đến hết 25 lượt gọi mà chưa tính gì; (2) 1 câu mô hình đọc sai hệ số khi áp phương pháp |
| Còn vấn đề nào nằm sau con số 95,7%? | Trong 35 câu ReAct có **8 câu (23%) kết thúc mà không có kết quả Calculator nào ủng hộ đáp án**: 4 sai và 4 đúng nhờ trả lời đoán. Nếu chỉ tính câu có bằng chứng, ReAct đạt 27/35 (77,1%) và không còn là 31/35 (88,6%) |

---

## 1. Phân dạng chưa đạt 100%

### 1.1 Quan sát về dữ liệu huấn luyện

- Dữ liệu huấn luyện bộ phân dạng có 12.780 cặp, tức 142 dạng × 90 biến thể. Biến thể chỉ thay số liệu của một mẫu câu gốc.
- Đếm số "mẫu câu" khác nhau trong mỗi dạng (che các chữ số, bỏ khoảng trắng và dấu LaTeX phụ, chỉ xét phần đề, không
  tính phương án): trung vị 3 mẫu câu mỗi dạng, nhiều nhất 80, ít nhất 1. **73/142 dạng có tối đa 3 mẫu câu.**
- Ví dụ các dạng chỉ có 1 mẫu câu: dạng 74 ("Tập xác định của hàm số $y=a^x$ là"), dạng 79 ("Tập xác định của hàm số
  $y=\log_a(x-c)$ là"), dạng 12 (đạo hàm $\ln(a+\sqrt{x+b})$), dạng 26, dạng 55, dạng 62.

### 1.2 Quan sát: các câu sai nằm ngoài mẫu câu đã huấn luyện

| | Số câu | Mẫu câu của đúng dạng đã có trong huấn luyện |
|---|---|---|
| Phân đúng | 77 | 17 câu |
| Phân sai | 16 | **0 câu** |

- Khi mẫu câu đã có trong huấn luyện: 17/17 đúng. Khi chưa có: 60/76 đúng (79%). Vậy bộ phân dạng **có tổng quát hóa** sang mẫu câu
  mới (60 câu đúng), nhưng sai ở khoảng 1/5 số câu như vậy.
- Độ giống về chữ (TF-IDF ký tự) giữa đề và các câu huấn luyện của đúng dạng: trung bình 0,47 với câu đúng, 0,25 với câu sai.

### 1.3 Các nhóm nguyên nhân quan sát được

Một câu có thể thuộc nhiều nhóm.

**Nhóm A. Cụm mở đầu giống dạng lân cận.** Với 63 câu từ web, 3 từ đầu của đề xuất hiện trong dữ liệu huấn luyện của đúng dạng
ở 18/47 câu đúng, nhưng chỉ ở 1/16 câu sai. Ở 6/16 câu sai, cụm mở đầu lại xuất hiện trong dữ liệu huấn luyện của **dạng bị đoán nhầm**:

| Câu | Đúng | Đoán | Cụm mở đầu |
|---|---|---|---|
| SRC-14 `y=(1/2)^x` | 74 (hàm mũ) | 3 (tập xác định hàm log bậc hai) | "Tìm tập xác định" |
| MOI-022 `y=e^{x²-2x}` | 74 | 3 | "Tìm tập xác định" |
| BS-009 `y=log(2x-x²)` | 3 | 37 | "Tập xác định" |
| MOI-035, MOI-036 (bất phương trình log) | 11 | 23, 38 (bất phương trình mũ, log thập phân) | "Tập nghiệm của" |
| BS-010 `9^{x+1}=27^{2x+1}` | 85 (phương trình mũ) | 33 (bất phương trình mũ) | "Tập nghiệm của" |

Suy luận: bộ phân dạng dựa nhiều vào cụm mở đầu của đề, trong khi điều phân biệt các dạng này nằm ở chỗ khác (loại hàm,
phương trình hay bất phương trình, dạng đối số).
Đây mới là một tín hiệu thống kê trên 16 câu, chưa phải bằng chứng nhân quả.

**Nhóm B. Cùng dạng nhưng đổi cách diễn đạt so với mẫu câu duy nhất trong huấn luyện.**

| Câu | Đúng | Đoán | Khác biệt so với huấn luyện của dạng đúng |
|---|---|---|---|
| THPT-010 `Giải phương trình 9^{x-1}=27^{x+2}` | 85 | 32 | Huấn luyện: "Nghiệm của phương trình $a^{px+q}=a^{rx+s}$ là" |
| BS-010 | 85 | 33 | Như trên: "Tập nghiệm của phương trình ... là" |
| THPT-008 `Tính đạo hàm của hàm số y=log₂(x²+1)` | 28 | 15 | Huấn luyện: "Hàm số $f(x)=\log_a(x^2+bx)$ có đạo hàm", dạng này không có hệ số tự do nào |
| WEB-019 "Có bao nhiêu giá trị nguyên của tham số m để phương trình ..." | 62 | 23 | Dạng 62 chỉ có mẫu câu "Gọi S là tập hợp tất cả các giá trị nguyên của m sao cho ..." |
| MOI-046 "Số phức z=-4+3i được biểu diễn bởi điểm M có tọa độ" | 106 | 99 | Huấn luyện: "Trên mặt phẳng tọa độ, điểm biểu diễn số phức z=... có tọa độ là" |
| BT-49 "Cho z₁=3+2i, z₂=3-2i. Phương trình bậc hai có hai nghiệm z₁, z₂ là" | 137 | 99 | Huấn luyện: "Phương trình nào dưới đây nhận hai số phức z=... và ... là nghiệm?" |

**Nhóm C. Trường hợp con của dạng chưa có trong huấn luyện.**

| Câu | Đúng | Đoán | Trường hợp con |
|---|---|---|---|
| MOI-036 | 11 | 38 | Dạng 11 trong huấn luyện chỉ có cơ số viết `\frac{a}{b}`. Đề viết cơ số `0,5`, tương đương nhưng khác cách viết |
| MOI-035 | 11 | 23 | Cơ số `e/3` (nhỏ hơn 1 nhưng không phải 1/2) |
| SRC-14, MOI-022 | 74 | 3 | Huấn luyện chỉ có $y=a^x$. Đề có $a=1/2$ dạng phân số và số mũ bậc hai $e^{x^2-2x}$ |
| MOI-042 `log₃(3-2x)` | 79 | 3 | Huấn luyện chỉ có $\log_a(x-c)$. Đề có đối số $c-kx$ |
| BS-011 `log₂(1+√x)` | 12 | 15 | Huấn luyện chỉ có $\ln(a+\sqrt{x+b})$. Đề dùng logarit cơ số 2 |
| SRC-23 `log_a(a²b)` | 26 | 75 | Dạng 26 chỉ có $\log_a(ab^k)$ |
| SRC-19 `log_{√a}b²+log_{a³}b⁶` | 55 | 15 | Dạng 55 chỉ có 1 mẫu câu, đề khác về dạng số mũ và cơ số |
| MOI-039 `(1+2i)²z + z̄ = 4i-20` | 120 | 116 | Huấn luyện dạng 120: $a(\bar z-i)-(b+ci)z=\dots$. Đề dùng bình phương số phức và không có nhóm $(\bar z - i)$ |

Suy luận: các dạng lân cận khác nhau ở một đặc điểm nhỏ (loại hàm, dạng đối số, cơ số) mà dữ liệu huấn luyện chưa đủ
đa dạng để bộ phân dạng học đặc điểm đó thay vì học cả mẫu câu.

**Giả thuyết đã loại:** ban đầu tôi nghĩ ba câu số phức (BT-49, MOI-039, MOI-046) sai vì dữ liệu huấn luyện dùng hệ số có
căn thức còn đề thực tế dùng số nguyên. Số liệu không ủng hộ: 50% câu huấn luyện số phức có căn thức, riêng dạng 106 và 137 chỉ có khoảng 1/3
câu có căn (32/90 và 30/90), nên dữ liệu huấn luyện có cả hai kiểu. Nguyên nhân của ba câu này là cách diễn đạt/cấu trúc (nhóm B, C), không phải kiểu số.

### 1.4 Độ tin cậy của bộ phân dạng không báo được lỗi

- Độ tin cậy trung bình: 0,89 với câu đúng, 0,74 với câu sai. Trong 16 câu sai có 6 câu có độ tin cậy từ 0,9 trở lên (ví dụ THPT-008: 1,00;
  SRC-14, MOI-022: 0,99).
- Dạng đúng nằm trong top 3 của bộ phân dạng chỉ ở **2/16** câu sai. Các lỗi này không phải "suýt đúng": xếp lại top 3 sẽ không cứu được.

### 1.5 Hậu quả của phân dạng sai trong lần chạy này

- 15/16 câu phân sai được giải bằng prompt zero-shot. Với 14 câu trong số đó, dạng đúng cũng là dạng zero-shot, nên dù phân sai,
  prompt vẫn **giống hệt** và kết quả không đổi. BT-49 là câu duy nhất có dạng đúng cần ReAct nhưng bị chuyển sang zero-shot, và vẫn đúng.
- Chỉ **MOI-039** bị dùng sai prompt ReAct (xem 2.3 mục e). Mức hại của phân dạng sai hiện nhỏ vì phần lớn dạng lẫn nhau cùng dùng prompt zero-shot chung.
  Khi mỗi dạng có prompt riêng tốt hơn, phân sai dạng mới thực sự làm mất đáp án.

### 1.6 Hướng khắc phục để kiểm chứng

1. **Thí nghiệm cắt bỏ (ablation):** chỉ đổi cụm mở đầu, hoặc chỉ đổi cách viết cơ số/đối số, giữ nguyên phần còn lại, rồi đo xem bộ phân dạng có đổi dự đoán không. Việc này kiểm chứng nhóm A, B, C.
2. **Dữ liệu huấn luyện đa dạng hơn:** mỗi dạng cần nhiều cách diễn đạt và nhiều trường hợp con. Chỉ cần đủ cho các dạng chỉ có 1 mẫu câu.
3. **Phân loại theo tầng:** chủ đề → họ hàm hoặc cấu trúc → dạng, để các dạng lân cận như 74/3/37/79 được phân biệt bằng đặc điểm chứ không bằng cụm mở đầu.
4. **Ngưỡng từ chối:** độ tin cậy hiện tại không hiệu chỉnh nên chưa dùng được để từ chối; cần một tín hiệu tốt hơn (ví dụ đồng thuận của nhiều lần chấm điểm).
5. **Kiểm tra sau định tuyến:** so đề với ví dụ trong prompt của dạng được chọn trước khi giải.

---

## 2. Đáp án mô hình chọn chưa đạt 100%

### 2.1 Bốn câu sai

| Câu | Dạng | Chuyện xảy ra |
|---|---|---|
| VD-012, VD-013, VD-014 | 69 | Mỗi câu có phương án "Vô số". Prompt yêu cầu "lưu bốn phương án dưới dạng số rồi so sánh". Mô hình lưu A, B rồi gặp `option_c = "Vô số"`: Calculator báo lỗi, mô hình gửi lại **đúng lệnh đó 23 đến 25 lần** đến hết 25 lượt, rồi bị ép trả lời và chọn D cả 3 lần. **Chưa tính bước nào của bài toán.** |
| VD-005 | 63 | Đề viết $4a^2$. Mô hình lấy hệ số $r=4$ thay vì $(2a)^2$ nên $r=2$, ra $a+2b=45/8$, cả bốn phép so sánh `False`, rồi vẫn chọn B |

Cả 4 đều đã được phân đúng dạng. Đáp án của họ do tôi tính lại độc lập bằng chương trình, nên khóa đáp án đáng tin.

### 2.2 Quan sát: đáp án đúng chưa chắc có căn cứ

Tôi đọc nhật ký Calculator của 35 câu ReAct và kiểm tra đáp án cuối có được một phép so sánh `True` của chính phương án đó ủng hộ không:

| | Số câu | Đúng |
|---|---|---|
| Có kết quả Calculator ủng hộ đáp án cuối | 27 | 27 |
| **Không có** (bị ép trả lời, hoặc đáp án mâu thuẫn với kết quả tính) | **8** | **4** |

Bốn câu đúng nhờ đoán:

| Câu | Dạng | Chuyện xảy ra |
|---|---|---|
| BS-004 | 137 | $a,b$ là ký hiệu chữ nên Calculator từ chối ("undefined name"). Mô hình gửi lệnh `a = a` **26 lần**, bị ép trả lời B (đúng) |
| BS-001 | 125 | Mô hình tìm cách dùng $K^2$ thay vì $|K|^2$ nên `solve` ra rỗng, rồi gửi lệnh dùng `z` chưa định nghĩa 18 lần, bị ép trả lời D (đúng) |
| MOI-039 | 120 | Dùng sai prompt D116, viết biểu thức có `z` chưa định nghĩa 16 lần, bị ép trả lời C (đúng) |
| WEB-087 | 133 | Công thức delta của phương pháp được viết cho dạng $z^2-2mz+\dots$, đề lại là $z^2-4z+(m-2)^2$. Calculator ra `count_total = 0`, cả bốn phép so sánh `False`, mô hình tự viết "đây là sai sót" rồi vẫn chọn C (đúng) |

- Tổng cộng 6 câu bị ép trả lời khi chạm giới hạn lượt gọi (3 đúng, 3 sai). Chữ cái chọn: D, D, D, D, B, C: **D chiếm 4/6**.
- Giả thuyết cần kiểm chứng: khi không có bằng chứng, mô hình thiên về phương án cuối, hoặc dựa vào kiến thức nhớ sẵn về các đề thi đã công bố. Không loại trừ khả năng câu thi thật nằm trong dữ liệu huấn luyện của Qwen3-4B.
- Theo nguồn: 10 câu ReAct từ web chỉ **6/10** có căn cứ, còn 25 câu từ đề chính thức có căn cứ **21/25**.

### 2.3 Các nguyên nhân quan sát được

**(a) Phương án không phải số.** Prompt dạy bước "lưu bốn phương án" bằng ví dụ toàn số và `Interval`. Trong 90 biến thể thử nghiệm của dạng này không có câu nào có phương án chữ, nên chưa từng phát hiện lỗi này.
Mô hình có nhận ra "Vô số" nghĩa là "infinite" nhưng không có cách nào lưu nó vào Calculator.

**(b) Phương pháp gắn cứng với mẫu câu.**
- BS-001: phương pháp giả định $w(|z|-i)=K/z$. Đề thật có $+1-3i$, tức dấu khác. Mô hình **phát hiện sự lệch** ("These do not match") nhưng prompt không có nhánh xử lý, nên nó bắt đầu lại và rơi vào vòng lặp lỗi.
- WEB-087: công thức delta gắn với vị trí tham số $m$ trong dạng gốc.
- VD-005: đề viết $4a^2$ thay vì $(2a)^2$ như các biến thể; dạng 63 gồm 3 câu thì 2 câu đúng, 1 câu đọc sai hệ số.
- BS-004: phương pháp chỉ cho phép ẩn tự do đã khai báo trước (ở đây là `z`); không có cách xử lý biểu thức chữ $a, b$.

**(c) Không phục hồi sau lỗi.** 5 câu gửi lại đúng một lệnh lỗi từ 16 đến 26 lần (BS-004: 26 lần, VD-014: 25, VD-012 và VD-013: 23, MOI-039: 16), còn BS-001 luân phiên hai lệnh lỗi. Ở bản Calculator Mũ–Logarit, thông báo lỗi ghi rõ "Do not send it again unchanged" nhưng mô hình vẫn lặp lại.
Bản Calculator của Số phức không có nhắc lặp lỗi, và thông báo lỗi lẫn tiếng Việt không dấu giữa prompt tiếng Anh ("(chua co bien nao)", "(khong co)"). Sau khi chạm giới hạn, mô hình bị ép trả lời (xem 2.2).

**(d) Không có quy trình khi mọi phép kiểm tra đều `False`.** VD-005 và WEB-087 đều gặp tình huống này; prompt không nói "hãy kiểm tra lại cách đọc đề", nên mô hình tự chọn một chữ cái.

**(e) Dùng sai prompt trong cùng chế độ ReAct (MOI-039).** Prompt D116 mô tả phương trình chỉ có $z$, không có $\bar z$. Mô hình đã bỏ qua phương pháp, viết `conjugate(z)` với `z` chưa là biến, và lặp lại.
Đây là trường hợp duy nhất mà phân sai dạng trực tiếp làm hỏng quá trình giải.

**(f) Phương pháp lập trình sẵn thành công khi số liệu đổi nhưng cấu trúc giữ nguyên.** 21/25 câu ReAct từ đề chính thức có căn cứ. VD-019 đến VD-021 đi đúng 30 lượt,
dựng đa thức bậc 4 $t^4-10t^3+9t^2+4t-4$ của riêng đề, tìm nghiệm bằng `nroots` và đếm. Điều này cho thấy prompt tổng quát hóa qua số liệu, **không** chứng minh mô hình lập luận tổng quát.

### 2.4 Zero-shot: 58/58 đúng, nhưng

- 12/58 câu dùng hơn 3000 token, 3 câu hơn 5000 token; dài nhất 7587 trên ngân sách 9216 token (82%). Nếu một câu tương tự dài hơn ngân sách, đáp án sẽ không được trích ra.
- **BS-011** (dạng 12) là câu ví dụ rõ nhất: phần suy nghĩ dài 21.567 ký tự, 95 lần do dự ("Wait", "Hmm", ...). Mô hình tính đúng đạo hàm $\frac{1}{2\sqrt{x}(1+\sqrt{x})\ln 2}$ nhưng **chép sai phương án A** thành $\frac{1}{2\sqrt{x}(1+\sqrt{x})\ln 2}$ (đề ghi $\frac{\ln 2}{2\sqrt{x}(1+\sqrt{x})}$),
  nên khẳng định "ra A", rồi tự mâu thuẫn, rồi mới nhận ra $\ln 4 = 2\ln 2$ và chọn D. Ở lần chạy trước **cùng câu này** mô hình chọn A và sai. Với cùng prompt và seed, kết quả không lặp lại vì thành phần batch thay đổi.
  Đây chính là lỗi "chép sai phương án" mà bước lưu phương án trong ReAct được thiết kế để tránh.
- Phần suy nghĩ của mô hình ở các câu đã đọc đều bằng tiếng Anh dù prompt yêu cầu giải bằng tiếng Việt; chỉ lời giải cuối bằng tiếng Việt.

### 2.5 Hướng khắc phục để kiểm chứng

1. **Phương án không phải số:** sửa quy tắc lưu phương án (đánh dấu phương án chữ, so sánh theo nhãn) hoặc bỏ qua phương án chữ; đo lại trên các dạng có nhóm phương án đặc biệt ("Vô số", "Không có giá trị nào").
2. **Bộ ngắt vòng lặp:** nếu một lệnh lỗi bị gửi lại quá 2 lần, đưa ra hướng dẫn khác hoặc chuyển sang chế độ khác.
3. **Đường dự phòng:** khi ReAct không có kết quả ủng hộ (chạm giới hạn, mọi phép so sánh `False`, lỗi lặp), quay về zero-shot hoặc chạy lại bằng prompt khác.
   Trong lần chạy này, đáp án zero-shot sẽ phát hiện và có thể sửa các câu ReAct không có căn cứ, nhưng cần đo lại.
4. **Không tính đáp án đoán là đáp án đúng:** báo cáo riêng "đúng có căn cứ" và "đúng do đoán".
5. **Kiểm tra đồng thuận:** so đáp án ReAct và zero-shot; hai chế độ bất đồng là dấu hiệu cần xem lại.
6. **Prompt theo trường hợp con:** thêm các biến thể cấu trúc (đổi dấu, tham số ở vị trí khác, biến chữ) vào dữ liệu thử nghiệm của mỗi dạng ReAct để phát hiện sớm (BS-001, WEB-087, BS-004).

---

## 3. Giới hạn của phân tích này

- Một lần chạy duy nhất; câu zero-shot có thể đổi kết quả giữa các lần chạy (BS-011).
- Cỡ mẫu nhỏ: 93 câu; ReAct chỉ 35 câu, trong đó web 10 câu.
- Nhãn dạng đúng do tôi gán và rà soát thủ công (xem `ra_soat_nhan_dang_23_cau_phan_sai.csv`); đã bỏ 7 câu nhãn không chắc.
- Các nhóm nguyên nhân ở mục 1.3 là suy luận từ so sánh với dữ liệu huấn luyện và cụm mở đầu, chưa có thí nghiệm cắt bỏ.
- Tôi đọc kỹ lời giải của các câu sai và các câu ReAct có bất thường; các câu zero-shot đúng còn lại được duyệt qua độ dài, số lần do dự và phần kết, chưa đọc từng bước.
- 30 câu đề chính thức cùng họ với các dạng của danh mục, nên kết quả tốt trên nhóm này không nói về dạng bài hoàn toàn mới.

## Phụ lục. 16 câu phân sai dạng

| Câu | Đúng | Đoán | Độ tin cậy | Nhóm |
|---|---|---|---|---|
| BT-49 | 137 | 99 | 0,42 | B |
| SRC-14 | 74 | 3 | 0,99 | A, C |
| SRC-19 | 55 | 15 | 0,35 | C |
| SRC-23 | 26 | 75 | 0,89 | C |
| WEB-019 | 62 | 23 | 0,91 | B |
| THPT-008 | 28 | 15 | 1,00 | B, C |
| THPT-010 | 85 | 32 | 0,69 | B |
| MOI-022 | 74 | 3 | 0,99 | A, C |
| MOI-035 | 11 | 23 | 0,91 | A, C |
| MOI-036 | 11 | 38 | 0,45 | A, C |
| MOI-039 | 120 | 116 | 0,89 | C |
| MOI-042 | 79 | 3 | 0,65 | C |
| MOI-046 | 106 | 99 | 0,60 | B |
| BS-009 | 3 | 37 | 0,36 | A |
| BS-010 | 85 | 33 | 0,79 | A, B |
| BS-011 | 12 | 15 | 0,97 | C |
