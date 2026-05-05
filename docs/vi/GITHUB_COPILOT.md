# Sử dụng GitHub Copilot với GAC

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | **Tiếng Việt** | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC hỗ trợ xác thực qua GitHub Copilot, cho phép bạn sử dụng gói đăng ký Copilot để truy cập các mô hình từ OpenAI, Anthropic, Google và nhiều hơn nữa — tất cả đều được bao gồm trong gói GitHub Copilot của bạn.

## GitHub Copilot OAuth là gì?

GitHub Copilot OAuth sử dụng **Device Flow** — một phương thức xác thực dựa trên trình duyệt an toàn, không yêu cầu máy chủ callback cục bộ. Bạn truy cập một URL, nhập mã một lần và ủy quyền GAC sử dụng quyền truy cập Copilot của bạn. Đằng sau hậu trường, GAC trao đổi token OAuth GitHub tồn tại lâu của bạn lấy các token phiên Copilot tồn tại ngắn (~30 phút) cấp quyền truy cập vào API Copilot.

Điều này cho phép bạn truy cập các mô hình từ nhiều nhà cung cấp thông qua một gói đăng ký duy nhất:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Lợi ích

- **Truy cập nhiều nhà cung cấp**: Sử dụng các mô hình từ OpenAI, Anthropic và Google thông qua một gói đăng ký duy nhất
- **Hiệu quả chi phí**: Sử dụng gói đăng ký Copilot hiện có thay vì trả tiền riêng cho các khóa API
- **Không cần quản lý khóa API**: Xác thực Device Flow — không cần xoay hoặc lưu trữ khóa
- **Hỗ trợ GitHub Enterprise**: Hoạt động với các phiên bản GHE qua flag `--host`

## Thiết lập

### Tùy chọn 1: Trong quá trình thiết lập ban đầu (Khuyến nghị)

Khi chạy `gac init`, chỉ cần chọn "Copilot" làm nhà cung cấp của bạn:

```bash
gac init
```

Trình hướng dẫn sẽ:

1. Yêu cầu bạn chọn "Copilot" từ danh sách nhà cung cấp
2. Hiển thị mã một lần và mở trình duyệt của bạn để xác thực Device Flow
3. Lưu token OAuth của bạn vào `~/.gac/oauth/copilot.json`
4. Đặt mô hình mặc định

### Tùy chọn 2: Chuyển sang Copilot sau

Nếu bạn đã cấu hình GAC với một nhà cung cấp khác:

```bash
gac model
```

Sau đó chọn "Copilot" từ danh sách nhà cung cấp và xác thực.

### Tùy chọn 3: Đăng nhập trực tiếp

Xác thực trực tiếp mà không thay đổi mô hình mặc định của bạn:

```bash
gac auth copilot login
```

### Sử dụng GAC bình thường

Sau khi xác thực, sử dụng GAC như bình thường:

