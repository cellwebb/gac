# Sử Dụng GAC Như Một MCP Server

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | **Tiếng Việt** | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC có thể chạy như một server [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), cho phép các AI agent và editor tạo commit thông qua các lời gọi công cụ có cấu trúc thay vì các lệnh shell.

## Mục Lục

- [Sử Dụng GAC Như Một MCP Server](#sử-dụng-gac-như-một-mcp-server)
  - [Mục Lục](#mục-lục)
  - [MCP Là Gì?](#mcp-là-gì)
  - [Lợi Ích](#lợi-ích)
  - [Thiết Lập](#thiết-lập)
    - [Claude Code](#claude-code)
    - [Claude Desktop](#claude-desktop)
    - [Cursor](#cursor)
    - [Các MCP Client Khác](#các-mcp-client-khác)
  - [Các Công Cụ Có Sẵn](#các-công-cụ-có-sẵn)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Quy Trình Làm Việc](#quy-trình-làm-việc)
    - [Commit Cơ Bản](#commit-cơ-bản)
    - [Xem Trước Trước Khi Commit](#xem-trước-trước-khi-commit)
    - [Commit Theo Nhóm](#commit-theo-nhóm)
    - [Commit Với Ngữ Cảnh](#commit-với-ngữ-cảnh)
  - [Cấu Hình](#cấu-hình)
  - [Xử Lý Sự Cố](#xử-lý-sự-cố)
  - [Xem Thêm](#xem-thêm)

## MCP Là Gì?

Model Context Protocol là một tiêu chuẩn mở cho phép các ứng dụng AI gọi các công cụ bên ngoài thông qua một giao diện có cấu trúc. Bằng cách chạy GAC như một MCP server, bất kỳ client tương thích MCP nào cũng có thể kiểm tra trạng thái repository và tạo commit được hỗ trợ bởi AI mà không cần gọi trực tiếp các lệnh shell.

## Lợi Ích

- **Tương tác có cấu trúc**: Agent gọi các công cụ có kiểu dữ liệu với tham số đã được xác thực thay vì phân tích đầu ra shell
- **Quy trình hai công cụ**: `gac_status` để kiểm tra, `gac_commit` để hành động - phù hợp tự nhiên với lý luận của agent
- **Đầy đủ khả năng GAC**: Thông điệp commit AI, commit theo nhóm, quét bí mật và push - tất cả đều có sẵn qua MCP
- **Không cần cấu hình thêm**: Server sử dụng cấu hình GAC hiện có của bạn (`~/.gac.env`, cài đặt nhà cung cấp, v.v.)

## Thiết Lập

MCP server được khởi động bằng `gac serve` và giao tiếp qua stdio, phương thức truyền tải MCP tiêu chuẩn.

### Claude Code

Thêm vào `.mcp.json` của dự án hoặc file cấu hình toàn cục `~/.claude/claude_code_config.json`:

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

Hoặc nếu bạn đã cài đặt GAC toàn cục:

```json
{
  "mcpServers": {
    "gac": {
      "command": "gac",
      "args": ["serve"]
    }
  }
}
```

### Claude Desktop

Thêm vào file cấu hình Claude Desktop của bạn (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`, Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### Cursor

Thêm vào cài đặt MCP của Cursor (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### Các MCP Client Khác

Bất kỳ client tương thích MCP nào cũng có thể sử dụng GAC. Điểm vào server là:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

Nếu bạn đã cài đặt GAC (qua `uv tool install gac`), bạn có thể sử dụng trực tiếp `gac` thay vì `uvx gac`.

## Các Công Cụ Có Sẵn

Server cung cấp hai công cụ:

### gac_status

Kiểm tra trạng thái repository. Sử dụng trước khi commit để hiểu những gì sẽ được commit.

**Tham số:**

| Parameter           | Type                                    | Default     | Mô tả                                                |
| ------------------- | --------------------------------------- | ----------- | ---------------------------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Định dạng đầu ra                                     |
| `include_diff`      | bool                                    | `false`     | Bao gồm nội dung diff đầy đủ                         |
| `include_stats`     | bool                                    | `true`      | Bao gồm thống kê thay đổi dòng                       |
| `include_history`   | int                                     | `0`         | Số lượng commit gần đây cần bao gồm                  |
| `staged_only`       | bool                                    | `false`     | Chỉ hiển thị các thay đổi đã staged                  |
| `include_untracked` | bool                                    | `true`      | Bao gồm các tệp chưa được theo dõi                   |
| `max_diff_lines`    | int                                     | `500`       | Giới hạn kích thước đầu ra diff (0 = không giới hạn) |

**Trả về:** Tên nhánh, trạng thái tệp (staged/unstaged/untracked/conflicts), nội dung diff tùy chọn, thống kê tùy chọn và lịch sử commit tùy chọn.

### gac_commit

Tạo thông điệp commit được hỗ trợ bởi AI và tùy chọn thực thi commit.

**Tham số:**

| Parameter          | Type           | Default | Mô tả                                                            |
| ------------------ | -------------- | ------- | ---------------------------------------------------------------- |
| `stage_all`        | bool           | `false` | Stage tất cả các thay đổi trước khi commit (`git add -A`)        |
| `files`            | list[str]      | `[]`    | Các tệp cụ thể cần stage                                         |
| `dry_run`          | bool           | `false` | Xem trước mà không thực thi                                      |
| `message_only`     | bool           | `false` | Tạo thông điệp mà không commit                                   |
| `push`             | bool           | `false` | Push đến remote sau khi commit                                   |
| `group`            | bool           | `false` | Chia các thay đổi thành nhiều commit logic                       |
| `one_liner`        | bool           | `false` | Thông điệp commit một dòng                                       |
| `scope`            | string \| null | `null`  | Phạm vi commit tiêu chuẩn (tự động phát hiện nếu không cung cấp) |
| `hint`             | string         | `""`    | Ngữ cảnh bổ sung để có thông điệp tốt hơn                        |
| `model`            | string \| null | `null`  | Ghi đè mô hình AI (`provider:model_name`)                        |
| `language`         | string \| null | `null`  | Ghi đè ngôn ngữ thông điệp commit                                |
| `skip_secret_scan` | bool           | `false` | Bỏ qua quét bảo mật                                              |
| `no_verify`        | bool           | `false` | Bỏ qua hook pre-commit                                           |
| `auto_confirm`     | bool           | `false` | Bỏ qua gợi ý xác nhận (bắt buộc cho agent)                       |

**Trả về:** Trạng thái thành công, thông điệp commit đã tạo, hash commit (nếu đã commit), danh sách tệp đã thay đổi và các cảnh báo.

## Quy Trình Làm Việc

### Commit Cơ Bản

```text
1. gac_status()                              → Xem những gì đã thay đổi
2. gac_commit(stage_all=true, auto_confirm=true)  → Stage, tạo thông điệp và commit
```

### Xem Trước Trước Khi Commit

```text
1. gac_status(include_diff=true, include_stats=true)  → Xem chi tiết các thay đổi
2. gac_commit(stage_all=true, dry_run=true)            → Xem trước thông điệp commit
3. gac_commit(stage_all=true, auto_confirm=true)       → Thực thi commit
```

### Commit Theo Nhóm

```text
1. gac_status()                                           → Xem tất cả các thay đổi
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Xem trước các nhóm logic
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Thực thi commit theo nhóm
```

### Commit Với Ngữ Cảnh

```text
1. gac_status(include_history=5)  → Xem các commit gần đây để tham khảo phong cách
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Cấu Hình

MCP server sử dụng cấu hình GAC hiện có của bạn. Không cần thiết lập thêm ngoài:

1. **Nhà cung cấp và mô hình**: Chạy `gac init` hoặc `gac model` để cấu hình nhà cung cấp AI
2. **Khóa API**: Được lưu trong `~/.gac.env` (thiết lập trong quá trình `gac init`)
3. **Cài đặt tùy chọn**: Tất cả các biến môi trường GAC đều áp dụng (`GAC_LANGUAGE`, `GAC_VERBOSE`, v.v.)

Xem [tài liệu chính](USAGE.md#ghi-chú-cấu-hình) để biết tất cả các tùy chọn cấu hình.

## Xử Lý Sự Cố

### "No model configured"

Chạy `gac init` để thiết lập nhà cung cấp AI và mô hình trước khi sử dụng MCP server.

### "No staged changes found"

Stage các tệp thủ công (`git add`) hoặc sử dụng `stage_all=true` trong lời gọi `gac_commit`.

### Server không khởi động

Xác minh GAC đã được cài đặt và có thể truy cập:

```bash
uvx gac --version
# hoặc
gac --version
```

Nếu sử dụng `uvx`, đảm bảo `uv` đã được cài đặt và nằm trong PATH của bạn.

### Agent không tìm thấy server

Đảm bảo file cấu hình MCP nằm đúng vị trí cho client của bạn và đường dẫn `command` có thể truy cập từ môi trường shell của bạn.

### Lỗi đầu ra Rich

MCP server tự động chuyển hướng tất cả đầu ra Rich console sang stderr để ngăn lỗi giao thức stdio. Nếu bạn thấy đầu ra bị lỗi, hãy đảm bảo bạn đang chạy `gac serve` (không phải `gac` trực tiếp) khi sử dụng MCP.

## Xem Thêm

- [Tài liệu chính](USAGE.md)
- [Thiết lập Claude Code OAuth](CLAUDE_CODE.md)
- [Thiết lập Qwen.ai OAuth](QWEN.md)
- [Hướng dẫn xử lý sự cố](TROUBLESHOOTING.md)
- [Đặc tả MCP](https://modelcontextprotocol.io/)
