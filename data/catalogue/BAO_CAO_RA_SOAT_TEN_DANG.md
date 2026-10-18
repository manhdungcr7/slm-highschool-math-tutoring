# Rà soát tên và cách gọi tên các dạng bài (142 dạng)

Người đọc: nhóm làm đề tài, trước khi dùng danh mục này làm đầu vào cho bộ định tuyến dạng bài.

## 1. Cách gọi tên mới

Mỗi dạng được gọi bằng một số thứ tự chung cho cả hai chủ đề: **Dạng 1, Dạng 2, …, Dạng 142**, viết đầy đủ chữ 'Dạng', không dùng chữ cái a, b hay tiền tố.

| Chủ đề | Các dạng | Số dạng |
|---|---|---|
| Mũ-Logarit | Dạng 1 đến Dạng 88 | 88 |
| Số phức | Dạng 89 đến Dạng 142 | 54 |

Số thứ tự đi theo thứ tự mã cũ trong từng chủ đề. Hai dạng cũ D36a, D36b (và D50a, D50b) trở thành hai số riêng liền nhau. Cột `ma_cu` trong file CSV cho biết mã cũ tương ứng, để nối với các file prompt và kết quả đã có (ví dụ `prompt_D40.txt`). Mã cũ không xuất hiện trong văn bản mô hình đọc.

## 2. Kết quả kiểm tra

| Kiểm tra | Kết quả |
|---|---|
| Số dạng | 142 (Mũ-Logarit 88, Số phức 54) |
| Mã cũ trùng giữa hai chủ đề | D01 đến D54 có ở cả hai chủ đề (54 mã trùng, ví dụ D01 vừa là 'tìm đồng thời phần thực và phần ảo' vừa là 'giải phương trình lôgarit cơ bản'). Cách gọi 'Dạng 1 … Dạng 142' không còn trùng. |
| Tên dạng trùng nhau | Không có hai mô tả giống hệt. Sau khi bỏ dấu cách, dấu câu và chữ hoa (giữ lại ký hiệu < > và các từ 'lớn hơn', 'nhỏ hơn') vẫn không có hai mô tả trùng. |
| Dấu hiệu nhận dạng khớp với 12951 đề (8026 Mũ-Logarit, 4925 Số phức, gồm 171 câu gốc) | Mỗi đề khớp đúng một dấu hiệu, là dấu hiệu của chính dạng của nó: **12951/12951**. Không có đề nào khớp dấu hiệu của dạng khác. |
| Chi tiết mà mô tả nêu nhưng câu dẫn không thấy (nằm ở phương án hoặc là hằng số) | 18 kiểm chứng, đều đạt trên mọi biến thể của dạng đó. |
| Mô tả đã đổi | 142/142: 28 mô tả cũ sai so với đề, 22 nhập nhằng, 92 diễn đạt lại; 0 giữ nguyên. |
| Từ viết tắt trong mô tả | Đã viết đầy đủ (GTNN, GTLN thành giá trị nhỏ nhất, giá trị lớn nhất). |

Dấu hiệu nhận dạng là biểu thức chính quy viết cho từng dạng, tìm trên câu dẫn của đề (đã bỏ khoảng trắng và dấu $). Nó là bằng chứng cho hai điều: mô tả đúng với mọi đề của dạng, và hai dạng khác nhau không có đề nào chung đặc điểm nhận dạng.

**Nguyên tắc viết mô tả mới.** Bộ định tuyến chỉ nhìn thấy đề bài, nên mô tả nói cái nhìn thấy trong đề: cho gì (dạng biểu thức, điều kiện) và hỏi gì (đại lượng cần tìm). Mô tả cũ nhiều chỗ nói cách giải ('bằng đổi cơ số', 'qua ẩn phụ', 'bằng hàm đặc trưng', 'bằng bất đẳng thức Cô-si'); cách giải không hiện trong đề nên không giúp nhận dạng. Mô tả viết bằng lời, không dùng chữ thay thế như p, q, k; để prompt ngắn, mô tả đứng một mình, không kèm đề ví dụ. Một đề ví dụ thật (đề ngắn nhất của dạng) vẫn được lưu ở cột `vi_du` trong file CSV và JSON để tham khảo.

## 3. Mô tả cũ sai so với đề (đã sửa)

