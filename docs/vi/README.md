<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

# 🚀 Git Auto Commit (`gac`)

[![PyPI version](https://img.shields.io/pypi/v/gac.svg)](https://pypi.org/project/gac/)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](../../README.md) | [简体中文](../zh-CN/README.md) | [繁體中文](../zh-TW/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [हिन्दी](../hi/README.md) | **Tiếng Việt** | [Français](../fr/README.md) | [Русский](../ru/README.md) | [Español](../es/README.md) | [Português](../pt/README.md) | [Norsk](../no/README.md) | [Svenska](../sv/README.md) | [Deutsch](../de/README.md) | [Nederlands](../nl/README.md) | [Italiano](../it/README.md)

**Thông điệp commit được hỗ trợ bởi LLM, hiểu mã của bạn!**

**Tự động hóa commit của bạn!** Thay thế `git commit -m "..."` bằng `gac` để có thông điệp commit có ngữ cảnh, được định dạng tốt được tạo ra bởi các mô hình ngôn ngữ lớn!

---

## Bạn Nhận Được Gì

Thông điệp thông minh, có ngữ cảnh giải thích **tại sao** đằng sau những thay đổi của bạn:

![GAC generating a contextual commit message](../../assets/gac-simple-usage.vi.png)

---

</div>

<!-- markdownlint-enable MD033 MD036 -->

## Bắt Đầu Nhanh

### Sử dụng gac mà không cần cài đặt

```bash
uvx gac init   # Cấu hình nhà cung cấp, mô hình và ngôn ngữ của bạn
uvx gac  # Tạo và commit với LLM
```

Chỉ vậy thôi! Xem lại thông điệp đã tạo và xác nhận bằng `y`.

### Cài đặt và sử dụng gac

```bash
uv tool install gac
gac init
gac
```

### Nâng cấp gac đã cài đặt

```bash
uv tool upgrade gac
```

---

## Tính Năng Chính

### 🌐 **Hơn 25 Nhà Cung Cấp Hỗ Trợ**

- **Anthropic** • **Azure OpenAI** • **Cerebras** • **ChatGPT (OAuth)** • **Chutes.ai**
- **Claude Code (OAuth)** • **DeepSeek** • **Fireworks** • **Gemini** • **GitHub Copilot**
- **Groq** • **Kimi for Coding** • **LM Studio** • **MiniMax.io** • **Mistral AI** • **Moonshot AI**
- **Ollama** • **OpenAI** • **OpenRouter** • **Qwen Cloud (CN & INTL)** • **Replicate**
- **Streamlake/Vanchin** • **Synthetic.new** • **Together AI** • **Wafer.ai**
- **Z.AI** • **Z.AI Coding** • **Custom Endpoints (Anthropic/OpenAI)**

### 🧠 **Phân Tích LLM Thông Minh**

- **Hiểu ý định**: Phân tích cấu trúc mã, logic và các mẫu để hiểu "tại sao" đằng sau những thay đổi của bạn, không chỉ những gì đã thay đổi
- **Nhận thức ngữ nghĩa**: Nhận biết tái cấu trúc, sửa lỗi, tính năng và các thay đổibreaking để tạo thông điệp commit có ngữ cảnh phù hợp
- **Lọc thông minh**: Ưu tiên các thay đổi có ý nghĩa trong khi bỏ qua các tệp được tạo, phụ thuộc và artifacts
- **Nhóm commit thông minh** - Tự động nhóm các thay đổi liên quan thành nhiều commit logic với `--group`

### 📝 **Nhiều Định Dạng Thông Điệp**

- **Một dòng** (-o flag): Thông điệp commit một dòng theo định dạng commit tiêu chuẩn
- **Tiêu chuẩn** (mặc định): Tóm tắt với các gạch đầu dòng giải thích chi tiết triển khai
- **Chi tiết** (-v flag): Giải thích toàn diện bao gồm động cơ, cách tiếp cận kỹ thuật và phân tích tác động
- **Quy tắc 50/72** (cờ --50-72): Áp dụng định dạng tin nhắn commit cổ điển để dễ đọc tối ưu trong git log và GitHub UI
- **DCO/Signoff** (cờ --signoff): Thêm dòng Signed-off-by để tuân thủ Developer Certificate of Origin (bắt buộc bởi Cherry Studio, Linux kernel và các dự án khác)

### 🌍 **Hỗ Trợ Đa Ngôn Ngữ**

- **25+ ngôn ngữ**: Tạo thông điệp commit bằng tiếng Anh, tiếng Trung, tiếng Nhật, tiếng Hàn, tiếng Tây Ban Nha, tiếng Pháp, tiếng Đức và 20+ ngôn ngữ khác
- **Dịch linh hoạt**: Chọn giữ tiền tố commit tiêu chuẩn bằng tiếng Anh để tương thích công cụ, hoặc dịch hoàn toàn chúng
- **Nhiều quy trình làm việc**: Đặt ngôn ngữ mặc định với `gac language`, hoặc sử dụng flag `-l <language>` để ghi đè một lần
- **Hỗ trợ chữ viết gốc**: Hỗ trợ đầy đủ cho các chữ viết không phải Latin bao gồm CJK, Cyrillic, Thai và nhiều hơn nữa

### 💻 **Trải Nghiệm Nhà Phát Triển**

- **Phản hồi tương tác**: Gõ `r` để reroll, `e` để chỉnh sửa (TUI tại chỗ mặc định, hoặc `$GAC_EDITOR` nếu đã đặt), hoặc gõ trực tiếp phản hồi của bạn như `làm nó ngắn hơn` hoặc `tập trung vào sửa lỗi`
- **Hỏi đáp tương tác**: Sử dụng `--interactive` (`-i`) để trả lời các câu hỏi nhắm mục tiêu về các thay đổi của bạn để có thông điệp commit có nhiều ngữ cảnh hơn
- **Quy trình làm việc một lệnh**: Quy trình làm việc hoàn chỉnh với các flag như `gac -ayp` (stage tất cả, tự động xác nhận, push)
- **Tích hợp Git**: Tôn các hook pre-commit và lefthook, chạy chúng trước các thao tác LLM tốn kém
- **MCP server**: Chạy `gac serve` để cung cấp công cụ commit cho AI agent thông qua [Model Context Protocol](https://modelcontextprotocol.io/)

### 📊 **Thống Kê Sử Dụng**

- **Theo dõi các gac của bạn**: Xem bạn đã thực hiện bao nhiêu commit với gac, chuỗi hiện tại, hoạt động đỉnh hàng ngày/hàng tuần, và các dự án hàng đầu
- **Theo dõi token**: Tổng token prompt và completion theo ngày, tuần, dự án và mô hình — với cúp kỷ lục cho việc sử dụng token
- **Mô hình hàng đầu**: Xem mô hình nào bạn sử dụng nhiều nhất và mỗi mô hình tiêu thụ bao nhiêu token
- **Thống kê theo dự án**: Xem thống kê cho tất cả repo với `gac stats projects`
- **Ăn mừng điểm cao**: 🏆 cúp khi bạn thiết lập kỷ lục hàng ngày, hàng tuần, token, hoặc chuỗi mới; 🥈 khi ngang bằng
- **Chọn tham gia khi cài đặt**: `gac init` hỏi bạn có muốn bật thống kê và giải thích chính xác những gì được lưu trữ
- **Từ chối bất cứ lúc nào**: Đặt `GAC_DISABLE_STATS=true` (hoặc `1`/`yes`/`on`) để vô hiệu hóa. Đặt thành `false`/`0`/`no` (hoặc bỏ đặt) giữ thống kê được bật
- **Ưu tiên quyền riêng tư**: Lưu trữ cục bộ trong `~/.gac_stats.json`. Chỉ số lượng, ngày tháng, tên dự án và tên mô hình — không có thông điệp commit, mã, hay dữ liệu cá nhân. Không thu thập dữ liệu từ xa

### 🛡️ **Bảo Mật Tích Hợp**

- **Phát hiện bí mật tự động**: Quét các khóa API, mật khẩu và token trước khi commit
- **Bảo vệ tương tác**: Gợi ý trước khi commit dữ liệu nhạy cảm tiềm tàng với các tùy chọn khắc phục rõ ràng
- **Lọc thông minh**: Bỏ qua các tệp ví dụ, tệp mẫu và văn bản giữ chỗ để giảm các dương tính giả

---

## Ví Dụ Sử Dụng

### Quy Trình Cơ Bản

```bash
# Stage các thay đổi của bạn
git add .

# Tạo và commit với LLM
gac

# Xem lại → y (commit) | n (hủy) | r (reroll) | e (chỉnh sửa) | hoặc gõ phản hồi
```

### Lệnh Thông Dụng

| Lệnh             | Mô t�                                                                         |
| ---------------- | ----------------------------------------------------------------------------- |
| `gac`            | Tạo thông điệp commit                                                         |
| `gac -y`         | Tự động xác nhận (không cần xem lại)                                          |
| `gac -a`         | Stage tất cả trước khi tạo thông điệp commit                                  |
| `gac -o`         | Thông điệp một dòng cho các thay đổi nhỏ                                      |
| `gac -v`         | Định dạng chi tiết với Động cơ, Cách tiếp cận Kỹ thuật, và Phân tích Tác động |
| `gac -h "gợi ý"` | Thêm ngữ cảnh cho LLM (ví dụ, `gac -h "sửa lỗi"`)                             |
| `gac -s`         | Bao gồm phạm vi (ví dụ, feat(auth):)                                          |
| `gac -i`         | Hỏi về các thay đổi để có ngữ cảnh tốt hơn                                    |
| `gac -g`         | Nhóm các thay đổi thành nhiều commit logic                                    |
| `gac -p`         | Commit và push                                                                |
| `gac stats`      | Xem thống kê sử dụng gac của bạn                                              |

### Ví Dụ Người Dùng Nâng Cao

```bash
# Quy trình hoàn chỉnh trong một lệnh
# Xem thống kê commit của bạn
gac stats

# Thống kê tất cả dự án
gac stats projects

gac -ayp -h "chuẩn bị phát hành"

# Giải thích chi tiết với phạm vi
gac -v -s

# Thông điệp một dòng nhanh cho các thay đổi nhỏ
gac -o

# Nhóm các thay đổi thành các commit logic liên quan
gac -ag

# Chế độ tương tác với đầu ra chi tiết cho giải thích chi tiết
gac -iv

# Gỡ lỗi xem LLM thấy gì
gac --show-prompt

# Bỏ qua quét bảo mật (sử dụng cẩn thận)
gac --skip-secret-scan

# Thêm signoff để tuân thủ DCO (Cherry Studio, Linux kernel, v.v.)
gac --signoff
```

### Hệ Thống Phản Hồi Tương Tác

Không hài lòng với kết quả? Bạn có một số tùy chọn:

```bash
# Reroll đơn giản (không có phản hồi)
r

# Chỉnh sửa thông điệp commit
e
# Mặc định: TUI tại chỗ với phím tắt vi/emacs
# Nhấn Esc+Enter hoặc Ctrl+S để gửi, Ctrl+C để hủy

# Đặt GAC_EDITOR để mở trình soạn thảo ưa thích:
# GAC_EDITOR=code gac → mở VS Code (--wait tự động áp dụng)
# GAC_EDITOR=vim gac → mở vim
# GAC_EDITOR=nano gac → mở nano

# Hoặc chỉ gõ phản hồi của bạn trực tiếp!
làm nó ngắn hơn và tập trung vào cải thiện hiệu suất
sử dụng định dạng commit tiêu chuẩn với phạm vi
giải thích các tác động bảo mật

# Nhấn Enter trên input trống để xem gợi ý lại
```

Tính năng chỉnh sửa (`e`) cho phép bạn tinh chỉnh thông điệp commit:

- **Mặc định (TUI tại chỗ)**: Chỉnh sửa đa dòng với phím tắt vi/emacs — sửa lỗi chính tả, điều chỉnh từ ngữ, tái cấu trúc
- **Với `GAC_EDITOR`**: Mở trình soạn thảo ưa thích (`code`, `vim`, `nano`, v.v.) — toàn bộ sức mạnh trình soạn thảo bao gồm tìm/thay thế, macro, v.v.

Trình soạn thảo GUI như VS Code được xử lý tự động: gac chèn `--wait` để quy trình chặn cho đến khi bạn đóng tab trình soạn thảo. Không cần cấu hình thêm.

---

## Cấu Hình

Chạy `gac init` để cấu hình nhà cung cấp của bạn một cách tương tác, hoặc đặt các biến môi trường:

Cần thay đổi nhà cung cấp hoặc mô hình sau này mà không ảnh hưởng đến cài đặt ngôn ngữ? Sử dụng `gac model` cho quy trình hợp lý bỏ qua các gợi ý ngôn ngữ.

```bash
# Ví dụ cấu hình
GAC_MODEL=anthropic:your-model-name
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Xem `.gac.env.example` cho tất cả các tùy chọn có sẵn.

**Muốn thông điệp commit bằng ngôn ngữ khác?** Chạy `gac language` để chọn từ 25+ ngôn ngữ bao gồm Español, Français, 日本語 và nhiều hơn nữa.

**Muốn tùy chỉnh kiểu thông điệp commit?** Xem [docs/CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md) để được hướng dẫn viết các gợi ý hệ thống tùy chỉnh.

---

## Nhận Trợ Giúp

- **Tài liệu đầy đủ**: [USAGE.md](USAGE.md) - Tham chiếu CLI hoàn chỉnh
- **MCP server**: [docs/MCP.md](MCP.md) - Sử dụng GAC làm MCP server cho AI agent
- **Claude Code OAuth**: [docs/CLAUDE_CODE.md](docs/vi/CLAUDE_CODE.md) - Cài đặt và xác thực Claude Code
- **ChatGPT OAuth**: [docs/CHATGPT_OAUTH.md](docs/vi/CHATGPT_OAUTH.md) - Cài đặt và xác thực ChatGPT OAuth
- **Gợi ý tùy chỉnh**: [CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md) - Tùy chỉnh kiểu thông điệp commit
- **Thống kê sử dụng**: Xem `gac stats --help` hoặc [tài liệu đầy đủ](docs/vi/USAGE.md#thống-kê-sử-dụng)
- **Xử lý sự cố**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Các vấn đề phổ biến và giải pháp
- **Đóng góp**: [CONTRIBUTING.md](CONTRIBUTING.md) - Thiết lập phát triển và hướng dẫn

---

<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

[⭐ Star chúng tôi trên GitHub](https://github.com/cellwebb/gac) • [🐛 Báo cáo vấn đề](https://github.com/cellwebb/gac/issues) • [📖 Tài liệu đầy đủ](USAGE.md)

</div>

<!-- markdownlint-enable MD033 MD036 -->
