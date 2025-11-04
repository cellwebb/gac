# Gợi Ý Hệ Thống Tùy Chỉnh

[English](../en/CUSTOM_SYSTEM_PROMPTS.md) | [简体中文](../zh-CN/CUSTOM_SYSTEM_PROMPTS.md) | [繁體中文](../zh-TW/CUSTOM_SYSTEM_PROMPTS.md) | [日本語](../ja/CUSTOM_SYSTEM_PROMPTS.md) | [한국어](../ko/CUSTOM_SYSTEM_PROMPTS.md) | [हिन्दी](../hi/CUSTOM_SYSTEM_PROMPTS.md) | **Tiếng Việt** | [Français](../fr/CUSTOM_SYSTEM_PROMPTS.md) | [Русский](../ru/CUSTOM_SYSTEM_PROMPTS.md) | [Español](../es/CUSTOM_SYSTEM_PROMPTS.md) | [Português](../pt/CUSTOM_SYSTEM_PROMPTS.md) | [Deutsch](../de/CUSTOM_SYSTEM_PROMPTS.md) | [Nederlands](../nl/CUSTOM_SYSTEM_PROMPTS.md)

Hướng dẫn này giải thích cách tùy chỉnh gợi ý hệ thống mà GAC sử dụng để tạo thông điệp commit, cho phép bạn xác định kiểu và quy ước thông điệp commit của riêng mình.

## Mục Lục

