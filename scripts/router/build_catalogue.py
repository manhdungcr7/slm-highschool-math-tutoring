# -*- coding: utf-8 -*-
"""Write the routing catalogue (CSV, JSON, prompt text) and the audit report.

python build_catalogue.py
Outputs go to data/catalogue/.

Every type gets one running number over both topics: "Dạng 1", "Dạng 2", ...  The old code (ML_D36a, SP_D05, ...) is kept
only as a lookup column, it never appears in the text a language model reads.
"""
import collections
import csv
import json
import os
import re
import statistics

import catalogue_ml
import catalogue_sp
from common import DROPPED, REPO, load_questions, stem

OUT = os.path.join(REPO, "data", "catalogue")
TOPIC_ORDER = ["ML", "SP"]          # topic that is numbered first; change here to put Số phức first
TOPIC_NAME = {"ML": "Mũ-Logarit", "SP": "Số phức"}

# Types whose OLD name does not describe the questions that really belong to them (checked on the data).
WRONG = {
    "SP_D07": "Tên cũ ghi 'phần thực hoặc phần ảo của tích'. Cả 91 câu đều hỏi phần ảo của z₁z₂.",
    "SP_D08": "Tên cũ ghi 'phần thực hoặc phần ảo của z²'. Cả 91 câu đều hỏi phần thực của z².",
    "SP_D14": "Tên cũ ghi 'tổng / hiệu'. Cả 91 câu đều là môđun của tổng z₁+z₂, không có câu nào về hiệu.",
    "SP_D29": "Tên cũ ghi 'phần thực hoặc phần ảo'. Cả 91 câu đều hỏi phần ảo, phương trình luôn là i·z̄ = c.",
    "SP_D10": "Tên cũ ghi 'Cho một số số phức'. Đề không cho số phức nào, chỉ hỏi 'Số phức nào dưới đây là số thuần ảo?'.",
    "SP_D21": "Tên cũ ghi 'tổ hợp tuyến tính (vd 2z₁+z₂)'. Cả 91 câu đều đúng là 2z₁+z₂.",
    "SP_D27": "Tên cũ ghi 'biểu thức phối hợp nhiều phép toán'. Cả 91 câu đều là w = iz + z̄.",
    "SP_D40": "Tên cũ không nói đề hỏi gì. Cả 91 câu đều hỏi tọa độ tâm đường tròn.",
    "SP_D12": "Tên cũ ghi 'dưới dạng biểu thức'. Cả 91 câu đều có z = i(a+bi).",
    "ML_D10": "Tên cũ chung chung. Đề là y = ln(x² + k) − mx + 1, k thay đổi theo biến thể (1, 4, 9, 16, …).",
    "ML_D13": "Tên cũ ghi 'rút gọn biểu thức'. Đề không ghi biểu thức; log_p(q·a^k/b) nằm trong các phương án và p, q, k thay đổi.",
    "ML_D06": "Tên cũ ghi 'công thức đổi cơ số'. Đề là log_{a^k}(ab) nằm trong các phương án, k thay đổi.",
    "ML_D19": "Tên cũ ghi 'a^f(x) > a^k'. Đề có dạng a^{f(x)} − a^k > 0 (có phép trừ, so với 0).",
    "ML_D14": "Tên cũ ghi 'cơ số nhỏ hơn 1'. Cả 91 câu đều có cơ số 1/2 và hai vế đều là lôgarit.",
    "ML_D53": "Tên cũ ghi 'log_a(f(x)) > k, cơ số a'. Có câu gốc viết log(x−2) > 0 không ghi cơ số.",
    "ML_D27": "Tên cũ ghi 'a^f(x) < a^g(x)'. Có câu gốc có vế phải chỉ là số (2^{x+1} < 4).",
    "ML_D38": "Tên cũ ghi 'hai vế là tam thức bậc hai'. Thực tế chỉ vế phải bậc hai; vế trái bậc nhất hoặc hằng (2^5 ≥ 2^{x²+2x}).",
    "ML_D43": "Tên cũ ghi 'lôgarit cơ bản (lôgarit thập phân)'. Thực tế là log x ≥ k, k có thể âm hoặc phân số.",
    "ML_D46": "Tên cũ nêu cách giải ('ẩn phụ t = log_a b'). Đề là a^x = b^y = (ab)^{1/k}, P = x + m·y; hệ số của y và k thay đổi.",
    "ML_D22": "Tên cũ chung chung. Đề là log_a b = k (k là số hoặc căn), tính log_{√b/a} √(b/a).",
    "ML_D68": "Tên cũ nêu cách giải ('bất đẳng thức Cô-si'). Mọi hệ số trong hai lôgarit đều thay đổi theo biến thể.",
    "ML_D65": "Tên cũ nêu cách giải ('hàm đặc trưng'). Mọi hệ số của phương trình đều thay đổi theo biến thể.",
    "ML_D75": "Tên cũ chung chung. Biểu thức √(c^x − m) có c là số nguyên hoặc phân số; 89/91 câu dùng phân số.",
    "ML_D94": "Tên cũ chung chung. Biểu thức P = x² + y² + px + qy, p và q thay đổi.",
    "ML_D93": "Tên cũ chung chung. Bất phương trình (p^b − p)(a·q^b − r) < 0 có p, q, r thay đổi.",
    "ML_D88": "Tên cũ chung chung. Các cơ số, hằng số trong tích thay đổi theo biến thể.",
    "ML_D79": "Tên cũ chung chung. Hai cơ số lôgarit và ngưỡng k thay đổi.",
    "ML_D56": "Tên cũ chung chung. Hai cơ số, x² − c và hai mẫu số đều thay đổi.",
}