| Dạng | Mã cũ | Mô tả cũ | Vấn đề (đối chiếu với dữ liệu) | Mô tả mới |
|---|---|---|---|---|
| Dạng 5 | ML_D06 | Nhận biết công thức đổi cơ số lôgarit | Tên cũ ghi 'công thức đổi cơ số'. Đề là log_{a^k}(ab) nằm trong các phương án, k thay đổi. | Cho hai số thực dương a, b với a khác 1, chọn đẳng thức đúng cho lôgarit có cơ số là một lũy thừa của a và biểu thức là tích a nhân b. Đề chỉ nêu điều kiện của a, b; các đẳng thức nằm trong bốn phương án. |
| Dạng 8 | ML_D10 | Tìm tham số để hàm số chứa lôgarit tự nhiên đơn điệu trên R | Tên cũ chung chung. Đề là y = ln(x² + k) − mx + 1, k thay đổi theo biến thể (1, 4, 9, 16, …). | Tìm các giá trị của tham số m để hàm số y bằng ln của (x bình phương cộng một số) trừ m nhân x cộng 1 đồng biến trên toàn bộ trục số. |
| Dạng 10 | ML_D13 | Rút gọn biểu thức lôgarit chứa tích, thương và lũy thừa | Tên cũ ghi 'rút gọn biểu thức'. Đề không ghi biểu thức; log_p(q·a^k/b) nằm trong các phương án và p, q, k thay đổi. | Cho hai số thực dương a, b, chọn đẳng thức đúng khi khai triển lôgarit của một biểu thức có tích, thương và lũy thừa của a, b. Biểu thức cần khai triển chỉ xuất hiện trong bốn phương án. |
| Dạng 11 | ML_D14 | Giải bất phương trình lôgarit cơ số nhỏ hơn 1 | Tên cũ ghi 'cơ số nhỏ hơn 1'. Cả 91 câu đều có cơ số 1/2 và hai vế đều là lôgarit. | Giải bất phương trình lôgarit cơ số một phần hai, trong đó hai vế đều là lôgarit của một biểu thức bậc nhất theo x. |
| Dạng 16 | ML_D19 | Giải bất phương trình mũ cơ bản dạng a^f(x)>a^k | Tên cũ ghi 'a^f(x) > a^k'. Đề có dạng a^{f(x)} − a^k > 0 (có phép trừ, so với 0). | Giải bất phương trình mũ có dạng: một lũy thừa có số mũ bậc nhất theo x, trừ đi một lũy thừa hằng số, lớn hơn 0. |
| Dạng 19 | ML_D22 | Tính giá trị biểu thức lôgarit phức hợp qua một lôgarit cho trước | Tên cũ chung chung. Đề là log_a b = k (k là số hoặc căn), tính log_{√b/a} √(b/a). | Cho lôgarit cơ số a của b bằng một số (a, b dương, a khác 1 và khác căn b), tính lôgarit cơ số (căn b chia a) của căn bậc hai của (b chia a). |
| Dạng 23 | ML_D27 | Giải bất phương trình mũ cùng cơ số dạng a^f(x)<a^g(x) | Tên cũ ghi 'a^f(x) < a^g(x)'. Có câu gốc có vế phải chỉ là số (2^{x+1} < 4). | Giải bất phương trình mũ có hai vế là hai lũy thừa cùng cơ số, số mũ bậc nhất theo x hoặc là hằng số, dấu nhỏ hơn. |
| Dạng 33 | ML_D38 | Giải bất phương trình mũ cùng cơ số, hai vế là tam thức bậc hai | Tên cũ ghi 'hai vế là tam thức bậc hai'. Thực tế chỉ vế phải bậc hai; vế trái bậc nhất hoặc hằng (2^5 ≥ 2^{x²+2x}). | Giải bất phương trình mũ có số mũ vế trái bậc nhất theo x (hoặc là hằng số), số mũ vế phải là tam thức bậc hai theo x, dấu lớn hơn hoặc bằng. |
| Dạng 38 | ML_D43 | Giải bất phương trình lôgarit cơ bản (lôgarit thập phân) | Tên cũ ghi 'lôgarit cơ bản (lôgarit thập phân)'. Thực tế là log x ≥ k, k có thể âm hoặc phân số. | Giải bất phương trình lôgarit thập phân: log x lớn hơn hoặc bằng một số (không ghi cơ số, biểu thức bên trong chỉ là x, số có thể âm hoặc là phân số). |
| Dạng 41 | ML_D46 | Tìm giá trị nhỏ nhất của biểu thức mũ-lôgarit qua ẩn phụ t=log_a b | Tên cũ nêu cách giải ('ẩn phụ t = log_a b'). Đề là a^x = b^y = (ab)^{1/k}, P = x + m·y; hệ số của y và k thay đổi. | Cho a, b lớn hơn 1 và a mũ x bằng b mũ y bằng (a nhân b) mũ một phần số nào đó, tìm tập chứa giá trị nhỏ nhất của x cộng một hệ số nhân y. |
| Dạng 49 | ML_D53 | Giải bất phương trình lôgarit cơ bản dạng log_a(f(x))>k | Tên cũ ghi 'log_a(f(x)) > k, cơ số a'. Có câu gốc viết log(x−2) > 0 không ghi cơ số. | Giải bất phương trình lôgarit: lôgarit của một biểu thức bậc nhất theo x lớn hơn một số (có ghi cơ số, hoặc là lôgarit thập phân), dấu lớn hơn. |
| Dạng 52 | ML_D56 | Đếm số nguyên thỏa bất phương trình lôgarit hai cơ số khác nhau | Tên cũ chung chung. Hai cơ số, x² − c và hai mẫu số đều thay đổi. | Đếm số nguyên x thỏa bất phương trình giữa hai lôgarit khác cơ số của hai phân thức cùng có tử số là x bình phương trừ một số. |
| Dạng 60 | ML_D65 | Tìm giá trị nhỏ nhất của biểu thức hai biến từ phương trình lôgarit bằng hàm đặc trưng | Tên cũ nêu cách giải ('hàm đặc trưng'). Mọi hệ số của phương trình đều thay đổi theo biến thể. | Cho phương trình có lôgarit của một phân thức theo x, y bằng một biểu thức theo x, y; tìm giá trị nhỏ nhất của x cộng y. |
| Dạng 63 | ML_D68 | Tìm giá trị biểu thức từ hệ hai đẳng thức lôgarit-mũ bằng bất đẳng thức Cô-si | Tên cũ nêu cách giải ('bất đẳng thức Cô-si'). Mọi hệ số trong hai lôgarit đều thay đổi theo biến thể. | Cho hệ thức có hai lôgarit của các biểu thức bậc hai theo a, b cộng nhau bằng 2, tính a cộng 2 nhân b. |
| Dạng 69 | ML_D75 | Đếm giá trị nguyên dương tham số để phương trình tích (lôgarit bậc hai và căn chứa tham số) có nghiệm | Tên cũ chung chung. Biểu thức √(c^x − m) có c là số nguyên hoặc phân số; 89/91 câu dùng phân số. | Cho phương trình tích của một biểu thức bậc hai theo lôgarit cơ số 2 của x với căn bậc hai của (một hàm mũ trừ m) bằng 0, đếm số giá trị nguyên dương của m để phương trình có đúng hai nghiệm phân biệt. |
| Dạng 73 | ML_D79 | Đếm số nguyên một biến sao cho số giá trị nguyên biến kia thỏa bất phương trình lôgarit không vượt một ngưỡng | Tên cũ chung chung. Hai cơ số lôgarit và ngưỡng k thay đổi. | Đếm số nguyên x sao cho với mỗi x có không quá một số lượng cho trước các số nguyên y thỏa bất phương trình giữa hai lôgarit. |
| Dạng 82 | ML_D88 | Đếm số nguyên thỏa bất phương trình tích (lôgarit và mũ) nhỏ hơn hoặc bằng 0 | Tên cũ chung chung. Các cơ số, hằng số trong tích thay đổi theo biến thể. | Đếm số nguyên x thỏa bất phương trình tích của (hiệu hai lôgarit) và (một số trừ một lũy thừa) lớn hơn hoặc bằng 0. |
| Dạng 87 | ML_D93 | Đếm số nguyên dương tham số sao cho có đúng k giá trị nguyên biến kia thỏa bất phương trình tích | Tên cũ chung chung. Bất phương trình (p^b − p)(a·q^b − r) < 0 có p, q, r thay đổi. | Đếm số nguyên dương a sao cho với mỗi a có đúng ba số nguyên b thỏa bất phương trình tích hai thừa số chứa hàm mũ nhỏ hơn 0. |
| Dạng 88 | ML_D94 | Tìm giá trị lớn nhất của biểu thức hai biến từ điều kiện đúng với mọi tham số bằng bất đẳng thức Cauchy-Schwarz | Tên cũ chung chung. Biểu thức P = x² + y² + px + qy, p và q thay đổi. | Cho một bất đẳng thức có lũy thừa của a đúng với mọi a dương, tìm giá trị lớn nhất của biểu thức bậc hai theo x và y. |
| Dạng 95 | SP_D07 | Cho hai số phức, tìm phần thực hoặc phần ảo của tích của chúng | Tên cũ ghi 'phần thực hoặc phần ảo của tích'. Cả 91 câu đều hỏi phần ảo của z₁z₂. | Cho hai số phức z1, z2, tìm phần ảo của tích z1 nhân z2. |
| Dạng 96 | SP_D08 | Cho số phức z, tìm phần thực hoặc phần ảo của bình phương z² | Tên cũ ghi 'phần thực hoặc phần ảo của z²'. Cả 91 câu đều hỏi phần thực của z². | Cho số phức z = a + bi, tìm phần thực của z bình phương. |
| Dạng 98 | SP_D10 | Cho một số số phức, nhận biết số nào là số thuần ảo | Tên cũ ghi 'Cho một số số phức'. Đề không cho số phức nào, chỉ hỏi 'Số phức nào dưới đây là số thuần ảo?'. | Chọn trong bốn phương án số phức nào là số thuần ảo (đề không cho sẵn số phức nào, chỉ hỏi 'Số phức nào dưới đây là số thuần ảo?'). |
| Dạng 100 | SP_D12 | Cho số phức dưới dạng biểu thức, tìm số phức liên hợp z̄ | Tên cũ ghi 'dưới dạng biểu thức'. Cả 91 câu đều có z = i(a+bi). | Cho số phức z là tích của i với một số phức (ví dụ z = i nhân (5 trừ 4i)), tìm số phức liên hợp của z. |
| Dạng 102 | SP_D14 | Cho hai số phức, tính môđun của tổng / hiệu của chúng | Tên cũ ghi 'tổng / hiệu'. Cả 91 câu đều là môđun của tổng z₁+z₂, không có câu nào về hiệu. | Cho hai số phức z1, z2, tính môđun của tổng z1 cộng z2. |
| Dạng 109 | SP_D21 | Tìm điểm biểu diễn của một tổ hợp tuyến tính hai số phức (vd 2z₁+z₂) | Tên cũ ghi 'tổ hợp tuyến tính (vd 2z₁+z₂)'. Cả 91 câu đều đúng là 2z₁+z₂. | Cho hai số phức z1, z2, tìm tọa độ điểm biểu diễn của số phức 2 nhân z1 cộng z2. |
| Dạng 115 | SP_D27 | Cho số phức z, tính một biểu thức phối hợp nhiều phép toán theo z | Tên cũ ghi 'biểu thức phối hợp nhiều phép toán'. Cả 91 câu đều là w = iz + z̄. | Cho số phức z = a + bi, tính số phức w = i nhân z cộng số phức liên hợp của z. |
| Dạng 117 | SP_D29 | Giải phương trình bậc nhất ẩn z (chỉ chứa z hoặc z̄), tìm phần thực hoặc phần ảo của z | Tên cũ ghi 'phần thực hoặc phần ảo'. Cả 91 câu đều hỏi phần ảo, phương trình luôn là i·z̄ = c. | Cho phương trình i nhân số phức liên hợp của z bằng một số phức (chỉ chứa số phức liên hợp của z), tìm phần ảo của z. |
| Dạng 128 | SP_D40 | Cho điều kiện |z−z₀|=R, tìm tập hợp điểm biểu diễn z (đường tròn) | Tên cũ không nói đề hỏi gì. Cả 91 câu đều hỏi tọa độ tâm đường tròn. | Cho môđun của (z trừ một số phức) bằng một số, tập hợp điểm biểu diễn z là một đường tròn; tìm tọa độ tâm của đường tròn. |