```bash
# Stage các thay đổi của bạn
git add .

# Tạo và commit với Copilot
gac

# Hoặc ghi đè mô hình cho một commit duy nhất
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Các mô hình có sẵn

Copilot cung cấp quyền truy cập vào các mô hình từ nhiều nhà cung cấp. Các mô hình hiện tại bao gồm:

| Nhà cung cấp | Mô hình                                                                                        |
| ------------ | ---------------------------------------------------------------------------------------------- |
| OpenAI       | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic    | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google       | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Lưu ý:** Danh sách mô hình hiển thị sau khi đăng nhập chỉ mang tính thông tin và có thể lỗi thời khi GitHub thêm các mô hình mới. Kiểm tra [tài liệu GitHub Copilot](https://docs.github.com/en/copilot) để xem các mô hình có sẵn mới nhất.

## GitHub Enterprise

Để xác thực với một phiên bản GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC sẽ tự động sử dụng các endpoint Device Flow và API chính xác cho phiên bản GHE của bạn. Token phiên được lưu theo host, do đó các phiên bản GHE khác nhau được xử lý độc lập.

## Lệnh CLI

GAC cung cấp các lệnh CLI chuyên dụng để quản lý xác thực Copilot:

### Đăng nhập

Xác thực hoặc xác thực lại với GitHub Copilot:

```bash
gac auth copilot login
```

Trình duyệt của bạn sẽ mở trang Device Flow nơi bạn nhập mã một lần. Nếu bạn đã được xác thực, bạn sẽ được hỏi có muốn xác thực lại hay không.

Đối với GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Đăng xuất

Xóa các token Copilot đã lưu:

```bash
gac auth copilot logout
```

Thao tác này xóa tệp token đã lưu tại `~/.gac/oauth/copilot.json` và bộ nhớ đệm phiên.

### Trạng thái

Kiểm tra trạng thái xác thực Copilot hiện tại của bạn:

```bash
gac auth copilot status
```

Hoặc kiểm tra tất cả các nhà cung cấp cùng một lúc:

```bash
gac auth
```

## Cách hoạt động

Quy trình xác thực Copilot khác với ChatGPT và Claude Code OAuth:

1. **Device Flow** — GAC yêu cầu mã thiết bị từ GitHub và hiển thị nó
2. **Ủy quyền trình duyệt** — Bạn truy cập URL và nhập mã
3. **Polling token** — GAC polling GitHub cho đến khi bạn hoàn tất ủy quyền
4. **Trao đổi token phiên** — Token OAuth GitHub được trao đổi lấy token phiên Copilot tồn tại ngắn
5. **Tự động làm mới** — Token phiên (~30 phút) được tự động làm mới từ token OAuth đã lưu

Khác với OAuth dựa trên PKCE (ChatGPT/Claude Code), Device Flow không yêu cầu máy chủ callback cục bộ hoặc quản lý cổng.

## Khắc phục sự cố

### «Không tìm thấy xác thực Copilot»

Chạy lệnh đăng nhập để xác thực:

```bash
gac auth copilot login
```

### «Không thể lấy token phiên Copilot»

Điều này có nghĩa là GAC đã nhận được token OAuth GitHub nhưng không thể trao đổi nó lấy token phiên Copilot. Thường thì điều này có nghĩa là:

1. **Không có gói đăng ký Copilot** — Tài khoản GitHub của bạn không có gói đăng ký Copilot đang hoạt động
2. **Token bị thu hồi** — Token OAuth đã bị thu hồi; xác thực lại với `gac auth copilot login`

### Token phiên hết hạn

Token phiên hết hạn sau khoảng 30 phút. GAC tự động làm mới chúng từ token OAuth đã lưu, do đó bạn không cần xác thực lại thường xuyên. Nếu tự động làm mới thất bại:

```bash
gac auth copilot login
```

### «Tên máy chủ không hợp lệ hoặc không an toàn»

Flag `--host` xác thực tên máy chủ một cách nghiêm ngặt để ngăn chặn các cuộc tấn công SSRF. Nếu bạn thấy lỗi này:

- Đảm bảo tên máy chủ không bao gồm cổng (ví dụ: sử dụng `ghe.company.com` không phải `ghe.company.com:8080`)
- Không bao gồm giao thức hoặc đường dẫn (ví dụ: sử dụng `ghe.company.com` không phải `https://ghe.company.com/api`)
- Địa chỉ IP riêng và `localhost` bị chặn vì lý do bảo mật

### Vấn đề GitHub Enterprise

Nếu xác thực GHE thất bại:

1. Xác minh rằng phiên bản GHE của bạn đã bật Copilot
2. Kiểm tra tên máy chủ GHE của bạn có thể truy cập được từ máy của bạn
3. Đảm bảo tài khoản GHE của bạn có giấy phép Copilot
4. Thử với flag `--host` một cách rõ ràng: `gac auth copilot login --host ghe.mycompany.com`

## Sự khác biệt so với các nhà cung cấp OAuth khác

| Tính năng            | ChatGPT OAuth                 | Claude Code                 | Copilot                                          |
| -------------------- | ----------------------------- | --------------------------- | ------------------------------------------------ |
| Phương thức xác thực | PKCE (callback trình duyệt)   | PKCE (callback trình duyệt) | Device Flow (mã một lần)                         |
| Máy chủ callback     | Cổng 1455-1465                | Cổng 8765-8795              | Không cần                                        |
| Thời gian sống token | Tồn tại lâu (tự động làm mới) | Hết hạn (xác thực lại)      | Phiên ~30 phút (tự động làm mới)                 |
| Mô hình              | OpenAI tối ưu Codex           | Họ Claude                   | Nhiều nhà cung cấp (OpenAI + Anthropic + Google) |
| Hỗ trợ GHE           | Không                         | Không                       | Có (flag `--host`)                               |

## Lưu ý bảo mật

- **Không bao giờ commit token OAuth của bạn** vào kiểm soát phiên bản
- GAC lưu trữ token OAuth trong `~/.gac/oauth/copilot.json` (bên ngoài thư mục dự án của bạn)
- Token phiên được lưu trong `~/.gac/oauth/copilot_session.json` với quyền `0o600`
- Tên máy chủ được xác thực nghiêm ngặt để ngăn chặn các cuộc tấn công SSRF và chèn URL
- Địa chỉ IP riêng, địa chỉ loopback và `localhost` bị chặn làm tên máy chủ
- Device Flow không mở bất kỳ cổng cục bộ nào, giảm bề mặt tấn công

## Xem thêm

- [Tài liệu chính](USAGE.md)
- [Hướng dẫn khắc phục sự cố](TROUBLESHOOTING.md)
- [Hướng dẫn ChatGPT OAuth](CHATGPT_OAUTH.md)
- [Hướng dẫn Claude Code](CLAUDE_CODE.md)
- [Tài liệu GitHub Copilot](https://docs.github.com/en/copilot)