- [Gợi Ý Hệ Thống Tùy Chỉnh](#gợi-ý-hệ-thống-tùy-chỉnh)
  - [Mục Lục](#mục-lục)
  - [Gợi Ý Hệ Thống Là Gì?](#gợi-ý-hệ-thống-là-gì)
  - [Tại Sao Sử Dụng Gợi Ý Hệ Thống Tùy Chỉnh?](#tại-sao-sử-dụng-gợi-ý-hệ-thống-tùy-chỉnh)
  - [Bắt Đầu Nhanh](#bắt-đầu-nhanh)
  - [Viết Gợi Ý Hệ Thống Tùy Chỉnh Của Bạn](#viết-gợi-ý-hệ-thống-tùy-chỉnh-của-bạn)
  - [Ví Dụ](#ví-dụ)
    - [Kiểu Commit Dựa Trên Emoji](#kiểu-commit-dựa-trên-emoji)
    - [Quy Ước Cụ Thể Đội Vụ](#quy-ước-cụ-thể-đội-vụ)
    - [Kiểu Kỹ Thuật Chi Tiết](#kiểu-kỹ-thuật-chi-tiết)
  - [Thực Hành Tốt Nhất](#thực-hành-tốt-nhất)
    - [Nên](#nên)
    - [Không Nên](#không-nên)
    - [Mẹo](#mẹo)
  - [Xử Lý Sự Cố](#xử-lý-sự-cố)
    - [Thông điệp vẫn có tiền tố "chore:"](#thông- điệp-vẫn-có-tiền-to-chore)
    - [AI bỏ qua hướng dẫn của tôi](#ai-bỏ-qua-hướng-dẫn-của-tôi)
    - [Thông điệp quá dài/ngắn](#thông- điệp-quá-dài-ngắn)
    - [Gợi ý tùy chỉnh không được sử dụng](#gợi-ý-tùy-chỉnh-không-được-sử-dụng)
    - [Muốn chuyển lại về mặc định](#muốn-chuyển-lại-về-mặc-định)
  - [Tài Liệu Liên Quan](#tài-liệu-liên-quan)
  - [Cần Trợ Giúp?](#cần-trợ-giúp)

## Gợi Ý Hệ Thống Là Gì?

GAC sử dụng hai gợi ý khi tạo thông điệp commit:

1. **Gợi Ý Hệ Thống** (có thể tùy chỉnh): Hướng dẫn định định vai trò, kiểu và quy ước cho thông điệp commit
2. **Gợi Ý Người Dùng** (tự động): Dữ liệu git diff hiển thị những gì đã thay đổi

Gợi ý hệ thống nói với AI _cách_ viết thông điệp commit, trong khi gợi ý người dùng cung cấp _cái gì_ (thay đổi mã thực tế).

## Tại Sao Sử Dụng Gợi Ý Hệ Thống Tùy Chỉnh?

Bạn có thể muốn gợi ý hệ thống tùy chỉnh nếu:

- Đội của bạn sử dụng kiểu thông điệp commit khác với commit tiêu chuẩn
- Bạn thích emojis, tiền tố, hoặc các định dạng tùy chỉnh khác
- Bạn muốn ít hoặc nhiều chi tiết hơn trong thông điệp commit
- Bạn có hướng dẫn hoặc mẫu cụ thể cho công ty
- Bạn muốn khớp với giọng điệu và phong cách của đội bạn
- Bạn muốn thông điệp commit bằng ngôn ngữ khác (xem Cấu Hình Ngôn Ngữ dưới đây)

## Bắt Đầu Nhanh

1. **Tạo tệp gợi ý hệ thống tùy chỉnh của bạn:**

   ```bash
   # Sao chép ví dụ làm điểm bắt đầu
   cp ../../examples/custom_system_prompt.example.vi.txt ~/.config/gac/my_system_prompt.txt

   # Hoặc tạo của riêng bạn từ đầu
   vim ~/.config/gac/my_system_prompt.txt
   ```

2. **Thêm vào tệp `.gac.env` của bạn:**

   ```bash
   # Trong ~/.gac.env hoặc .gac.env cấp dự án
   GAC_SYSTEM_PROMPT_PATH=/path/to/your/custom_system_prompt.txt
   ```

3. **Kiểm tra nó:**

   ```bash
   gac --dry-run
   ```

Chỉ vậy thôi! GAC bây giờ sẽ sử dụng hướng dẫn tùy chỉnh của bạn thay vì mặc định.

## Viết Gợi Ý Hệ Thống Tùy Chỉnh Của Bạn

Gợi ý hệ thống tùy chỉnh của bạn có thể là văn bản thuần túy—không cần định dạng hoặc thẻ XML đặc biệt. Chỉ cần viết hướng dẫn rõ ràng cho cách AI nên tạo thông điệp commit.

**Những điều chính yếu cần bao gồm:**

1. **Định nghĩa vai trò** - AI nên hành động như thế nào
2. **Yêu cầu định dạng** - Cấu trúc, độ dài, kiểu
3. **Ví dụ** - Hiển thị thông điệp commit tốt trông như thế nào
4. **Ràng buộc** - Những gì cần tránh hoặc yêu cầu để đáp ứng

**Cấu trúc ví dụ:**

```text
Bạn là người viết thông điệp commit cho [dự án/đội ngũ của bạn].

Khi phân tích các thay đổi mã, tạo thông điệp commit mà:

1. [Yêu cầu đầu tiên]
2. [Yêu cầu thứ hai]
3. [Yêu cầu thứ ba]

Định dạng ví dụ:
[Hiển thị ví dụ thông điệp commit]

Toàn bộ phản hồi của bạn sẽ được sử dụng trực tiếp làm thông điệp commit.
```

## Ví Dụ

### Kiểu Commit Dựa Trên Emoji

Xem [`custom_system_prompt.example.vi.txt`](../../examples/custom_system_prompt.example.vi.txt) cho ví dụ hoàn chỉnh dựa trên emoji.

**Đoạn ngắn:**

```text
Bạn là người viết thông điệp commit sử dụng emojis và giọng điệu thân thiện.

Bắt đầu mỗi thông điệp với một emoji:
- 🎉 cho các tính năng mới
- 🐛 cho các sửa lỗi
- 📝 cho tài liệu
- ♻️ cho tái cấu trúc

Giữ dòng đầu tiên dưới 72 ký tự và giải thích TẠI SAO thay đổi quan trọng.
```

### Quy Ước Cụ Thể Đội Vụ

```text
Bạn đang viết thông điệp commit cho ứng dụng ngân hàng doanh nghiệp.

Yêu cầu:
1. Bắt đầu với số vé JIRA trong ngoặc (ví dụ, [BANK-1234])
2. Sử dụng giọng điệu trang trọng, chuyên nghiệp
3. Bao gồm các tác động bảo mật nếu có liên quan
4. Tham khảo các yêu cầu tuân thủ (PCI-DSS, SOC2, v.v.)
5. Giữ thông điệp ngắn gọn nhưng hoàn chỉnh

Định dạng:
[TICKET-123] Tóm tắt ngắn gọn của thay đổi

Giải thích chi tiết những gì đã thay đổi và tại sao. Bao gồm:
- Lý do kinh doanh
- Cách tiếp cận kỹ thuật
- Đánh giá rủi ro (nếu có)

Ví dụ:
[BANK-1234] Triển khai giới hạn tốc độ cho các endpoint đăng nhập

Thêm giới hạn tốc độ dựa trên Redis để ngăn chặn các tấn công brute force.
Giới hạn các nỗ lực đăng nhập thành 5 mỗi IP mỗi 15 phút.
Tuân thủ yêu cầu bảo mật SOC2 cho kiểm soát truy cập.
```

### Kiểu Kỹ Thuật Chi Tiết

```text
Bạn là người viết thông điệp commit kỹ thuật tạo tài liệu toàn diện.

Đối với mỗi commit, cung cấp:

1. Tiêu đề rõ ràng, mô tả (dưới 72 ký tự)
2. Một dòng trống
3. CÁI GÌ: Điều gì đã thay đổi (2-3 câu)
4. TẠI SAO: Tại sao thay đổi là cần thiết (2-3 câu)
5. NHƯ THẾ NÀO: Cách tiếp cận kỹ thuật hoặc các chi tiết triển khai chính
6. TÁC ĐỘNG: Các tệp/thành phần bị ảnh hưởng và các tác động phụ tiềm tàng

Sử dụng độ chính xác kỹ thuật. Tham khảo các hàm, lớp và module cụ thể.
Sử dụng thì hiện tại và chủ động.

Ví dụ:
Tái cấu trúc middleware xác thực để sử dụng tiêm phụ thuộc

CÁI GÌ: Thay thế trạng thái xác thực tổng thể với AuthService có thể tiêm. Cập nhật
tất cả các trình xử lý tuyến đường để chấp nhận AuthService qua tiêm hàm tạo.

TẠI SAO: Trạng thái tổng thể làm cho việc kiểm tra khó khăn và tạo ra các phụ thuộc ẩn.
Tiêm phụ thuộc cải thiện khả năng kiểm thử và làm cho các phụ thuộc rõ ràng.

NHƯ THẾ NÀO: Tạo giao diện AuthService, triển khai JWTAuthService và
MockAuthService. Sửa đổi hàm tạo trình xử lý tuyến đường để yêu cầu AuthService.
Cập nhật cấu hình container tiêm phụ thuộc.

TÁC ĐỘNG: Ảnh hưởng đến tất cả các tuyến đường được xác thực. Không có thay đổi hành vi cho người dùng.
Kiểm thử hiện chạy nhanh hơn 3x với MockAuthService. Di chuyển cần thiết cho
routes/auth.ts, routes/api.ts và routes/admin.ts.
```

## Thực Hành Tốt Nhất

### Nên

- ✅ **Cụ thể** - Hướng dẫn rõ ràng tạo ra kết quả tốt hơn
- ✅ **Bao gồm ví dụ** - Hiển thị cho AI thấy trông tốt như thế nào
- ✅ **Kiểm tra lặp lại** - Thử gợi ý của bạn, tinh chỉnh dựa trên kết quả
- ✅ **Giữ nó tập trung** - Quá nhiều quy tắc có thể làm AI bối rối
- ✅ **Sử dụng thuật ngữ nhất quán** - Bám sát các thuật ngữ giống nhau trong suốt
- ✅ **Kết thúc với lời nhắc nhở** - Củng cố rằng phản hồi sẽ được sử dụng nguyên trạng

### Không Nên

- ❌ **Sử dụng thẻ XML** - Văn bản thuần túy hoạt động tốt nhất (trừ khi bạn muốn cấu trúc đó cụ thể)
- ❌ **Làm nó quá dài** - Nhắm đến 200-500 từ hướng dẫn
- ❌ **Mâu thuẫn với chính mình** - Nhất quán trong các yêu cầu của bạn
- ❌ **Quên phần kết thúc** - Luôn nhắc nhở: "Toàn bộ phản hồi của bạn sẽ được sử dụng trực tiếp làm thông điệp commit"

### Mẹo

- **Bắt đầu với ví dụ** - Sao chép `../../examples/custom_system_prompt.example.vi.txt` và sửa đổi nó
- **Kiểm tra với `--dry-run`** - Xem kết quả mà không thực hiện commit
- **Sử dụng `--show-prompt`** - Xem những gì đang được gửi đến AI
- **Lặp lại dựa trên kết quả** - Nếu thông điệp chưa đúng, điều chỉnh hướng dẫn của bạn
- **Kiểm soát phiên bản gợi ý của bạn** - Giữ gợi ý tùy chỉnh của bạn trong kho của đội bạn
- **Gợi ý cụ thể dự án** - Sử dụng .gac.env cấp dự án cho các kiểu cụ thể dự án

## Xử Lý Sự Cố

### Thông Điệp Vẫn Có Tiền Tố "chore:"

**Vấn đề:** Các thông điệp emoji tùy chỉnh của bạn đang nhận được "chore:" được thêm vào.

**Giải pháp:** Điều này không nên xảy ra—GAC tự động vô hiệu hóa thực thi commit tiêu chuẩn khi sử dụng gợi ý hệ thống tùy chỉnh. Nếu bạn thấy điều này, vui lòng [tạo vấn đề](https://github.com/cellwebb/gac/issues).

### AI Bỏ Qua Hướng Dẫn Của Tôi

**Vấn đề:** Các thông điệp đã tạo không làm theo định dạng tùy chỉnh của bạn.

**Giải pháp:**

1. Làm cho hướng dẫn của bạn rõ ràng và cụ thể hơn
2. Thêm các ví dụ rõ ràng về định dạng mong muốn
3. Kết thúc với: "Toàn bộ phản hồi của bạn sẽ được sử dụng trực tiếp làm thông điệp commit"
4. Giảm số lượng yêu cầu—quá nhiều có thể làm AI bối rối
5. Thử sử dụng mô hình khác (một số làm theo hướng dẫn tốt hơn những mô hình khác)

### Thông Điệp Quá Dài/Ngắn

**Vấn đề:** Các thông điệp đã tạo không khớp với yêu cầu độ dài của bạn.

**Giải pháp:**

- Rõ ràng về độ dài (ví dụ, "Giữ thông điệp dưới 50 ký tự")
- Hiển thị ví dụ về độ dài chính xác bạn muốn
- Cân nhắc sử dụng flag `--one-liner` cũng cho các thông điệp ngắn

### Gợi Ý Tùy Chỉnh Không Được Sử Dụng

**Vấn đề:** GAC vẫn sử dụng định dạng commit mặc định.

**Giải pháp:**

1. Kiểm tra rằng `GAC_SYSTEM_PROMPT_PATH` được đặt đúng:

   ```bash
   gac config get GAC_SYSTEM_PROMPT_PATH
   ```

2. Xác minh đường dẫn tệp tồn tại và có thể đọc:

   ```bash
   cat "$GAC_SYSTEM_PROMPT_PATH"
   ```

3. Kiểm tra các tệp .gac.env theo thứ tự này:
   - Cấp dự án: `./.gac.env`
   - Cấp người dùng: `~/.gac.env`
4. Thử đường dẫn tuyệt đối thay vì đường dẫn tương đối

### Cấu Hình Ngôn Ngữ

**Lưu ý:** Bạn không cần gợi ý hệ thống tùy chỉnh để thay đổi ngôn ngữ thông điệp commit!

Nếu bạn chỉ muốn thay đổi ngôn ngữ của thông điệp commit (trong khi giữ định dạng commit tiêu chuẩn), sử dụng trình chọn ngôn ngữ tương tác:

```bash
gac language
```

Điều này sẽ trình bày menu tương tác với 25+ ngôn ngữ trong chữ viết gốc của chúng (Español, Français, 日本語, v.v.). Chọn ngôn ngữ ưa thích của bạn, và nó sẽ tự động đặt `GAC_LANGUAGE` trong tệp `~/.gac.env` của bạn.

Ngoài ra, bạn có thể đặt ngôn ngữ thủ công:

```bash
# Trong ~/.gac.env hoặc .gac.env cấp dự án
GAC_LANGUAGE=Spanish
```

Theo mặc định, các tiền tố commit tiêu chuẩn (feat:, fix:, v.v.) vẫn bằng tiếng Anh để tương thích với công cụ changelog và đường ống CI/CD, trong khi tất cả văn bản khác là bằng ngôn ngữ bạn chỉ định.

**Muốn dịch tiền tố cũng?** Đặt `GAC_TRANSLATE_PREFIXES=true` trong `.gac.env` của bạn để bản địa hóa đầy đủ:

```bash
GAC_LANGUAGE=Spanish
GAC_TRANSLATE_PREFIXES=true
```

Điều này sẽ dịch mọi thứ, bao gồm cả tiền tố (ví dụ, `corrección:` thay vì `fix:`).

Điều này đơn giản hơn việc tạo gợi ý hệ thống tùy chỉnh nếu ngôn ngữ là nhu cầu tùy chỉnh duy nhất của bạn.

### Muốn Chuyển Lại Về Mặc Định

**Vấn đề:** Muốn sử dụng gợi ý mặc định tạm thời.

**Giải pháp:**

```bash
# Tùy chọn 1: Bỏ đặt biến môi trường
gac config unset GAC_SYSTEM_PROMPT_PATH

# Tùy chọn 2: Ghi chú nó ra trong .gac.env
# GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt

# Tùy chọn 3: Sử dụng .gac.env khác cho các dự án cụ thể
```

---

## Tài Liệu Liên Quan

- [USAGE.md](USAGE.md) - Các flag và tùy chọn dòng lệnh
- [README.md](../../README.md) - Cài đặt và thiết lập cơ bản
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Xử lý sự cố chung

## Cần Trợ Giúp?

- Báo cáo vấn đề: [GitHub Issues](https://github.com/cellwebb/gac/issues)
- Chia sẻ gợi ý tùy chỉnh của bạn: Đóng góp được hoan nghênh!
