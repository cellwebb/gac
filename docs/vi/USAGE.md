# Sử Dụng Dòng Lệnh gac

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | **Tiếng Việt** | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

Tài liệu này mô tả tất cả các flag và tùy chọn có sẵn cho công cụ CLI `gac`.

## Mục Lục

- [Sử Dụng Dòng Lệnh gac](#sử-dụng-dòng-lệnh-gac)
  - [Mục Lục](#mục-lục)
  - [Sử Dụng Cơ Bản](#sử-dụng-cơ-bản)
  - [Flag Quy Trình Chính](#flag-quy-trình-chính)
  - [Tùy Chỉnh Thông Điệp](#tùy-chỉnh-thông-điệp)
  - [Đầu Ra và Độ Chi Tiết](#đầu-ra-và-độ-chi-tiết)
  - [Trợ Giúp và Phiên Bản](#trợ-giúp-và-phiên-bản)
  - [Ví Dụ Quy Trình](#ví-dụ-quy-trình)
  - [Nâng Cao](#nâng-cao)
    - [Bỏ Qua Hooks Pre-commit và Lefthook](#bỏ-qua-hooks-pre-commit-và-lefthook)
    - [Quét Bảo Mật](#quét-bảo-mật)
    - [Xác Minh Chứng Chỉ SSL](#xác-minh-chứng-chỉ-ssl)
  - [Ghi Chú Cấu Hình](#ghi-chú-cấu-hình)
    - [Tùy Chọn Cấu Hình Nâng Cao](#tùy-chọn-cấu-hình-nâng-cao)
    - [Lệnh Con Cấu Hình](#lệnh-con-cấu-hình)
  - [Chế Độ Tương Tác](#chế-độ-tương-tác)
    - [Cách Hoạt Động](#cách-hoạt-động)
    - [Khi Nào Sử Dụng Chế Độ Tương Tác](#khi-nào-sử-dụng-chế-độ-tương-tác)
    - [Ví Dụ Sử Dụng](#ví-dụ-sử-dụng)
    - [Quy Trình Hỏi-Đáp](#quy-trình-hỏi-đáp)
    - [Kết Hợp Với Các Flag Khác](#kết-hợp-với-các-flag-khác)
    - [Thực T hành Tốt Nhất](#thực-t-hành-tốt-nhất)
  - [Nhận Trợ Giúp](#nhận-trợ-giúp)

## Sử Dụng Cơ Bản

```sh
gac init
# Sau đó làm theo các gợi ý để cấu hình nhà cung cấp, mô hình và khóa API một cách tương tác
gac
```

Tạo thông điệp commit được hỗ trợ bởi LLM cho các thay đổi đã staged và gợi ý xác nhận. Gợi ý xác nhận chấp nhận:

- `y` hoặc `yes` - Tiếp tục với commit
- `n` hoặc `no` - Hủy commit
- `r` hoặc `reroll` - Tạo lại thông điệp commit với cùng ngữ cảnh
- `e` hoặc `edit` - Chỉnh sửa thông điệp commit tại chỗ với chỉnh sửa terminal phong phú (phím tắt vi/emacs)
- Bất kỳ văn bản nào khác - Tạo lại với văn bản đó làm phản hồi (ví dụ, `làm nó ngắn hơn`, `tập trung vào hiệu suất`)
- Input trống (chỉ Enter) - Hiển thị gợi ý lại

---

## Flag Quy Trình Chính

| Flag / Tùy chọn      | Ngắn | Mô tả                                                                    |
| -------------------- | ---- | ------------------------------------------------------------------------ |
| `--add-all`          | `-a` | Stage tất cả các thay đổi trước khi committing                           |
| `--group`            | `-g` | Nhóm các thay đổi đã staged thành nhiều commit logic                     |
| `--push`             | `-p` | Push thay đổi đến remote sau khi committing                              |
| `--yes`              | `-y` | Tự động xác nhận commit mà không cần gợi ý                               |
| `--dry-run`          |      | Hiển thị những gì sẽ xảy ra mà không thực hiện thay đổi nào              |
| `--message-only`     |      | Chỉ in ra thông điệp commit được sinh ra, không thực hiện commit vào git |
| `--no-verify`        |      | Bỏ qua các hook pre-commit và lefthook khi committing                    |
| `--skip-secret-scan` |      | Bỏ qua quét bảo mật cho các bí mật trong các thay đổi đã staged          |
| `--no-verify-ssl`    |      | Bỏ qua xác minh chứng chỉ SSL (hữu ích cho proxy doanh nghiệp)           |
| `--interactive`      | `-i` | Đặt câu hỏi về các thay đổi để có commit tốt hơn                         |

**Lưu ý:** Kết hợp `-a` và `-g` (tức là `-ag`) để stage TẤT CẢ các thay đổi trước, sau đó nhóm chúng vào các commit.

**Lưu ý:** Khi sử dụng `--group`, giới hạn token đầu ra tối đa được tự động scale dựa trên số lượng tệp đang được commit (2x cho 1-9 tệp, 3x cho 10-19 tệp, 4x cho 20-29 tệp, 5x cho 30+ tệp). Điều này đảm bảo LLM có đủ token để tạo tất cả các commit được nhóm mà không bị cắt ngắn, ngay cả với các thay đổi lớn.

**Lưu ý:** `--message-only` và `--group` loại trừ lẫn nhau. Hãy dùng `--message-only` khi bạn muốn lấy thông điệp commit để xử lý bên ngoài, và dùng `--group` khi bạn muốn tổ chức nhiều commit trong cùng quy trình git hiện tại.

**Lưu ý:** Flag `--interactive` cung cấp ngữ cảnh bổ sung cho LLM bằng cách đặt câu hỏi về các thay đổi của bạn, dẫn đến các thông điệp commit chính xác và chi tiết hơn. Điều này đặc biệt hữu ích cho các thay đổi phức tạp hoặc khi bạn muốn đảm bảo thông điệp commit nắm bắt toàn bộ ngữ cảnh công việc của mình.

## Tùy Chỉnh Thông Điệp

| Flag / Tùy chọn     | Ngắn | Mô tả                                                             |
| ------------------- | ---- | ----------------------------------------------------------------- |
| `--one-liner`       | `-o` | Tạo thông điệp commit một dòng                                    |
| `--verbose`         | `-v` | Tạo thông điệp commit chi tiết với động cơ, kiến trúc, & tác động |
| `--hint <text>`     | `-h` | Thêm gợi ý để hướng dẫn LLM                                       |
| `--model <model>`   | `-m` | Chỉ định mô hình để sử dụng cho commit này                        |
| `--language <lang>` | `-l` | Ghi đè ngôn ngữ (tên hoặc mã: 'Spanish', 'es', 'zh-CN', 'ja')     |
| `--scope`           | `-s` | Suy luận phạm vi phù hợp cho commit                               |

**Lưu ý:** Bạn có thể cung cấp phản hồi một cách tương tác bằng cách chỉ cần gõ nó tại gợi ý xác nhận - không cần tiền tố với 'r'. Gõ `r` để reroll đơn giản, `e` để chỉnh sửa tại chỗ với phím tắt vi/emacs, hoặc gõ phản hồi của bạn trực tiếp như `làm nó ngắn hơn`.

## Đầu Ra và Độ Chi Tiết

| Flag / Tùy chọn       | Ngắn | Mô tả                                              |
| --------------------- | ---- | -------------------------------------------------- |
| `--quiet`             | `-q` | Chặn tất cả đầu ra trừ lỗi                         |
| `--log-level <level>` |      | Đặt mức log (debug, info, warning, error)          |
| `--show-prompt`       |      | In gợi ý LLM được sử dụng để tạo thông điệp commit |

## Trợ Giúp và Phiên Bản

| Flag / Tùy chọn | Ngắn | Mô tả                                 |
| --------------- | ---- | ------------------------------------- |
| `--version`     |      | Hiển thị phiên bản gac và thoát       |
| `--help`        |      | Hiển thị thông điệp trợ giúp và thoát |

---

## Ví Dụ Quy Trình

- **Stage tất cả các thay đổi và commit:**

  ```sh
  gac -a
  ```

- **Commit và push trong một bước:**

  ```sh
  gac -ap
  ```

- **Tạo thông điệp commit một dòng:**

  ```sh
  gac -o
  ```

- **Tạo thông điệp commit chi tiết với các phần có cấu trúc:**

  ```sh
  gac -v
  ```

- **Thêm gợi ý cho LLM:**

  ```sh
  gac -h "Tái cấu trúc logic xác thực"
  ```

- **Suy luận phạm vi cho commit:**

  ```sh
  gac -s
  ```

- **Nhóm các thay đổi đã staged thành các commit logic:**

  ```sh
  gac -g
  # Chỉ nhóm các tệp bạn đã staged
  ```

- **Nhóm tất cả các thay đổi (staged + unstaged) và tự động xác nhận:**

  ```sh
  gac -agy
  # Stage tất cả, nhóm chúng, và tự động xác nhận
  ```

- **Sử dụng mô hình cụ thể chỉ cho commit này:**

  ```sh
  gac -m anthropic:claude-haiku-4-5
  ```

- **Tạo thông điệp commit bằng ngôn ngữ cụ thể:**

  ```sh
  # Sử dụng mã ngôn ngữ (ngắn hơn)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # Sử dụng tên đầy đủ
  gac -l "Tiếng Trung Đơn Giản"
  gac -l Japanese
  gac -l Spanish
  ```

- **Chạy thử (xem những gì sẽ xảy ra):**

  ```sh
  gac --dry-run
  ```

- **Chỉ lấy thông điệp commit (cho tích hợp script):**

  ```sh
  gac --message-only
  # Ví dụ đầu ra: feat: add user authentication system
  ```

- **Lấy thông điệp commit ở dạng một dòng:**

  ```sh
  gac --message-only --one-liner
  # Ví dụ đầu ra: feat: add user authentication system
  ```

- **Sử dụng chế độ tương tác để cung cấp ngữ cảnh:**

  ```sh
  gac -i
  # Mục đích chính của những thay đổi này là gì?
  # Bạn đang giải quyết vấn đề gì?
  # Có chi tiết triển khai nào đáng đề cập không?
  ```

- **Chế độ tương tác với đầu ra chi tiết:**

  ```sh
  gac -i -v
  # Đặt câu hỏi và tạo thông điệp commit chi tiết
  ```

## Nâng Cao

- Kết hợp các flag để có các quy trình làm việc mạnh mẽ hơn (ví dụ, `gac -ayp` để stage, tự động xác nhận, và push)
- Sử dụng `--show-prompt` để gỡ lỗi hoặc xem lại gợi ý được gửi đến LLM
- Điều chỉnh độ chi tiết với `--log-level` hoặc `--quiet`

### Bỏ Qua Hooks Pre-commit và Lefthook

Flag `--no-verify` cho phép bạn bỏ qua bất kỳ hook pre-commit hoặc lefthook nào được cấu hình trong dự án của bạn:

```sh
gac --no-verify  # Bỏ qua tất cả các hook pre-commit và lefthook
```

**Sử dụng `--no-verify` khi:**

- Các hook pre-commit hoặc lefthook tạm thời thất bại
- Làm việc với các hook tốn thời gian
- Commit mã công việc đang tiến triển chưa vượt qua tất cả các kiểm tra

**Lưu ý:** Sử dụng cẩn thận vì các hook này duy trì tiêu chuẩn chất lượng mã.

### Quét Bảo Mật

gac bao gồm quét bảo mật tích hợp tự động phát hiện các bí mật và khóa API tiềm tàng trong các thay đổi đã staged của bạn trước khi commit. Điều này giúp ngăn ngừa vô tình commit thông tin nhạy cảm.

**Bỏ qua quét bảo mật:**

```sh
gac --skip-secret-scan  # Bỏ qua quét bảo mật cho commit này
```

**Để vô hiệu hóa vĩnh viễn:** Đặt `GAC_SKIP_SECRET_SCAN=true` trong tệp `.gac.env` của bạn.

**Khi nào bỏ qua:**

- Commit mã ví dụ với khóa giữ chỗ
- Làm việc với test fixtures chứa thông tin xác thực giả
- Khi bạn đã xác nhận các thay đổi an toàn

**Lưu ý:** Trình quét sử dụng khớp mẫu để phát hiện các định dạng bí mật phổ biến. Luôn xem lại các thay đổi đã staged của bạn trước khi commit.

### Xác Minh Chứng Chỉ SSL

Flag `--no-verify-ssl` cho phép bạn bỏ qua xác minh chứng chỉ SSL cho các cuộc gọi API:

```sh
gac --no-verify-ssl  # Bỏ qua xác minh SSL cho commit này
```

**Để cấu hình vĩnh viễn:** Đặt `GAC_NO_VERIFY_SSL=true` trong tệp `.gac.env` của bạn.

**Sử dụng `--no-verify-ssl` khi:**

- Proxy doanh nghiệp chặn lưu lượng SSL (proxy MITM)
- Môi trường phát triển sử dụng chứng chỉ tự ký
- Gặp lỗi chứng chỉ SSL do cài đặt bảo mật mạng

**Lưu ý:** Chỉ sử dụng tùy chọn này trong môi trường mạng đáng tin cậy. Vô hiệu hóa xác minh SSL làm giảm bảo mật và có thể khiến các yêu cầu API của bạn dễ bị tấn công man-in-the-middle.

## Ghi Chú Cấu Hình

- Cách được đề xuất để thiết lập gac là chạy `gac init` và làm theo các gợi ý tương tác.
- Đã cấu hình ngôn ngữ và chỉ cần chuyển đổi nhà cung cấp hoặc mô hình? Chạy `gac model` để lặp lại thiết lập mà không có câu hỏi ngôn ngữ.
- **Đang sử dụng Claude Code?** Xem [hướng dẫn thiết lập Claude Code](CLAUDE_CODE.md) để biết hướng dẫn xác thực OAuth.
- **Đang sử dụng Qwen.ai?** Xem [hướng dẫn cài đặt Qwen.ai](QWEN.md) để biết hướng dẫn xác thực OAuth.
- gac tải cấu hình theo thứ tự ưu tiên sau:
  1. Các flag CLI
  2. Các biến môi trường
  3. Cấp dự án `.gac.env`
  4. Cấp người dùng `~/.gac.env`

### Tùy Chọn Cấu Hình Nâng Cao

Bạn có thể tùy chỉnh hành vi của gac với các biến môi trường tùy chọn này:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Tự động suy luận và bao gồm phạm vi trong thông điệp commit (ví dụ, `feat(auth):` so với `feat:`)
- `GAC_VERBOSE=true` - Tạo thông điệp commit chi tiết với các phần động cơ, kiến trúc và tác động
- `GAC_TEMPERATURE=0.7` - Kiểm soát sự sáng tạo của LLM (0.0-1.0, thấp hơn = tập trung hơn)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Token tối đa cho thông điệp đã tạo (tự động scale 2-5x khi sử dụng `--group` dựa trên số lượng tệp; ghi đè để đi cao hơn hoặc thấp hơn)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Cảnh báo khi các gợi ý vượt quá số lượng token này
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Sử dụng gợi ý hệ thống tùy chỉnh để tạo thông điệp commit
- `GAC_LANGUAGE=Spanish` - Tạo thông điệp commit bằng ngôn ngữ cụ thể (ví dụ, Spanish, French, Japanese, German). Hỗ trợ tên đầy đủ hoặc mã ISO (es, fr, ja, de, zh-CN). Sử dụng `gac language` để lựa chọn tương tác
- `GAC_TRANSLATE_PREFIXES=true` - Dịch các tiền tố commit tiêu chuẩn (feat, fix, v.v.) vào ngôn ngữ đích (mặc định: false, giữ tiền tố bằng tiếng Anh)
- `GAC_SKIP_SECRET_SCAN=true` - Vô hiệu hóa quét bảo mật tự động cho các bí mật trong các thay đổi đã staged (sử dụng cẩn thận)
- `GAC_NO_VERIFY_SSL=true` - Bỏ qua xác minh chứng chỉ SSL cho các cuộc gọi API (hữu ích cho proxy doanh nghiệp chặn lưu lượng SSL)

Xem `.gac.env.example` cho mẫu cấu hình hoàn chỉnh.

Để được hướng dẫn chi tiết về việc tạo gợi ý hệ thống tùy chỉnh, xem [docs/CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md).

### Lệnh Con Cấu Hình

Các lệnh con sau đây có sẵn:

- `gac init` — Trình hướng dẫn thiết lập tương tác cho nhà cung cấp, mô hình và cấu hình ngôn ngữ
- `gac model` — Thiết lập nhà cung cấp/mô hình/khoá API không có lời nhắc ngôn ngữ (lý tưởng cho các thay đổi nhanh)
- `gac auth` — Hiển thị trạng thái xác thực OAuth cho tất cả nhà cung cấp
- `gac auth claude-code login` — Đăng nhập vào Claude Code sử dụng OAuth (mở trình duyệt)
- `gac auth claude-code logout` — Đăng xuất khỏi Claude Code và xóa token đã lưu
- `gac auth claude-code status` — Kiểm tra trạng thái xác thực Claude Code
- `gac auth qwen login` — Đăng nhập vào Qwen sử dụng luồng thiết bị OAuth (mở trình duyệt)
- `gac auth qwen logout` — Đăng xuất khỏi Qwen và xóa token đã lưu
- `gac auth qwen status` — Kiểm tra trạng thái xác thực Qwen
- `gac config show` — Hiển thị cấu hình hiện tại
- `gac config set KEY VALUE` — Đặt khóa cấu hình trong `$HOME/.gac.env`
- `gac config get KEY` — Lấy giá trị cấu hình
- `gac config unset KEY` — Xóa khóa cấu hình khỏi `$HOME/.gac.env`
- `gac language` (hoặc `gac lang`) — Trình chọn ngôn ngữ tương tác cho các thông điệp commit (đặt GAC_LANGUAGE)
- `gac diff` — Hiển thị git diff đã lọc với các tùy chọn cho các thay đổi đã được staged/chưa staged, màu sắc và cắt bớt

## Chế Độ Tương Tác

Flag `--interactive` (`-i`) cải thiện việc tạo thông điệp commit của gac bằng cách đặt các câu hỏi có mục tiêu về các thay đổi của bạn. Ngữ cảnh bổ sung này giúp LLM tạo ra các thông điệp commit chính xác, chi tiết và phù hợp với ngữ cảnh hơn.

### Cách Hoạt Động

Khi bạn sử dụng `--interactive`, gac sẽ đặt các câu hỏi như:

- **Mục đích chính của những thay đổi này là gì?** - Giúp hiểu mục tiêu cấp cao
- **Bạn đang giải quyết vấn đề gì?** - Cung cấp ngữ cảnh về động lực
- **Có chi tiết triển khai nào đáng đề cập không?** - Nắm bắt các thông số kỹ thuật
- **Có thay đổi phá vỡ nào không?** - Xác định các vấn đề tác động tiềm tàng
- **Điều này liên quan đến issue hoặc ticket nào không?** - Kết nối với quản lý dự án

### Khi Nào Sử Dụng Chế Độ Tương Tác

Chế độ tương tác đặc biệt hữu ích cho:

- **Các thay đổi phức tạp** nơi ngữ cảnh không rõ ràng chỉ từ diff
- **Công việc refactoring** kéo dài qua nhiều tệp và khái niệm
- **Tính năng mới** đòi hỏi giải thích mục tiêu tổng thể
- **Sửa lỗi** nơi nguyên nhân gốc không ngay lập tức hiển thị
- **Tối ưu hóa hiệu suất** nơi logic không rõ ràng
- **Chuẩn bị code review** - các câu hỏi giúp bạn suy nghĩ về các thay đổi của mình

### Ví Dụ Sử Dụng

**Chế độ tương tác cơ bản:**

```sh
gac -i
```

Điều này sẽ:

1. Hiển thị tóm tắt các thay đổi đã staged
2. Đặt câu hỏi về các thay đổi
3. Tạo thông điệp commit với câu trả lời của bạn
4. Yêu cầu xác nhận (hoặc tự động xác nhận khi kết hợp với `-y`)

**Chế độ tương tác với các thay đổi đã staged:**

```sh
gac -ai
# Stage tất cả các thay đổi, sau đó đặt câu hỏi để có ngữ cảnh tốt hơn
```

**Chế độ tương tác với các gợi ý cụ thể:**

```sh
gac -i -h "Di chuyển cơ sở dữ liệu cho hồ sơ người dùng"
# Đặt câu hỏi trong khi cung cấp gợi ý cụ thể để tập trung LLM
```

**Chế độ tương tác với đầu ra chi tiết:**

```sh
gac -i -v
# Đặt câu hỏi và tạo thông điệp commit chi tiết, có cấu trúc
```

**Chế độ tương tác xác nhận tự động:**

```sh
gac -i -y
# Đặt câu hỏi nhưng tự động xác nhận commit kết quả
```

### Quy Trình Hỏi-Đáp

Quy trình tương tác theo mẫu này:

1. **Xem xét thay đổi** - gac hiển thị tóm tắt những gì bạn đang commit
2. **Trả lời câu hỏi** - trả lời mỗi prompt với các chi tiết liên quan
3. **Cải thiện ngữ cảnh** - câu trả lời của bạn được thêm vào LLM prompt
4. **Tạo thông điệp** - LLM tạo thông điệp commit với ngữ cảnh đầy đủ
5. **Xác nhận** - xem xét và xác nhận commit (hoặc tự động với `-y`)

**Mẹo cho câu trả lời hữu ích:**

- **Ngắn gọn nhưng đầy đủ** - cung cấp các chi tiết quan trọng mà không quá dài dòng
- **Tập trung vào "tại sao"** - giải thích lý do đằng sau các thay đổi của bạn
- **Đề cập các giới hạn** - ghi chú các giới hạn hoặc cân nhắc đặc biệt
- **Liên kết ngữ cảnh bên ngoài** - tham chiếu các issues, tài liệu hoặc tài liệu thiết kế
- **Câu trả lời trống cũng được** - nếu câu hỏi không áp dụng, chỉ cần nhấn Enter

### Kết Hợp Với Các Flag Khác

Chế độ tương tác hoạt động tốt với hầu hết các flag khác:

```sh
# Stage tất cả các thay đổi và đặt câu hỏi
gac -ai

# Đặt câu hỏi với đầu ra chi tiết
gac -i -v
```

### Thực T hành Tốt Nhất

- **Sử dụng cho các PR phức tạp** - đặc biệt hữu ích cho các pull request cần giải thích chi tiết
- **Hợp tác nhóm** - các câu hỏi giúp bạn suy nghĩ về các thay đổi mà người khác sẽ xem xét
- **Chuẩn bị tài liệu** - câu trả lời của bạn có thể giúp hình thành cơ sở cho release notes
- **Công cụ học tập** - các câu hỏi củng cố các thực hành tốt cho thông điệp commit
- **Bỏ qua cho các thay đổi đơn giản** - cho các sửa đổi tầm thường, chế độ cơ bản có thể nhanh hơn

## Nhận Trợ Giúp

- Đối với gợi ý hệ thống tùy chỉnh, xem [docs/CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md)
- Đối với xử lý sự cố và mẹo nâng cao, xem [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Đối với cài đặt và cấu hình, xem [README.md#installation-and-configuration](README.md#installation-and-configuration)
- Để đóng góp, xem [docs/CONTRIBUTING.md](CONTRIBUTING.md)
- Thông tin giấy phép: [LICENSE](../LICENSE)