## 4. Mô tả cũ đúng nhưng nhập nhằng với dạng khác (đã sửa)

| Dạng | Mã cũ | Mô tả cũ | Lý do | Mô tả mới |
|---|---|---|---|---|
| Dạng 9 | ML_D12 | Giải phương trình mũ cơ bản dạng a^f(x)=a^k | Tên cũ của Dạng 9 và Dạng 85 gần như giống nhau (a^f(x)=a^k và a^f(x)=a^g(x)). Khác biệt thật: vế phải của Dạng 9 luôn là số nguyên (94/94), của Dạng 85 luôn là lũy thừa (91/91). | Giải phương trình mũ có số mũ là biểu thức bậc nhất theo x và vế phải là một số nguyên viết bình thường (không viết dưới dạng lũy thừa). |
| Dạng 17 | ML_D20 | Tính giá trị lôgarit có cơ số và biểu thức đều là lũy thừa của một số | Dạng 17 và Dạng 75 đều là lôgarit có căn của a, khác nhau ở chỗ căn nằm ở cơ số (Dạng 17) hay ở đối số (Dạng 75). | Cho a dương khác 1 và P là lôgarit cơ số căn bậc n của a, của a lũy thừa m; chọn mệnh đề đúng về giá trị của P. |
| Dạng 27 | ML_D33 | Giải bất phương trình mũ cùng cơ số, số mũ là tam thức bậc hai | Bốn dạng bất phương trình mũ cùng cơ số (Dạng 16, Dạng 23, Dạng 27, Dạng 33) có tên gần giống nhau; tên mới nêu số mũ ở từng vế và chiều bất đẳng thức. | Giải bất phương trình mũ có số mũ ở vế trái là tam thức bậc hai theo x, vế phải là một lũy thừa hằng số hoặc một số, dấu nhỏ hơn. |
| Dạng 30 | ML_D36a | Nhận biết mệnh đề đúng về lôgarit của lũy thừa | Dạng 30 và Dạng 31 cùng bài học log(a^k) = k·log a; khác ở cách hỏi (chọn đẳng thức đúng / log_c(a^k) bằng). | Cho a dương, chọn đẳng thức đúng trong bốn phương án, mỗi phương án là đẳng thức giữa lôgarit thập phân của a lũy thừa một số hoặc của một số nhân a. |
| Dạng 31 | ML_D36b | Tính lôgarit của lũy thừa bằng quy tắc đưa số mũ ra trước | Xem Dạng 30. | Cho a dương, tính lôgarit của a lũy thừa một số theo lôgarit của a; đề hỏi 'lôgarit của a lũy thừa đó bằng' và các phương án là biểu thức theo lôgarit của a. |
| Dạng 37 | ML_D42 | Tìm tập xác định hàm số lôgarit cơ bản y=log_a x | Dạng 37, Dạng 79, Dạng 56, Dạng 3 đều là tập xác định hàm lôgarit; tên mới nêu rõ đối số. | Tìm tập xác định của hàm số y bằng lôgarit cơ số a của x, biểu thức bên trong lôgarit chỉ là x. |
| Dạng 43 | ML_D48 | Giải bất phương trình mũ dạng a^x>c (c không là lũy thừa nguyên của a) | Dạng 43 và Dạng 76 chỉ khác chiều bất đẳng thức; đã thêm chữ LỚN HƠN / NHỎ HƠN để khác biệt nằm trong từ chứ không chỉ trong ký hiệu. | Giải bất phương trình mũ a mũ x LỚN HƠN c, trong đó c không là lũy thừa nguyên của a (đáp án chứa lôgarit). |
| Dạng 76 | ML_D82 | Giải bất phương trình mũ dạng a^x<c (c không là lũy thừa nguyên của a) | Xem Dạng 43. | Giải bất phương trình mũ a mũ x NHỎ HƠN c, trong đó c không là lũy thừa nguyên của a (đáp án chứa lôgarit). |
| Dạng 79 | ML_D85 | Tìm tập xác định hàm số lôgarit dạng log_a(x-c) | Xem Dạng 37. | Tìm tập xác định của hàm số y bằng lôgarit cơ số a của (x trừ một số). |
| Dạng 85 | ML_D91 | Giải phương trình mũ cùng cơ số dạng a^f(x)=a^g(x) | Xem Dạng 9. | Giải phương trình mũ có hai vế đều viết dưới dạng lũy thừa của cùng một cơ số, ví dụ 3 mũ (2x cộng 1) bằng 3 mũ (2 trừ x); có thể một vế là lũy thừa hằng số. |
| Dạng 93 | SP_D05 | Cho hai số phức z1, z2, tìm phần thực của tổng z1+z2 | Gần Dạng 112: cùng hai số phức z₁, z₂ và tổng. Dạng 93 hỏi phần thực của tổng, Dạng 112 hỏi chính tổng. | Cho hai số phức z1, z2, tìm phần thực của tổng z1 cộng z2. |
| Dạng 112 | SP_D24 | Cho hai số phức, tìm tổng của chúng | Tên cũ 'tìm tổng của chúng' gần Dạng 93 và Dạng 113; đáp án của Dạng 112 là một số phức. | Cho hai số phức, tính tổng của chúng; đáp án là một số phức (không hỏi phần thực hay môđun). |
| Dạng 116 | SP_D28 | Giải phương trình bậc nhất ẩn z (chỉ chứa z hoặc z̄), tính môđun |z| | Tên cũ của Dạng 116, Dạng 117, Dạng 118 đều chứa cụm 'chỉ chứa z hoặc z̄' nên không tách được chúng; Dạng 116 và Dạng 118 chứa z, Dạng 117 chứa z̄. | Cho phương trình chỉ chứa z (không có số phức liên hợp): z nhân một số phức, cộng một số thuần ảo, bằng một số thực; tính môđun của z. |
| Dạng 118 | SP_D30 | Giải phương trình bậc nhất ẩn z (chỉ chứa z hoặc z̄), tìm số phức liên hợp z̄ | Xem Dạng 116. | Cho phương trình i nhân z bằng một số phức (chỉ chứa z), tìm số phức liên hợp của z. |
| Dạng 125 | SP_D37 | Cho phương trình chứa |z| ở nhiều vị trí, đặt t=|z| và lấy môđun hai vế để xác định khoảng chứa |z| | Tên cũ của Dạng 125 và Dạng 126 chỉ khác vế cuối và nêu cách giải ('đặt t=|z|…') không hiện trong đề. | Cho phương trình có môđun của z ở nhiều vị trí: (một số phức) nhân môđun của z bằng (một số chia z) cộng một số phức; chọn mệnh đề đúng về khoảng chứa môđun của z. |
| Dạng 126 | SP_D38 | Cho phương trình chứa |z| ở nhiều vị trí, đặt t=|z| và lấy môđun hai vế để đếm số số phức z | Xem Dạng 125. | Đếm số số phức z thỏa phương trình: môđun của z nhân (z trừ một số phức), cộng một số thuần ảo, bằng (một số phức) nhân z. |
| Dạng 127 | SP_D39 | Cho hai điều kiện về môđun và liên hợp, đếm số số phức z thỏa mãn | Tên cũ 'hai điều kiện về môđun và liên hợp' quá chung. | Đếm số số phức z thỏa đồng thời: môđun của z bình phương bằng hệ số nhân môđun của (z trừ liên hợp của z), và môđun của tích (z trừ một số)(liên hợp của z trừ số đó nhân i) bằng bình phương môđun của (z cộng số đó nhân i). |
| Dạng 129 | SP_D41 | Cho một tích là số thuần ảo, tìm TÂM của đường tròn tập hợp điểm biểu diễn z | Tên cũ của Dạng 129 và Dạng 130 chỉ khác TÂM / BÁN KÍNH; đã thêm dạng tích để nhìn thấy khác biệt thứ hai. | Cho tích (z trừ một số thuần ảo) nhân (liên hợp của z trừ một số thực) là số thuần ảo; tìm tọa độ TÂM của đường tròn tập hợp điểm biểu diễn z. |
| Dạng 130 | SP_D42 | Cho một tích là số thuần ảo, tìm BÁN KÍNH của đường tròn tập hợp điểm biểu diễn z | Xem Dạng 129. | Cho tích (liên hợp của z trừ một số thuần ảo) nhân (z trừ một số thực) là số thuần ảo; tìm BÁN KÍNH của đường tròn tập hợp điểm biểu diễn z. |
| Dạng 133 | SP_D45 | Cho phương trình bậc hai một tham số m, đếm số giá trị m để hai nghiệm có môđun bằng nhau | Tên cũ của Dạng 133, Dạng 134, Dạng 135 cùng bắt đầu bằng 'Cho phương trình bậc hai một tham số m, đếm số giá trị m để …'. | Cho phương trình bậc hai z bình phương trừ 2m nhân z cộng (một hệ số nhân m cộng một số) bằng 0 với m thực; đếm số giá trị nguyên của m để phương trình có hai nghiệm phân biệt z1, z2 thỏa môđun của z1 bằng môđun của z2. |
| Dạng 134 | SP_D46 | Cho phương trình bậc hai một tham số m, đếm số giá trị m để tổng môđun hai nghiệm bằng S | Xem Dạng 133. | Cho phương trình bậc hai z bình phương trừ 2 nhân (m cộng một số) nhân z cộng m bình phương bằng 0 với m thực; đếm số giá trị của m để phương trình có hai nghiệm phân biệt z1, z2 thỏa tổng môđun của z1 và môđun của z2 bằng một số. |
| Dạng 135 | SP_D47 | Cho phương trình bậc hai một tham số m, đếm số giá trị m để tồn tại nghiệm z₀ có môđun R | Xem Dạng 133. | Cho phương trình bậc hai z bình phương trừ 2 nhân (m cộng một số) nhân z cộng m bình phương bằng 0 với m thực; đếm số giá trị của m để phương trình có một nghiệm z0 thỏa môđun của z0 bằng một số. |

