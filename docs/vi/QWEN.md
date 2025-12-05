[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | **Tiếng Việt** | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# Sử dụng Qwen.ai với GAC

GAC hỗ trợ xác thực qua Qwen.ai OAuth, cho phép bạn sử dụng tài khoản Qwen.ai của mình để tạo thông điệp commit. Tính năng này sử dụng xác thực luồng thiết bị OAuth để có trải nghiệm đăng nhập liền mạch.

## Qwen.ai là gì?

Qwen.ai là nền tảng AI của Alibaba Cloud cung cấp quyền truy cập vào dòng mô hình ngôn ngữ lớn Qwen. GAC hỗ trợ xác thực dựa trên OAuth, cho phép bạn sử dụng tài khoản Qwen.ai của mình mà không cần quản lý khóa API theo cách thủ công.

## Lợi ích

- **Xác thực dễ dàng**: Luồng thiết bị OAuth - chỉ cần đăng nhập bằng trình duyệt của bạn
- **Không cần quản lý khóa API**: Xác thực được xử lý tự động
- **Truy cập các mô hình Qwen**: Sử dụng các mô hình Qwen mạnh mẽ để tạo thông điệp commit

## Thiết lập

GAC bao gồm xác thực OAuth tích hợp cho Qwen.ai sử dụng luồng thiết bị. Quá trình thiết lập sẽ hiển thị mã và mở trình duyệt của bạn để xác thực.

### Tùy chọn 1: Trong quá trình thiết lập ban đầu (Khuyên dùng)

Khi chạy `gac init`, chỉ cần chọn "Qwen.ai (OAuth)" làm nhà cung cấp của bạn:

```bash
gac init
```

Trình hướng dẫn sẽ:

1. Yêu cầu bạn chọn "Qwen.ai (OAuth)" từ danh sách nhà cung cấp
2. Hiển thị mã thiết bị và mở trình duyệt của bạn
3. Bạn sẽ xác thực trên Qwen.ai và nhập mã
4. Lưu mã thông báo truy cập của bạn một cách an toàn
5. Đặt mô hình mặc định

### Tùy chọn 2: Chuyển sang Qwen.ai sau

Nếu bạn đã định cấu hình GAC với nhà cung cấp khác và muốn chuyển sang Qwen.ai:

```bash
gac model
```

Sau đó:

1. Chọn "Qwen.ai (OAuth)" từ danh sách nhà cung cấp
2. Làm theo luồng xác thực mã thiết bị
3. Mã thông báo được lưu an toàn vào `~/.gac/oauth/qwen.json`
4. Mô hình được định cấu hình tự động

### Tùy chọn 3: Đăng nhập trực tiếp

Bạn cũng có thể xác thực trực tiếp bằng cách sử dụng:

```bash
gac auth qwen login
```

Thao tác này sẽ:

1. Hiển thị mã thiết bị
2. Mở trình duyệt của bạn đến trang xác thực Qwen.ai
3. Sau khi bạn xác thực, mã thông báo sẽ được lưu tự động

### Sử dụng GAC bình thường

Sau khi xác thực, hãy sử dụng GAC như bình thường:

```bash
# Chuẩn bị các thay đổi của bạn
git add .

# Tạo và commit bằng Qwen.ai
gac

# Hoặc ghi đè mô hình cho một commit duy nhất
gac -m qwen:qwen3-coder-plus
```

## Các mô hình có sẵn

Tích hợp Qwen.ai OAuth sử dụng:

- `qwen3-coder-plus` - Được tối ưu hóa cho các tác vụ mã hóa (mặc định)

Đây là mô hình có sẵn thông qua điểm cuối OAuth portal.qwen.ai. Đối với các mô hình Qwen khác, hãy cân nhắc sử dụng nhà cung cấp OpenRouter cung cấp các tùy chọn mô hình Qwen bổ sung.

## Lệnh xác thực

GAC cung cấp một số lệnh để quản lý xác thực Qwen.ai:

```bash
# Đăng nhập vào Qwen.ai
gac auth qwen login

# Kiểm tra trạng thái xác thực
gac auth qwen status

# Đăng xuất và xóa mã thông báo đã lưu
gac auth qwen logout

# Kiểm tra trạng thái tất cả các nhà cung cấp OAuth
gac auth
```

### Tùy chọn đăng nhập

```bash
# Đăng nhập tiêu chuẩn (tự động mở trình duyệt)
gac auth qwen login

# Đăng nhập không mở trình duyệt (hiển thị URL để truy cập thủ công)
gac auth qwen login --no-browser

# Chế độ im lặng (đầu ra tối thiểu)
gac auth qwen login --quiet
```

## Khắc phục sự cố

### Mã thông báo hết hạn

Nếu bạn thấy lỗi xác thực, mã thông báo của bạn có thể đã hết hạn. Xác thực lại bằng cách chạy:

```bash
gac auth qwen login
```

Luồng mã thiết bị sẽ bắt đầu và trình duyệt của bạn sẽ mở để xác thực lại.

### Kiểm tra trạng thái xác thực

Để kiểm tra xem bạn hiện đã được xác thực chưa:

```bash
gac auth qwen status
```

Hoặc kiểm tra tất cả các nhà cung cấp cùng một lúc:

```bash
gac auth
```

### Đăng xuất

Để xóa mã thông báo đã lưu của bạn:

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (Không tìm thấy xác thực Qwen)

Điều này có nghĩa là GAC không thể tìm thấy mã thông báo truy cập của bạn. Xác thực bằng cách chạy:

```bash
gac auth qwen login
```

Hoặc chạy `gac model` và chọn "Qwen.ai (OAuth)" từ danh sách nhà cung cấp.

### "Authentication failed" (Xác thực không thành công)

Nếu xác thực OAuth không thành công:

1. Đảm bảo bạn có tài khoản Qwen.ai
2. Kiểm tra xem trình duyệt của bạn có mở chính xác không
3. Xác minh bạn đã nhập mã thiết bị chính xác
4. Thử một trình duyệt khác nếu sự cố vẫn tiếp diễn
5. Xác minh kết nối mạng đến `qwen.ai`

### Mã thiết bị không hoạt động

Nếu xác thực mã thiết bị không hoạt động:

1. Đảm bảo mã chưa hết hạn (mã có hiệu lực trong thời gian giới hạn)
2. Thử chạy lại `gac auth qwen login` để lấy mã mới
3. Sử dụng cờ `--no-browser` và truy cập URL thủ công nếu mở trình duyệt không thành công

## Ghi chú bảo mật

- **Không bao giờ commit mã thông báo truy cập của bạn** vào kiểm soát phiên bản
- GAC tự động lưu trữ mã thông báo trong `~/.gac/oauth/qwen.json` (bên ngoài thư mục dự án của bạn)
- Các tệp mã thông báo có quyền hạn chế (chỉ chủ sở hữu mới có thể đọc)
- Mã thông báo có thể hết hạn và sẽ yêu cầu xác thực lại
- Luồng thiết bị OAuth được thiết kế để xác thực an toàn trên các hệ thống không có màn hình

## Xem thêm

- [Tài liệu chính](USAGE.md)
- [Thiết lập Claude Code](CLAUDE_CODE.md)
- [Hướng dẫn khắc phục sự cố](TROUBLESHOOTING.md)
- [Tài liệu Qwen.ai](https://qwen.ai)
