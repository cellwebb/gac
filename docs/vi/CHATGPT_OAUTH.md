# Sử dụng ChatGPT OAuth với GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC hỗ trợ xác thực qua ChatGPT OAuth, cho phép bạn sử dụng gói đăng ký ChatGPT của mình để truy cập API Codex của OpenAI thay vì phải trả tiền riêng cho các khóa API OpenAI. Điều này phản ánh cùng luồng OAuth được sử dụng bởi Codex CLI của OpenAI.

> ⚠️ **Lưu ý — sử dụng không được phê duyệt:** Điều này sử dụng cùng luồng OAuth với Codex CLI của OpenAI, và mặc dù hiện tại nó hoạt động, OpenAI có thể hạn chế việc sử dụng token của bên thứ ba bất cứ lúc nào. GAC đủ nhỏ để đến nay vẫn chưa bị chú ý, nhưng việc sử dụng ChatGPT OAuth ở đây **không được chính thức phê duyệt** cho các công cụ bên thứ ba và có thể ngừng hoạt động bất cứ lúc nào. Nếu bạn cần tạo thông báo commit đáng tin cậy, hãy sử dụng nhà cung cấp API trực tiếp (`openai`, v.v.). Xem [tài liệu Codex của OpenAI](https://openai.com/codex) để biết chính sách hiện tại.

## ChatGPT OAuth là gì?

ChatGPT OAuth cho phép bạn tận dụng gói đăng ký ChatGPT Plus hoặc Pro hiện có của mình để truy cập API Codex nhằm tạo thông báo commit. Thay vì quản lý các khóa API và thanh toán theo token, bạn xác thực một lần qua trình duyệt và GAC sẽ tự động xử lý vòng đời token.

## Lợi ích

- **Hiệu quả chi phí**: Sử dụng gói đăng ký ChatGPT Plus/Pro hiện có của bạn thay vì phải trả tiền riêng cho quyền truy cập API
- **Cùng các mô hình**: Truy cập các mô hình tối ưu hóa Codex (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **Không cần quản lý khóa API**: OAuth dựa trên trình duyệt có nghĩa là không cần xoay hoặc lưu trữ khóa API
- **Thanh toán riêng biệt**: Việc sử dụng ChatGPT OAuth được tách riêng khỏi thanh toán API OpenAI trực tiếp

## Thiết lập

GAC bao gồm xác thực OAuth tích hợp cho ChatGPT. Quy trình thiết lập hoàn toàn tự động và sẽ mở trình duyệt của bạn để xác thực.

### Tùy chọn 1: Trong quá trình thiết lập ban đầu (Khuyến nghị)

Khi chạy `gac init`, chỉ cần chọn "ChatGPT OAuth" làm nhà cung cấp của bạn:

```bash
gac init
```

Trình hướng dẫn sẽ:

1. Yêu cầu bạn chọn "ChatGPT OAuth" từ danh sách nhà cung cấp
2. Tự động mở trình duyệt của bạn để xác thực OAuth
3. Lưu token truy cập của bạn vào `~/.gac/oauth/chatgpt-oauth.json`
4. Đặt mô hình mặc định

### Tùy chọn 2: Chuyển sang ChatGPT OAuth sau

Nếu bạn đã cấu hình GAC với một nhà cung cấp khác và muốn chuyển sang ChatGPT OAuth:

```bash
gac model
```

Sau đó:

1. Chọn "ChatGPT OAuth" từ danh sách nhà cung cấp
2. Trình duyệt của bạn sẽ tự động mở để xác thực OAuth
3. Token được lưu vào `~/.gac/oauth/chatgpt-oauth.json`
4. Mô hình được cấu hình tự động

### Sử dụng GAC bình thường

Sau khi xác thực, sử dụng GAC như bình thường:

```bash
# Stage các thay đổi của bạn
git add .

# Tạo và commit với ChatGPT OAuth
gac

# Hoặc ghi đè mô hình cho một commit duy nhất
gac -m chatgpt-oauth:gpt-5.5
```

## Các mô hình có sẵn

ChatGPT OAuth cung cấp quyền truy cập vào các mô hình tối ưu hóa Codex. Các mô hình hiện tại bao gồm:

- `gpt-5.5` — Mô hình Codex mới nhất và mạnh mẽ nhất
- `gpt-5.4` — Mô hình Codex thế hệ trước
- `gpt-5.3-codex` — Mô hình Codex thế hệ thứ ba

Kiểm tra [tài liệu OpenAI](https://platform.openai.com/docs/models) để biết danh sách đầy đủ các mô hình có sẵn.

## Lệnh CLI

GAC cung cấp các lệnh CLI chuyên dụng để quản lý ChatGPT OAuth:

### Đăng nhập

Xác thực hoặc xác thực lại với ChatGPT OAuth:

```bash
gac auth chatgpt login
```

Trình duyệt của bạn sẽ tự động mở để hoàn tất luồng OAuth. Nếu bạn đã được xác thực, điều này sẽ làm mới token của bạn.

### Đăng xuất

Xóa các token ChatGPT OAuth đã lưu:

```bash
gac auth chatgpt logout
```

Điều này xóa tệp token đã lưu tại `~/.gac/oauth/chatgpt-oauth.json`.

### Trạng thái

Kiểm tra trạng thái xác thực ChatGPT OAuth hiện tại của bạn:

```bash
gac auth chatgpt status
```

Hoặc kiểm tra tất cả các nhà cung cấp cùng một lúc:

```bash
gac auth
```

## Khắc phục sự cố

### Token đã hết hạn

Nếu bạn thấy lỗi xác thực, token của bạn có thể đã hết hạn. Xác thực lại bằng cách chạy:

```bash
gac auth chatgpt login
```

Trình duyệt của bạn sẽ tự động mở để xác thực OAuth mới. GAC tự động sử dụng token làm mới để gia hạn quyền truy cập mà không cần xác thực lại khi có thể.

### Kiểm tra trạng thái xác thực

Để kiểm tra xem bạn hiện có được xác thực hay không:

```bash
gac auth chatgpt status
```

Hoặc kiểm tra tất cả các nhà cung cấp cùng một lúc:

```bash
gac auth
```

### Đăng xuất

Để xóa token đã lưu của bạn:

```bash
gac auth chatgpt logout
```

### "Không tìm thấy token ChatGPT OAuth"

Điều này có nghĩa là GAC không thể tìm thấy token truy cập của bạn. Xác thực bằng cách chạy:

```bash
gac model
```

Sau đó chọn "ChatGPT OAuth" từ danh sách nhà cung cấp. Luồng OAuth sẽ bắt đầu tự động.

### "Xác thực không thành công"

Nếu xác thực OAuth không thành công:

1. Đảm bảo bạn có gói đăng ký ChatGPT Plus hoặc Pro đang hoạt động
2. Kiểm tra xem trình duyệt của bạn có mở đúng không
3. Thử trình duyệt khác nếu sự cố vẫn tiếp diễn
4. Xác minh kết nối mạng với `auth.openai.com`
5. Kiểm tra xem các cổng 1455-1465 có sẵn cho máy chủ callback cục bộ không

### Cổng đã được sử dụng

Máy chủ callback OAuth tự động thử các cổng 1455-1465. Nếu tất cả các cổng đều bị chiếm:

```bash
# Trên macOS/Linux:
lsof -ti:1455-1465 | xargs kill -9

# Trên Windows (PowerShell):
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Sau đó chạy lại `gac auth chatgpt login`.

## Sự khác biệt so với nhà cung cấp OpenAI

| Tính năng     | OpenAI (`openai:`)          | ChatGPT OAuth (`chatgpt-oauth:`)                 |
| ------------- | --------------------------- | ------------------------------------------------ |
| Xác thực      | Khóa API (`OPENAI_API_KEY`) | OAuth (luồng trình duyệt tự động)                |
| Thanh toán    | Thanh toán API theo token   | Dựa trên gói đăng ký (ChatGPT Plus/Pro)          |
| Thiết lập     | Nhập khóa API thủ công      | OAuth tự động qua `gac init` hoặc `gac model`    |
| Quản lý token | Khóa API tồn tại lâu dài    | Token OAuth (tự động làm mới bằng token làm mới) |
| Mô hình       | Tất cả các mô hình OpenAI   | Mô hình tối ưu hóa Codex                         |

## Lưu ý bảo mật

- **Không bao giờ commit token truy cập của bạn** vào kiểm soát phiên bản
- GAC lưu trữ token OAuth trong `~/.gac/oauth/chatgpt-oauth.json` (bên ngoài thư mục dự án của bạn)
- Luồng OAuth sử dụng PKCE (Proof Key for Code Exchange) để tăng cường bảo mật
- Máy chủ callback cục bộ chỉ chạy trên localhost (cổng 1455-1465)
- Token làm mới được sử dụng để tự động gia hạn quyền truy cập mà không cần xác thực lại

## Xem thêm

- [Tài liệu chính](USAGE.md)
- [Hướng dẫn khắc phục sự cố](TROUBLESHOOTING.md)
- [Tài liệu Codex của OpenAI](https://openai.com/codex)