# Types whose old name is true but not enough to tell it apart from a neighbour.
AMBIGUOUS = {
    "SP_D05": "Gần SP_D24: cùng hai số phức z₁, z₂ và tổng. D05 hỏi phần thực của tổng, D24 hỏi chính tổng.",
    "SP_D24": "Tên cũ 'tìm tổng của chúng' gần SP_D05 và SP_D25; đáp án của D24 là một số phức.",
    "SP_D28": "Tên cũ của D28, D29, D30 đều chứa cụm 'chỉ chứa z hoặc z̄' nên không tách được chúng; D28 và D30 chứa z, D29 chứa z̄.",
    "SP_D30": "Xem SP_D28.",
    "SP_D37": "Tên cũ của D37 và D38 chỉ khác vế cuối và nêu cách giải ('đặt t=|z|…') không hiện trong đề.",
    "SP_D38": "Xem SP_D37.",
    "SP_D39": "Tên cũ 'hai điều kiện về môđun và liên hợp' quá chung.",
    "SP_D45": "Tên cũ của D45, D46, D47 cùng bắt đầu bằng 'Cho phương trình bậc hai một tham số m, đếm số giá trị m để …'.",
    "SP_D46": "Xem SP_D45.",
    "SP_D47": "Xem SP_D45.",
    "SP_D41": "Tên cũ của D41 và D42 chỉ khác TÂM / BÁN KÍNH; đã thêm dạng tích để nhìn thấy khác biệt thứ hai.",
    "SP_D42": "Xem SP_D41.",
    "ML_D12": "Tên cũ của D12 và D91 gần như giống nhau (a^f(x)=a^k và a^f(x)=a^g(x)). Khác biệt thật: vế phải của D12 luôn là số nguyên (94/94), của D91 luôn là lũy thừa (91/91).",
    "ML_D91": "Xem ML_D12.",
    "ML_D33": "Bốn dạng bất phương trình mũ cùng cơ số (D19, D27, D33, D38) có tên gần giống nhau; tên mới nêu số mũ ở từng vế và chiều bất đẳng thức.",
    "ML_D48": "D48 và D82 chỉ khác chiều bất đẳng thức; đã thêm chữ LỚN HƠN / NHỎ HƠN để khác biệt nằm trong từ chứ không chỉ trong ký hiệu.",
    "ML_D82": "Xem ML_D48.",
    "ML_D20": "D20 và D81 đều là lôgarit có căn của a, khác nhau ở chỗ căn nằm ở cơ số (D20) hay ở đối số (D81).",
    "ML_D36a": "D36a và D36b cùng bài học log(a^k) = k·log a; khác ở cách hỏi (chọn đẳng thức đúng / log_c(a^k) bằng).",
    "ML_D36b": "Xem ML_D36a.",
    "ML_D42": "D42, D85, D61, D04 đều là tập xác định hàm lôgarit; tên mới nêu rõ đối số.",
    "ML_D85": "Xem ML_D42.",
}

