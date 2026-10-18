# Vấn đề hiện tại của pipeline (ghi chú để nghiên cứu tiếp)

Pipeline phiên bản 1 (router Qwen3-0.6B + LoRA → prompt của dạng → Qwen3-4B zero-shot hoặc ReAct + Calculator) được thử trên 93 mẫu
thực tế: phân dạng đúng 77/93, đáp án đúng 89/93. Ở 16 câu phân sai dạng, mô hình vẫn giải và cho đáp án đúng; cả 4 câu đáp án
sai đều đã được phân đúng dạng.

**Mục tiêu nghiên cứu:** toàn bộ quá trình từ đề bài đến đáp án phải đạt 100%.

**Cách chọn vấn đề để ghi:** một vấn đề được ghi nếu nó là nguyên nhân chính dẫn đến một kết quả sai, dù chỉ ở một câu, không xét tần suất.
Hiện tượng xảy ra nhiều nhưng không phải nguyên nhân chính của kết quả sai thì chưa ghi. Khi pipeline phiên bản 2 (đã sửa các vấn đề
dưới đây) được thử lại trên bộ đánh giá và một hiện tượng nào đó trở thành nguyên nhân chính khiến chưa đạt 100%, lúc đó mới nghiên cứu
để có phiên bản 3. Ngoại lệ: các vấn đề ở mục "chưa làm sai đáp án" vẫn được ghi vì có thể là vấn đề nghiên cứu về SLM khi giải toán.

Bằng chứng từng câu: [`PHAN_TICH_LOI.md`](PHAN_TICH_LOI.md). Số liệu tái tạo bằng `scripts/pipeline/analyze_pipeline_errors.py`.

## Về vấn đề của mô hình phân dạng

- **Dữ liệu huấn luyện chỉ đổi số liệu, ít đổi mẫu câu.** Gặp mẫu câu mới (đổi cách diễn đạt, cách viết cơ số, hàm, cách hỏi) thì mô hình dễ
  phân sai. Trung vị mỗi dạng chỉ có 3 mẫu câu trong dữ liệu huấn luyện; cả 16 câu sai đều có mẫu câu chưa từng xuất hiện.
- **Các dạng gần giống nhau có cùng cụm mở đầu thì dễ bị lẫn với nhau**, ví dụ những dạng cùng mở đầu "Tìm tập xác định của ...".
- **Pipeline chưa có cơ chế tìm và xử lý riêng với những câu không thuộc các dạng bài được xác định trước.** Mô hình luôn trả về một dạng,
  và độ tin cậy không báo được lỗi (6 trong 16 câu sai có độ tin cậy từ 0,9 trở lên).

## Về vấn đề của mô hình sinh khi giải

*Các vấn đề dẫn đến đáp án sai:*

- **Khi áp dụng ReAct, SLM thấy kết quả có vấn đề nhưng chưa tự tìm được cách sửa để đảm bảo đáp án cuối đúng.** Mục tiêu là đáp án cuối
  đúng, không đòi hỏi quá trình giải phải hoàn hảo. Hiện tại khi một bước ở giữa hỏng (công cụ báo lỗi, đọc sai tham số từ đề, kết quả tính
  không khớp phương án nào), mô hình chỉ lặp lại cách làm cũ hoặc chọn đại một phương án, không đổi hướng và không kiểm tra lại. Ví dụ, gặp phương án
  "Vô số", mô hình viết rằng đó không phải đáp án hợp lệ nhưng vẫn lặp lại một lệnh lỗi cho đến khi bị ép trả lời (3 câu sai). Đề ghi $4a^2$ nhưng
  mô hình đọc thành $(4a)^2$, rồi cả bốn phép so sánh đều `False` mà vẫn chọn một phương án (1 câu sai).
- **Khi giải zero-shot, mô hình tính đúng nhưng so với phương án thì sai (đã từng xảy ra ở một lần chạy).** Mô hình chép sai một phương án rồi cho
  rằng khớp với kết quả của mình, và không nhận ra một phương án khác thực ra bằng kết quả của mình ($\ln 4 = 2\ln 2$), nên chọn sai (câu BS-011, lần chạy
  đầu). Ở lần chạy sau, cùng câu này mô hình tự nghi ngờ nhiều lần và mới nhận ra, nên chọn đúng. Mới quan sát ở một câu.

*Vấn đề chưa làm sai đáp án (vẫn cho đáp án đúng) nhưng đáng nghiên cứu ở SLM khi giải toán:*

- **Ở 4 câu ReAct, mô hình chọn được đáp án đúng nhưng không phải do mô hình giải ra** (BS-004, BS-001, MOI-039, WEB-087). Khi đề khác câu ví dụ trong
  prompt (biến chữ thay cho số, dấu khác, tham số ở vị trí khác, dùng nhầm prompt của dạng khác), công cụ báo lỗi hoặc kết quả tính ra không khớp phương án
  nào. Mô hình có lúc tự nhận ra có gì đó lệch nhưng không tìm được cách khác, nên chọn đại một phương án và tình cờ trúng. Trong chuỗi giải của 4 câu này
  không có lập luận nào dẫn tới đáp án cuối. Chưa kiểm chứng: nếu cho zero-shot giải riêng các câu này thì có đúng không.

*Không ghi (không phải nguyên nhân của kết quả sai):* zero-shot lập luận dài và hay tự nghi ngờ (vẫn kết thúc trong ngân sách 9216 token, câu dài nhất
dùng 7587 token); kết quả không lặp lại giữa các lần chạy (là vấn đề của cách đánh giá: cần chạy lặp lại).

## Rút kinh nghiệm cho phiên bản sau

- Phiên bản 2 cần xử lý các vấn đề ở trên, rồi thử lại trên bộ đánh giá (có thêm các đề lệch mẫu và phương án không phải số) để xem vấn đề nào còn là nguyên
  nhân chính của kết quả sai.
- Chạy lặp lại nhiều lần mỗi phiên bản: cùng prompt và seed nhưng khác thành phần batch thì lời giải có thể khác.
- Nhãn dạng của bộ thực tế do người gán thủ công; 7 câu có nhãn chưa chắc đã được bỏ khỏi bộ 93 câu (xem `README.md` cùng thư mục).
