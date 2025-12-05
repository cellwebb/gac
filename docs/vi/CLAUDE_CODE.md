# Sử dụng Claude Code với GAC

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | **Tiếng Việt** | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC hỗ trợ xác thực qua đăng ký Claude Code, cho phép bạn sử dụng đăng ký Claude Code của mình thay vì trả cho API Anthropic đắt tiền. Điều này hoàn hảo cho những người dùng đã có quyền truy cập Claude Code qua đăng ký của họ.

## Claude Code là gì?

Claude Code là dịch vụ đăng ký của Anthropic cung cấp quyền truy cập Claude mô hình dựa trên OAuth. Thay vì sử dụng khóa API (được tính phí theo token), Claude Code sử dụng token OAuth từ đăng ký của bạn.

## Lợi ích

- **Hiệu quả về chi phí**: Sử dụng đăng ký Claude Code hiện có của bạn thay vì trả riêng cho quyền truy cập API
- **Cùng mô hình**: Truy cập các mô hình Claude tương tự (ví dụ: `claude-sonnet-4-5`)
- **Thanh toán riêng biệt**: Việc sử dụng Claude Code tách biệt với thanh toán API Anthropic

## Cài đặt

GAC bao gồm xác thực OAuth tích hợp cho Claude Code. Quá trình cài đặt được tự động hóa hoàn toàn và sẽ mở trình duyệt của bạn để xác thực.

### Tùy chọn 1: Trong quá trình cài đặt ban đầu (Khuyến nghị)

Khi chạy `gac init`, chỉ cần chọn "Claude Code" làm nhà cung cấp của bạn:

```bash
gac init
```

Trình hướng dẫn sẽ:

1. Yêu cầu bạn chọn "Claude Code" từ danh sách nhà cung cấp
2. Tự động mở trình duyệt của bạn để xác thực OAuth
3. Lưu token truy cập của bạn vào `~/.gac.env`
4. Đặt mô hình mặc định

### Tùy chọn 2: Chuyển sang Claude Code sau

Nếu bạn đã cấu hình GAC với nhà cung cấp khác và muốn chuyển sang Claude Code:

```bash
gac model
```

Sau đó:

1. Chọn "Claude Code" từ danh sách nhà cung cấp
2. Trình duyệt của bạn sẽ tự động mở để xác thực OAuth
3. Token được lưu vào `~/.gac.env`
4. Mô hình được cấu hình tự động

### Sử dụng GAC bình thường

Sau khi xác thực, sử dụng GAC như bình thường:

```bash
# Stage các thay đổi của bạn
git add .

# Tạo và commit với Claude Code
gac

# Hoặc ghi đè mô hình cho một commit duy nhất
gac -m claude-code:claude-sonnet-4-5
```

## Các mô hình có sẵn

Claude Code cung cấp quyền truy cập vào các mô hình tương tự như API Anthropic. Các mô hình gia đình Claude 4.5 hiện tại bao gồm:

- `claude-sonnet-4-5` - Mô hình Sonnet mới nhất và thông minh nhất, tốt nhất cho lập trình
- `claude-haiku-4-5` - Nhanh và hiệu quả
- `claude-opus-4-5` - Mô hình có khả năng nhất cho lý luận phức tạp

Xem [tài liệu Claude](https://docs.claude.com/en/docs/about-claude/models/overview) để có danh sách đầy đủ các mô hình có sẵn.

## Xử lý sự cố

### Token hết hạn

Nếu bạn thấy lỗi xác thực, token của bạn có thể đã hết hạn. Xác thực lại bằng cách chạy:

```bash
gac auth claude-code login
```

Trình duyệt của bạn sẽ tự động mở để xác thực OAuth mới. Ngoài ra, bạn có thể chạy `gac model`, chọn "Claude Code (OAuth)" và chọn "Xác thực lại (lấy token mới)".

### Kiểm tra trạng thái xác thực

Để kiểm tra xem bạn hiện đang được xác thực hay không:

```bash
gac auth claude-code status
```

Hoặc kiểm tra tất cả các nhà cung cấp cùng lúc:

```bash
gac auth
```

### Đăng xuất

Để xóa token đã lưu của bạn:

```bash
gac auth claude-code logout
```

### "Không tìm thấy CLAUDE_CODE_ACCESS_TOKEN"

Điều này có nghĩa là GAC không thể tìm thấy token truy cập của bạn. Xác thực bằng cách chạy:

```bash
gac model
```

Sau đó chọn "Claude Code" từ danh sách nhà cung cấp. Quy trình OAuth sẽ bắt đầu tự động.

### "Xác thực thất bại"

Nếu xác thực OAuth thất bại:

1. Đảm bảo bạn có đăng ký Claude Code hoạt động
2. Kiểm tra trình duyệt của bạn mở đúng cách
3. Thử trình duyệt khác nếu sự cố tiếp diễn
4. Xác minh kết nối mạng đến `claude.ai`
5. Kiểm tra các cổng 8765-8795 có sẵn cho máy chủ callback cục bộ

## Khác biệt so với nhà cung cấp Anthropic

| Tính năng     | Anthropic (`anthropic:`)       | Claude Code (`claude-code:`)                              |
| ------------- | ------------------------------ | --------------------------------------------------------- |
| Xác thực      | Khóa API (`ANTHROPIC_API_KEY`) | OAuth (quy trình trình duyệt tự động)                     |
| Thanh toán    | Thanh toán API theo token      | Dựa trên đăng ký                                          |
| Cài đặt       | Nhập khóa API thủ công         | OAuth tự động qua `gac init` hoặc `gac model`             |
| Quản lý token | Khóa API dài hạn               | Token OAuth (có thể hết hạn, dễ xác thực lại qua `model`) |
| Mô hình       | Cùng mô hình                   | Cùng mô hình                                              |

## Ghi chú bảo mật

- **Không bao giờ commit token truy cập của bạn** vào kiểm soát phiên bản
- GAC tự động lưu trữ token trong `~/.gac.env` (ngoài thư mục dự án của bạn)
- Token có thể hết hạn và sẽ yêu cầu xác thực lại qua `gac model`
- Quy trình OAuth sử dụng PKCE (Proof Key for Code Exchange) để tăng cường bảo mật
- Máy chủ callback cục bộ chỉ chạy trên localhost (cổng 8765-8795)

## Xem thêm

- [Tài liệu chính](USAGE.md)
- [Thiết lập và xác thực Qwen.ai](QWEN.md)
- [Hướng dẫn xử lý sự cố](TROUBLESHOOTING.md)
- [Tài liệu Claude Code](https://claude.ai/code)