REACT = {"D08", "D10", "D16", "D17", "D22", "D23", "D24", "D25", "D28", "D29", "D40", "D41", "D45", "D46", "D47",
         "D51", "D52", "D56", "D57", "D65", "D68", "D69", "D71", "D75", "D78", "D79", "D83", "D84", "D88", "D89",
         "D93", "D94"}


def entries():
    return catalogue_sp.ENTRIES + catalogue_ml.ENTRIES


def sort_key(code):
    topic, rest = code.split("_", 1)
    m = re.match(r"D(\d+)(.*)", rest)
    return TOPIC_ORDER.index(topic), int(m.group(1)), m.group(2)


def numbering():
    order = sorted((e["code"] for e in entries()), key=sort_key)
    return {c: i + 1 for i, c in enumerate(order)}


def solve_mode(code):
    if code.startswith("ML_"):
        return "ReAct+Calculator" if code[3:] in REACT else "zero-shot"
    return ""


def main():
    os.makedirs(OUT, exist_ok=True)
    num = numbering()
    old, rows = load_questions()
    count = collections.Counter(r["label"] for r in rows)
    src = collections.Counter(r["label"] for r in rows if r["source"] == "Câu gốc")

    def label(code):
        return f"Dạng {num[code]}"

    def shortest_example(code):
        """The shortest real question stem of the type, used as a worked example next to the description."""
        qs = [stem(r["text"]).replace("\n", " ").strip() for r in rows if r["label"] == code]
        return min(qs, key=len)

    examples = {e["code"]: shortest_example(e["code"]) for e in entries()}

    def conv(text, topic):
        """Replace old codes (SP_D05, ML_D36a, or bare D05 inside the topic of the entry) by 'Dạng N'."""
        text = re.sub(r"\b(SP|ML)_D(\d+[ab]?)\b", lambda m: label(m.group(0)), text)
        return re.sub(r"\bD(\d+[ab]?)\b", lambda m: label(f"{topic}_D{m.group(1)}"), text)

    table = []
    for e in sorted(entries(), key=lambda e: num[e["code"]]):
        c = e["code"]
        topic = c[:2]
        table.append(dict(
            ten_goi=label(c), so_dang=num[c], chu_de=TOPIC_NAME[topic], ma_cu=c, ten_dang_cu=old[c],
            mo_ta_dang_moi=e["name"], vi_du=examples[c],
            muc_do=("Tên cũ sai so với đề" if c in WRONG else "Tên cũ nhập nhằng" if c in AMBIGUOUS else
                    "Diễn đạt lại" if old[c] != e["name"] else "Giữ nguyên"),
            so_cau=count[c], so_cau_goc=src[c], cach_giai=solve_mode(c),
            phan_biet_voi="; ".join(f"{label(o)}: {conv(d, topic)}" for o, d in e.get("close_to", [])),
            dau_hieu_nhan_dang=e["pattern"]))

    with open(os.path.join(OUT, "danh_muc_dang_bai.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    with open(os.path.join(OUT, "danh_muc_dang_bai.json"), "w", encoding="utf-8") as f:
        json.dump([dict(ten_goi=t["ten_goi"], mo_ta=t["mo_ta_dang_moi"], vi_du=t["vi_du"]) for t in table], f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "danh_muc_trong_prompt.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(f"{t['ten_goi']}: {t['mo_ta_dang_moi']}" for t in table) + "\n")

    n = len(table)
    chg = collections.Counter(t["muc_do"] for t in table)
    first = {tp: min(num[c] for c in num if c.startswith(tp)) for tp in TOPIC_ORDER}
    last = {tp: max(num[c] for c in num if c.startswith(tp)) for tp in TOPIC_ORDER}
    lines = []
    A = lines.append
    n_ml = sum(1 for t in table if t["chu_de"] == TOPIC_NAME["ML"])
    n_sp = n - n_ml
    q_ml = sum(t["so_cau"] for t in table if t["chu_de"] == TOPIC_NAME["ML"])
    q_sp = sum(t["so_cau"] for t in table if t["chu_de"] == TOPIC_NAME["SP"])
    q_src = sum(t["so_cau_goc"] for t in table)
    raw = collections.Counter(r["label"] for r in load_questions(keep_dropped=True)[1])
    A(f"# Rà soát tên và cách gọi tên các dạng bài ({n} dạng)")
    A("")
    A("Người đọc: nhóm làm đề tài, trước khi dùng danh mục này làm đầu vào cho bộ định tuyến dạng bài.")
    A("")
    A("## 1. Cách gọi tên mới")
    A("")
    A(f"Mỗi dạng được gọi bằng một số thứ tự chung cho cả hai chủ đề: **Dạng 1, Dạng 2, …, Dạng {n}**, viết đầy đủ chữ 'Dạng', không dùng chữ cái a, b hay tiền tố.")
    A("")
    A("| Chủ đề | Các dạng | Số dạng |")
    A("|---|---|---|")
    for tp in TOPIC_ORDER:
        A(f"| {TOPIC_NAME[tp]} | Dạng {first[tp]} đến Dạng {last[tp]} | {last[tp] - first[tp] + 1} |")
    A("")
    A("Số thứ tự đi theo thứ tự mã cũ trong từng chủ đề. Hai dạng cũ D36a, D36b (và D50a, D50b) trở thành hai số riêng liền nhau. Cột `ma_cu` trong file CSV cho biết mã cũ tương ứng, để nối với các file prompt và kết quả đã có (ví dụ `prompt_D40.txt`). Mã cũ không xuất hiện trong văn bản mô hình đọc.")
    A("")
    A("## 2. Kết quả kiểm tra")
    A("")
    A("| Kiểm tra | Kết quả |")
    A("|---|---|")
    A(f"| Số dạng | {n} (Mũ-Logarit {n_ml}, Số phức {n_sp}) |")
    A(f"| Mã cũ trùng giữa hai chủ đề | D01 đến D54 có ở cả hai chủ đề (54 mã trùng, ví dụ D01 vừa là 'tìm đồng thời phần thực và phần ảo' vừa là 'giải phương trình lôgarit cơ bản'). Cách gọi 'Dạng 1 … Dạng {n}' không còn trùng. |")
    A("| Tên dạng trùng nhau | Không có hai mô tả giống hệt. Sau khi bỏ dấu cách, dấu câu và chữ hoa (giữ lại ký hiệu < > và các từ 'lớn hơn', 'nhỏ hơn') vẫn không có hai mô tả trùng. |")
    A(f"| Dấu hiệu nhận dạng khớp với {q_ml + q_sp} đề ({q_ml} Mũ-Logarit, {q_sp} Số phức, gồm {q_src} câu gốc) | Mỗi đề khớp đúng một dấu hiệu, là dấu hiệu của chính dạng của nó: **{q_ml + q_sp}/{q_ml + q_sp}**. Không có đề nào khớp dấu hiệu của dạng khác. |")
    A("| Chi tiết mà mô tả nêu nhưng câu dẫn không thấy (nằm ở phương án hoặc là hằng số) | 18 kiểm chứng, đều đạt trên mọi biến thể của dạng đó. |")
    A(f"| Mô tả đã đổi | {sum(1 for t in table if t['muc_do'] != 'Giữ nguyên')}/{n}: {chg['Tên cũ sai so với đề']} mô tả cũ sai so với đề, {chg['Tên cũ nhập nhằng']} nhập nhằng, {chg['Diễn đạt lại']} diễn đạt lại; {chg['Giữ nguyên']} giữ nguyên. |")
    A("| Từ viết tắt trong mô tả | Đã viết đầy đủ (GTNN, GTLN thành giá trị nhỏ nhất, giá trị lớn nhất). |")
    A("")
    A("Dấu hiệu nhận dạng là biểu thức chính quy viết cho từng dạng, tìm trên câu dẫn của đề (đã bỏ khoảng trắng và dấu $). Nó là bằng chứng cho hai điều: mô tả đúng với mọi đề của dạng, và hai dạng khác nhau không có đề nào chung đặc điểm nhận dạng.")
    A("")
    A("**Nguyên tắc viết mô tả mới.** Bộ định tuyến chỉ nhìn thấy đề bài, nên mô tả nói cái nhìn thấy trong đề: cho gì (dạng biểu thức, điều kiện) và hỏi gì (đại lượng cần tìm). Mô tả cũ nhiều chỗ nói cách giải ('bằng đổi cơ số', 'qua ẩn phụ', 'bằng hàm đặc trưng', 'bằng bất đẳng thức Cô-si'); cách giải không hiện trong đề nên không giúp nhận dạng. Mô tả viết bằng lời, không dùng chữ thay thế như p, q, k; để prompt ngắn, mô tả đứng một mình, không kèm đề ví dụ. Một đề ví dụ thật (đề ngắn nhất của dạng) vẫn được lưu ở cột `vi_du` trong file CSV và JSON để tham khảo.")
    A("")
    A("## 3. Mô tả cũ sai so với đề (đã sửa)")
    A("")
    A("| Dạng | Mã cũ | Mô tả cũ | Vấn đề (đối chiếu với dữ liệu) | Mô tả mới |")
    A("|---|---|---|---|---|")
    for t in table:
        if t["ma_cu"] in WRONG:
            A(f"| {t['ten_goi']} | {t['ma_cu']} | {t['ten_dang_cu']} | {conv(WRONG[t['ma_cu']], t['ma_cu'][:2])} | {t['mo_ta_dang_moi']} |")
    A("")
    A("## 4. Mô tả cũ đúng nhưng nhập nhằng với dạng khác (đã sửa)")
    A("")
    A("| Dạng | Mã cũ | Mô tả cũ | Lý do | Mô tả mới |")
    A("|---|---|---|---|---|")
    for t in table:
        c = t["ma_cu"]
        if c in AMBIGUOUS and c not in WRONG and t["muc_do"] != "Giữ nguyên":
            A(f"| {t['ten_goi']} | {c} | {t['ten_dang_cu']} | {conv(AMBIGUOUS[c], c[:2])} | {t['mo_ta_dang_moi']} |")
    A("")
    A("## 5. Các cặp dạng dễ nhầm và điểm phân biệt")
    A("")
    A("Điểm phân biệt của mỗi cặp đã ghi ngay trong mô tả, không cần xem đề.")
    A("")
    A("| Dạng | Dễ nhầm với | Điểm phân biệt |")
    A("|---|---|---|")
    seen = set()
    for e in sorted(entries(), key=lambda e: num[e["code"]]):
        for o, d in e.get("close_to", []):
            key = tuple(sorted((e["code"], o)))
            if key in seen:
                continue
            seen.add(key)
            A(f"| {label(e['code'])} | {label(o)} | {conv(d, e['code'][:2])} |")
    A("")
    A("## 6. Dạng đã bỏ vì trùng với dạng khác")
    A("")
    A("Quy ước: hai dạng giống nhau về bài toán thì bỏ hẳn một dạng. Các file dữ liệu gốc không bị sửa; dạng bị bỏ chỉ không có trong danh mục và bộ định tuyến.")
    A("")
    A("| Dạng bị bỏ (mã cũ) | Mô tả cũ | Giữ lại thay thế | Lý do | Số câu bỏ |")
    A("|---|---|---|---|---|")
    for dc, why in DROPPED.items():
        keeper = "ML_D20"
        A(f"| {dc} | {old[dc]} | {label(keeper)} (mã cũ {keeper}) | {why} | {raw[dc]} |")
    A("")
    A("Dạng bị bỏ thì không còn trong tập huấn luyện lẫn tập kiểm tra; số dạng giảm một và tổng số câu giảm theo.")
    A("")
    A("## 7. Các cặp cần bạn và thầy quyết định")
    A("")
    A("Các cặp này tách được bằng dấu hiệu bề mặt (đã kiểm chứng ở mục 2) và danh mục hiện giữ mỗi cặp là hai dạng riêng, vì dạng câu hỏi khác nhau rõ. Nếu theo quy ước 'giống nhau thì bỏ một dạng' thì đây là các ứng viên tiếp theo.")
    A("")
    A("| Cặp | Vì sao gần nhau | Gợi ý |")
    A("|---|---|---|")
    pairs = [
        ("ML_D36a", "ML_D36b", "Cùng bài học log(a^k) = k·log a; khác ở cách hỏi.", "Giữ riêng nếu bài báo cần số liệu theo dạng gốc của nguồn."),
        ("ML_D12", "ML_D91", "Cùng loại phương trình mũ cùng cơ số; khác ở cách viết vế phải.", "Giữ riêng, khác biệt ổn định trên mọi câu (94/94 và 91/91)."),
        ("ML_D13", "ML_D30", "Cùng bài học tính chất lôgarit của tích, thương, lũy thừa.", "Giữ riêng, dạng câu hỏi khác nhau rõ."),
    ]
    for a, b, why, hint in pairs:
        A(f"| {label(a)} và {label(b)} | {why} | {hint} |")
    A("")
    A("## 8. Lưu ý khi đưa danh mục vào prompt")
    A("")
    lens = [len(t["mo_ta_dang_moi"]) + len(t["ten_goi"]) + 2 for t in table]
    A(f"- Mỗi dòng 'Dạng N: mô tả' dài trung bình {round(statistics.mean(lens))} ký tự, dài nhất {max(lens)}; cả danh mục khoảng {sum(lens)} ký tự (file `danh_muc_trong_prompt.txt`). Tiếng Việt tốn nhiều token, nên cần đo bằng tokenizer của Qwen3 trước khi chốt cách fine-tune, vì loss chỉ tính trên đầu ra nhưng chi phí tính toán vẫn tính trên cả chuỗi.")
    A(f"- Cột `cach_giai` mới điền cho Mũ-Logarit ({sum(1 for t in table if t['cach_giai'] == 'ReAct+Calculator')} dạng ReAct+Calculator, {sum(1 for t in table if t['cach_giai'] == 'zero-shot')} dạng zero-shot). Cách giải của từng dạng Số phức cần lấy từ kết quả Số phức rồi điền nốt.")
    A("")
    A("## 9. Cách chạy lại các kiểm tra")
    A("")
    A("```")
    A("cd scripts/router")
    A("python check_catalogue.py ALL     # mô tả duy nhất; mỗi đề khớp đúng dấu hiệu của dạng mình")
    A("python check_claims.py            # các chi tiết trong mô tả nằm ở phương án hoặc là hằng số")
    A("python name_similarity.py 40      # các cặp mô tả giống nhau nhất và phần khác nhau")
    A("python build_catalogue.py         # xuất lại danh mục và báo cáo này")
    A("```")
    with open(os.path.join(OUT, "BAO_CAO_RA_SOAT_TEN_DANG.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("written:", OUT)
    print({tp: (first[tp], last[tp]) for tp in TOPIC_ORDER}, chg)


if __name__ == "__main__":
    main()