## 5. Các cặp dạng dễ nhầm và điểm phân biệt

Điểm phân biệt của mỗi cặp đã ghi ngay trong mô tả, không cần xem đề.

| Dạng | Dễ nhầm với | Điểm phân biệt |
|---|---|---|
| Dạng 1 | Dạng 18 | Dạng 18 có tổng hai lôgarit |
| Dạng 1 | Dạng 65 | Dạng 65 có lôgarit ở cả hai vế |
| Dạng 1 | Dạng 49 | Dạng 49 là bất phương trình |
| Dạng 2 | Dạng 67 | Dạng 67 số mũ là tam thức bậc hai |
| Dạng 2 | Dạng 74 | Dạng 74 hỏi tập xác định |
| Dạng 3 | Dạng 56 | Dạng 56 đối số là phân thức |
| Dạng 5 | Dạng 70 | Dạng 70 đối số chỉ là b |
| Dạng 9 | Dạng 85 | Dạng 85 viết vế phải dưới dạng lũy thừa a^{g(x)} |
| Dạng 9 | Dạng 80 | Dạng 80 có c không là lũy thừa nguyên của a |
| Dạng 10 | Dạng 30 | Dạng 30 chỉ có một biến a và so sánh log(a^k) với log(ka) |
| Dạng 11 | Dạng 49 | Dạng 49 một vế là lôgarit, vế kia là số |
| Dạng 12 | Dạng 28 | Dạng 28 là log_a(x² + bx) |
| Dạng 15 | Dạng 28 | Dạng 28 đối số là x² + bx |
| Dạng 15 | Dạng 12 | Dạng 12 là ln của biểu thức chứa căn |
| Dạng 16 | Dạng 23 | Dạng 23 có hai vế là lũy thừa với dấu <, không có phép trừ |
| Dạng 16 | Dạng 43 | Dạng 43 có a^x > c |
| Dạng 17 | Dạng 75 | Dạng 75 cơ số là a, đối số là căn của a |
| Dạng 18 | Dạng 65 | Dạng 65 có lôgarit ở mỗi vế và số 1 ở vế phải |
| Dạng 23 | Dạng 27 | Dạng 27 số mũ bậc hai ở vế trái |
| Dạng 23 | Dạng 33 | Dạng 33 số mũ bậc hai ở vế phải, dấu ≥ |
| Dạng 23 | Dạng 85 | Dạng 85 là phương trình |
| Dạng 26 | Dạng 31 | Dạng 31 chỉ có một biến, log_c(a^k) |
| Dạng 26 | Dạng 10 | Dạng 10 chọn mệnh đề đúng |
| Dạng 27 | Dạng 33 | Dạng 33 số mũ bậc hai ở vế phải |
| Dạng 30 | Dạng 31 | Dạng 31 hỏi giá trị log_c(a^k) bằng biểu thức nào |
| Dạng 31 | Dạng 70 | Dạng 70 là log_{a²} b, cơ số có lũy thừa |
| Dạng 32 | Dạng 39 | Dạng 39 có a, b là số mũ trong đối số |
| Dạng 35 | Dạng 58 | Dạng 58 có điều kiện x₁x₂ cho trước và log_a²x không có (bx) |
| Dạng 36 | Dạng 53 | Dạng 53 là bất phương trình với bốn lôgarit |
| Dạng 37 | Dạng 79 | Dạng 79 đối số là x − c |
| Dạng 37 | Dạng 74 | Dạng 74 là hàm mũ a^x |
| Dạng 38 | Dạng 49 | Dạng 49 có cơ số a ghi rõ và đối số bậc nhất |
| Dạng 42 | Dạng 78 | Dạng 78 có hàm mũ và y là số nguyên |
| Dạng 42 | Dạng 83 | Dạng 83 có e^x |
| Dạng 43 | Dạng 76 | Dạng 76 là a^x < c |
| Dạng 44 | Dạng 61 | Dạng 61 đối số là tích c·a |
| Dạng 44 | Dạng 50 | Dạng 50 là hiệu hai ln |
| Dạng 45 | Dạng 46 | Dạng 46 là tổng log_p a^k + log_p b |
| Dạng 47 | Dạng 77 | Dạng 77 có hiệu hai lũy thừa nhân (log − hằng) và dấu ≤ |
| Dạng 47 | Dạng 82 | Dạng 82 có hiệu hai lôgarit nhân (hằng − lũy thừa) |
| Dạng 48 | Dạng 87 | Dạng 87 có đúng ba số nguyên b và bất phương trình tích |
| Dạng 48 | Dạng 73 | Dạng 73 không quá k số nguyên y và bất phương trình lôgarit |
| Dạng 56 | Dạng 79 | Dạng 79 đối số là nhị thức |
| Dạng 73 | Dạng 52 | Dạng 52 chỉ một biến x |
| Dạng 77 | Dạng 82 | Dạng 82 thừa số đầu là hiệu hai lôgarit, dấu ≥ |
| Dạng 78 | Dạng 83 | Dạng 83 có e^x và y nguyên dương |
| Dạng 80 | Dạng 43 | Dạng 43 là bất phương trình a^x > c |
| Dạng 90 | Dạng 91 | phần thực / phần ảo |
| Dạng 92 | Dạng 89 | hỏi z̄ chứ không phải z |
| Dạng 93 | Dạng 112 | Dạng 93 hỏi phần thực của tổng, Dạng 112 hỏi chính tổng (đáp án là số phức) |
| Dạng 93 | Dạng 94 | Dạng 94 hỏi phần ảo của z₁+z̄₂ |
| Dạng 93 | Dạng 102 | Dạng 102 hỏi môđun của tổng |
| Dạng 95 | Dạng 93 | tích / tổng |
| Dạng 95 | Dạng 94 | tích z₁z₂ / tổng z₁+z̄₂ |
| Dạng 96 | Dạng 90 | Dạng 90 hỏi phần thực của chính z, Dạng 96 hỏi phần thực của z² |
| Dạng 96 | Dạng 107 | Dạng 107 hỏi điểm biểu diễn của z² chứ không hỏi phần thực |
| Dạng 99 | Dạng 100 | Dạng 100 cho z dưới dạng tích i(a+bi) cần nhân ra trước |
| Dạng 99 | Dạng 118 | Dạng 118 cho z qua phương trình iz = c |
| Dạng 102 | Dạng 101 | Dạng 101 chỉ cho một số phức |
| Dạng 103 | Dạng 104 | Dạng 104 cho hai số phức z, w rồi tính |z·w̄| |
| Dạng 103 | Dạng 105 | Dạng 105 tính môđun của tích (c+di)·z |
| Dạng 104 | Dạng 105 | Dạng 105 không có liên hợp, chỉ một số phức z |
| Dạng 106 | Dạng 107 | Dạng 107 cho z = (a+bi)² phải bình phương trước |
| Dạng 106 | Dạng 110 | Dạng 110 cho điểm tìm số phức, chiều ngược lại |
| Dạng 108 | Dạng 106 | Dạng 106 hỏi điểm biểu diễn của chính z |
| Dạng 109 | Dạng 112 | Dạng 112 hỏi chính số phức z₁+z₂, không hỏi tọa độ điểm biểu diễn |
| Dạng 110 | Dạng 111 | Dạng 111 chỉ hỏi phần thực của z |
| Dạng 112 | Dạng 113 | Dạng 113 là hiệu |
| Dạng 116 | Dạng 117 | Dạng 117 phương trình chỉ chứa z̄ |
| Dạng 116 | Dạng 120 | Dạng 120 chứa cả z và z̄ |
| Dạng 117 | Dạng 118 | Dạng 118 phương trình iz = c và hỏi liên hợp |
| Dạng 119 | Dạng 120 | Dạng 120 phương trình khác và hỏi môđun |
| Dạng 119 | Dạng 121 | Dạng 121 phương trình chứa |z| |
| Dạng 122 | Dạng 123 | Dạng 123 điều kiện thứ hai là z/(z−q) thuần ảo |
| Dạng 125 | Dạng 126 | Dạng 126 là phương trình |z|(z−…)=(…)z và hỏi đếm số số phức z |
| Dạng 128 | Dạng 129 | Dạng 129 điều kiện là một tích thuần ảo |
| Dạng 129 | Dạng 130 | Dạng 130 hỏi BÁN KÍNH |
| Dạng 131 | Dạng 132 | Dạng 132 có w = (c+iz)/(1+z) dạng phân thức |
| Dạng 133 | Dạng 134 | Dạng 134 phương trình có dạng z² − 2(m+k)z + m² = 0 và điều kiện tổng môđun |
| Dạng 134 | Dạng 135 | cùng phương trình, Dạng 135 hỏi tồn tại nghiệm z₀ có |z₀| = R |
| Dạng 138 | Dạng 140 | Dạng 140 điều kiện |z² − C| = k|z| và hỏi M²+m² |

## 6. Dạng đã bỏ vì trùng với dạng khác

Quy ước: hai dạng giống nhau về bài toán thì bỏ hẳn một dạng. Các file dữ liệu gốc không bị sửa; dạng bị bỏ chỉ không có trong danh mục và bộ định tuyến.

| Dạng bị bỏ (mã cũ) | Mô tả cũ | Giữ lại thay thế | Lý do | Số câu bỏ |
|---|---|---|---|---|
| ML_D59 | Tính giá trị lôgarit có cơ số là căn bậc hai của biến | Dạng 17 (mã cũ ML_D20) | Cùng một bài toán với ML_D20 (log_{ⁿ√a} a^m); ML_D20 có cả các câu với m = 1, trùng hẳn về toán. | 91 |

Dạng bị bỏ thì không còn trong tập huấn luyện lẫn tập kiểm tra; số dạng giảm một và tổng số câu giảm theo.

## 7. Các cặp cần bạn và thầy quyết định

Các cặp này tách được bằng dấu hiệu bề mặt (đã kiểm chứng ở mục 2) và danh mục hiện giữ mỗi cặp là hai dạng riêng, vì dạng câu hỏi khác nhau rõ. Nếu theo quy ước 'giống nhau thì bỏ một dạng' thì đây là các ứng viên tiếp theo.

| Cặp | Vì sao gần nhau | Gợi ý |
|---|---|---|
| Dạng 30 và Dạng 31 | Cùng bài học log(a^k) = k·log a; khác ở cách hỏi. | Giữ riêng nếu bài báo cần số liệu theo dạng gốc của nguồn. |
| Dạng 9 và Dạng 85 | Cùng loại phương trình mũ cùng cơ số; khác ở cách viết vế phải. | Giữ riêng, khác biệt ổn định trên mọi câu (94/94 và 91/91). |
| Dạng 10 và Dạng 26 | Cùng bài học tính chất lôgarit của tích, thương, lũy thừa. | Giữ riêng, dạng câu hỏi khác nhau rõ. |

## 8. Lưu ý khi đưa danh mục vào prompt

- Mỗi dòng 'Dạng N: mô tả' dài trung bình 129 ký tự, dài nhất 258; cả danh mục khoảng 18254 ký tự (file `danh_muc_trong_prompt.txt`). Tiếng Việt tốn nhiều token, nên cần đo bằng tokenizer của Qwen3 trước khi chốt cách fine-tune, vì loss chỉ tính trên đầu ra nhưng chi phí tính toán vẫn tính trên cả chuỗi.
- Cột `cach_giai` mới điền cho Mũ-Logarit (32 dạng ReAct+Calculator, 56 dạng zero-shot). Cách giải của từng dạng Số phức cần lấy từ kết quả Số phức rồi điền nốt.

## 9. Cách chạy lại các kiểm tra

```
cd scripts/router
python check_catalogue.py ALL     # mô tả duy nhất; mỗi đề khớp đúng dấu hiệu của dạng mình
python check_claims.py            # các chi tiết trong mô tả nằm ở phương án hoặc là hằng số
python name_similarity.py 40      # các cặp mô tả giống nhau nhất và phần khác nhau
python build_catalogue.py         # xuất lại danh mục và báo cáo này
```
