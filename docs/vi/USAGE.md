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
  - [Thống Kê Sử Dụng](#thống-kê-sử-dụng)
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
- `e` hoặc `edit` - Chỉnh sửa thông điệp commit. Mặc định mở TUI tại chỗ với phím tắt vi/emacs. Đặt `GAC_EDITOR` để mở trình soạn thảo ưa thích (vd., `GAC_EDITOR=code gac` cho VS Code, `GAC_EDITOR=vim gac` cho vim)
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
| `--signoff`          |      | Thêm dòng Signed-off-by vào thông điệp commit (tuân thủ DCO)             |
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
| `--50-72`           |      | Áp dụng quy tắc 50/72 cho định dạng thông điệp commit             |

**Lưu ý:** Cờ `--50-72` áp dụng [quy tắc 50/72](https://www.conventionalcommits.org/en/v1.0.0/#summary) trong đó:

- Dòng chủ đề: tối đa 50 ký tự
- Các dòng nội dung: tối đa 72 ký tự mỗi dòng
- Điều này giữ cho thông điệp commit dễ đọc trong `git log --oneline` và giao diện GitHub

Bạn cũng có thể đặt `GAC_USE_50_72_RULE=true` trong tệp `.gac.env` của mình để luôn áp dụng quy tắc này.

**Lưu ý:** Bạn có thể cung cấp phản hồi một cách tương tác bằng cách chỉ cần gõ nó tại gợi ý xác nhận - không cần tiền tố với 'r'. Gõ `r` để reroll đơn giản, `e` để chỉnh sửa thông điệp (TUI tại chỗ mặc định, hoặc `$GAC_EDITOR` nếu đã đặt), hoặc gõ phản hồi của bạn trực tiếp như `làm nó ngắn hơn`.

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

### Dòng Signed-off-by (Tuân thủ DCO)

gac hỗ trợ thêm dòng `Signed-off-by` vào thông điệp commit, được yêu cầu cho việc tuân thủ [Developer Certificate of Origin (DCO)](https://developercertificate.org/) trong nhiều dự án mã nguồn mở.

**Thêm signoff :**

```sh
gac --signoff  # Thêm dòng Signed-off-by vào thông điệp commit (tuân thủ DCO)
```

**Để bật vĩnh viễn :** Đặt `GAC_SIGNOFF=true` trong tệp `.gac.env` của bạn, hoặc thêm `signoff=true` vào cấu hình của bạn.

**Chức năng :**

- Thêm `Signed-off-by: Tên của bạn <your.email@example.com>` vào thông điệp commit
- Sử dụng cấu hình git của bạn (`user.name` và `user.email`) cho dòng này
- Yêu cầu cho các dự án như Cherry Studio, Linux kernel và các dự án khác sử dụng DCO

**Thiết lập danh tính git :**

Đảm bảo cấu hình git của bạn có tên và email chính xác :

```sh
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"
```

**Lưu ý :** Dòng Signed-off-by được thêm bởi git trong quá trình commit, không phải bởi AI trong quá trình tạo thông điệp. Bạn sẽ không thấy nó trong bản xem trước, nhưng nó sẽ có trong commit cuối cùng (kiểm tra bằng `git log -1`).

## Ghi Chú Cấu Hình

- Cách được đề xuất để thiết lập gac là chạy `gac init` và làm theo các gợi ý tương tác.
- Đã cấu hình ngôn ngữ và chỉ cần chuyển đổi nhà cung cấp hoặc mô hình? Chạy `gac model` để lặp lại thiết lập mà không có câu hỏi ngôn ngữ.
- **Đang sử dụng Claude Code?** Xem [hướng dẫn thiết lập Claude Code](CLAUDE_CODE.md) để biết hướng dẫn xác thực OAuth.
- **Đang sử dụng ChatGPT OAuth?** Xem [hướng dẫn thiết lập ChatGPT OAuth](CHATGPT_OAUTH.md) để biết hướng dẫn xác thực trình duyệt.
- **Đang sử dụng GitHub Copilot?** Xem [hướng dẫn thiết lập GitHub Copilot](GITHUB_COPILOT.md) để biết hướng dẫn xác thực Device Flow.
- gac tải cấu hình theo thứ tự ưu tiên sau:
  1. Các flag CLI
  2. Các biến môi trường
  3. Cấp dự án `.gac.env`
  4. Cấp người dùng `~/.gac.env`

### Tùy Chọn Cấu Hình Nâng Cao

Bạn có thể tùy chỉnh hành vi của gac với các biến môi trường tùy chọn này:

- `GAC_EDITOR=code --wait` - Ghi đè trình soạn thảo được sử dụng khi bạn nhấn `e` tại gợi ý xác nhận. Mặc định, `e` mở TUI tại chỗ; đặt `GAC_EDITOR` sẽ chuyển sang trình soạn thảo ngoài. Hỗ trợ bất kỳ lệnh trình soạn thảo nào với đối số. Cờ chờ (`--wait`/`-w`) được tự động chèn cho các trình soạn thảo GUI đã biết (VS Code, Cursor, Zed, Sublime Text) để quy trình chặn cho đến khi bạn đóng tệp
- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Tự động suy luận và bao gồm phạm vi trong thông điệp commit (ví dụ, `feat(auth):` so với `feat:)
- `GAC_VERBOSE=true` - Tạo thông điệp commit chi tiết với các phần động cơ, kiến trúc và tác động
- `GAC_USE_50_72_RULE=true` - Luôn áp dụng quy tắc 50/72 cho thông điệp commit (chủ đề ≤50 ký tự, các dòng nội dung ≤72 ký tự)
- `GAC_SIGNOFF=true` - Luôn thêm dòng Signed-off-by vào commit (để tuân thủ DCO)
- `GAC_TEMPERATURE=0.7` - Kiểm soát sự sáng tạo của LLM (0.0-1.0, thấp hơn = tập trung hơn)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Token tối đa cho thông điệp đã tạo (tự động scale 2-5x khi sử dụng `--group` dựa trên số lượng tệp; ghi đè để đi cao hơn hoặc thấp hơn)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Cảnh báo khi các gợi ý vượt quá số lượng token này
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Sử dụng gợi ý hệ thống tùy chỉnh để tạo thông điệp commit
- `GAC_LANGUAGE=Spanish` - Tạo thông điệp commit bằng ngôn ngữ cụ thể (ví dụ, Spanish, French, Japanese, German). Hỗ trợ tên đầy đủ hoặc mã ISO (es, fr, ja, de, zh-CN). Sử dụng `gac language` để lựa chọn tương tác
- `GAC_TRANSLATE_PREFIXES=true` - Dịch các tiền tố commit tiêu chuẩn (feat, fix, v.v.) vào ngôn ngữ đích (mặc định: false, giữ tiền tố bằng tiếng Anh)
- `GAC_SKIP_SECRET_SCAN=true` - Vô hiệu hóa quét bảo mật tự động cho các bí mật trong các thay đổi đã staged (sử dụng cẩn thận)
- `GAC_NO_VERIFY_SSL=true` - Bỏ qua xác minh chứng chỉ SSL cho các cuộc gọi API (hữu ích cho proxy doanh nghiệp chặn lưu lượng SSL)
- `GAC_DISABLE_STATS=true` - Vô hiệu hóa theo dõi thống kê sử dụng (không đọc hoặc ghi tệp thống kê; dữ liệu hiện có được bảo tồn). Chỉ giá trị truthy vô hiệu hóa thống kê; đặt thành `false`/`0`/`no`/`off` giữ thống kê được bật, giống như để biến không xác định

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
- `gac auth chatgpt login` — Đăng nhập vào ChatGPT sử dụng OAuth (mở trình duyệt)
- `gac auth chatgpt logout` — Đăng xuất khỏi ChatGPT và xóa token đã lưu
- `gac auth chatgpt status` — Kiểm tra trạng thái xác thực ChatGPT OAuth
- `gac auth copilot login` — Đăng nhập GitHub Copilot bằng Device Flow
- `gac auth copilot login --host ghe.mycompany.com` — Đăng nhập Copilot trên phiên bản GitHub Enterprise
- `gac auth copilot logout` — Đăng xuất Copilot và xóa token đã lưu
- `gac auth copilot status` — Kiểm tra trạng thái xác thực Copilot
- `gac config show` — Hiển thị cấu hình hiện tại
- `gac config set KEY VALUE` — Đặt khóa cấu hình trong `$HOME/.gac.env`
- `gac config get KEY` — Lấy giá trị cấu hình
- `gac config unset KEY` — Xóa khóa cấu hình khỏi `$HOME/.gac.env`
- `gac language` (hoặc `gac lang`) — Trình chọn ngôn ngữ tương tác cho các thông điệp commit (đặt GAC_LANGUAGE)
- `gac editor` (hoặc `gac edit`) — Bộ chọn editor tương tác cho phím `e` tại prompt xác nhận (đặt GAC_EDITOR)
- `gac diff` — Hiển thị git diff đã lọc với các tùy chọn cho các thay đổi đã được staged/chưa staged, màu sắc và cắt bớt
- `gac serve` — Khởi động GAC như một [MCP server](MCP.md) để tích hợp AI agent (truyền tải stdio)
- `gac stats show` — Xem thống kê sử dụng gac của bạn (tổng số, chuỗi, hoạt động hàng ngày & hàng tuần, sử dụng token, dự án hàng đầu, mô hình hàng đầu)
- `gac stats models` — Xem thống kê chi tiết cho tất cả mô hình với phân tích token và biểu đồ so sánh tốc độ
- `gac stats projects` — Xem thống kê tất cả dự án với phân tích token
- `gac stats reset` — Đặt lại tất cả thống kê về không (yêu cầu xác nhận)

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

## Thống Kê Sử Dụng

gac theo dõi thống kê sử dụng nhẹ để bạn có thể xem hoạt động commit, chuỗi, sử dụng token, và các dự án và mô hình tích cực nhất của mình. Thống kê được lưu trữ cục bộ trong `~/.gac_stats.json` và không bao giờ được gửi đi đâu — không có thu thập dữ liệu từ xa.

**Được theo dõi:** tổng số lần chạy gac, tổng số commit, tổng token prompt và completion, ngày sử dụng đầu/cuối, số đếm hàng ngày và hàng tuần (gacs, commits, tokens), chuỗi hiện tại và dài nhất, hoạt động theo dự án (gacs, commits, token prompt + completion) và hoạt động theo mô hình (gacs, token prompt + completion).

**Không được theo dõi:** thông điệp commit, nội dung mã, đường dẫn tệp, thông tin cá nhân, hoặc bất cứ điều gì ngoài số đếm, ngày tháng, tên dự án (lấy từ git remote hoặc tên thư mục) và tên mô hình.

### Chọn tham gia hoặc từ chối

`gac init` hỏi bạn có muốn bật thống kê và giải thích chính xác những gì được lưu trữ. Bạn có thể thay đổi ý kiến bất cứ lúc nào:

- **Bật thống kê:** bỏ đặt `GAC_DISABLE_STATS` hoặc đặt thành `false`/`0`/`no`/`off`/rỗng.
- **Vô hiệu hóa thống kê:** đặt `GAC_DISABLE_STATS` thành giá trị truthy (`true`, `1`, `yes`, `on`).

Khi bạn từ chối thống kê trong `gac init` và phát hiện tệp `~/.gac_stats.json` hiện có, bạn sẽ được đề xuất tùy chọn xóa nó.

### Lệnh Con Thống Kê

| Lệnh                 | Mô tả                                                                                                                      |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `gac stats`          | Hiển thị thống kê của bạn (giống như `gac stats show`)                                                                     |
| `gac stats show`     | Hiển thị thống kê đầy đủ: tổng số, chuỗi, hoạt động hàng ngày & hàng tuần, sử dụng token, dự án hàng đầu, mô hình hàng đầu |
| `gac stats models`   | Hiển thị thống kê chi tiết cho **tất cả** các mô hình đã sử dụng, với phân tích token và biểu đồ so sánh tốc độ            |
| `gac stats projects` | Hiển thị thống kê **tất cả** các dự án với phân tích token                                                                 |
| `gac stats reset`    | Đặt lại tất cả thống kê về không (yêu cầu xác nhận)                                                                        |

### Ví Dụ

```sh
# Xem thống kê tổng thể của bạn
gac stats

# Phân tích chi tiết tất cả các mô hình đã sử dụng
gac stats models

# Thống kê tất cả dự án
gac stats projects

# Đặt lại tất cả thống kê (với yêu cầu xác nhận)
gac stats reset
```

### Những Gì Bạn Sẽ Thấy

Chạy `gac stats` hiển thị:

- **Tổng số gac và commit** — bao nhiêu lần bạn đã sử dụng gac và bao nhiêu commit nó đã tạo
- **Chuỗi hiện tại và dài nhất** — các ngày liên tiếp có hoạt động gac (🔥 ở 5+ ngày)
- **Tóm tắt hoạt động** — gac, commit và token hôm nay và tuần này so với ngày đỉnh và tuần đỉnh của bạn
- **Dự án hàng đầu** — 5 repo tích cực nhất của bạn theo số gac + commit, với sử dụng token theo dự án

Running `gac stats projects` hiển thị **tất cả** các dự án (không chỉ 5 dự án hàng đầu) với:

- **Bảng tất cả dự án** — mỗi dự án được sắp xếp theo hoạt động, với số gac, số commit, token prompt, token completion, token suy luận và tổng token
- **Mô hình hàng đầu** — 5 mô hình được sử dụng nhiều nhất với token prompt, completion và tổng số đã tiêu thụ

Running `gac stats models` hiển thị **tất cả** các mô hình (không chỉ 5 mô hình hàng đầu) với:

- **Bảng tất cả mô hình** — mỗi mô hình đã sử dụng được sắp xếp theo hoạt động, với số gac, tốc độ (token/giây), token prompt, token completion, token suy luận và tổng token
- **Biểu đồ so sánh tốc độ** — biểu đồ thanh ngang của tất cả các mô hình có tốc độ đã biết, sắp xếp từ nhanh nhất đến chậm nhất, mã màu theo phần trăm tốc độ (🟡 siêu nhanh, 🟢 nhanh, 🔵 vừa phải, 🔘 chậm)
- **Ăn mừng điểm cao** — 🏆 cúp khi bạn thiết lập kỷ lục hàng ngày, hàng tuần, token, hoặc chuỗi mới; 🥈 khi ngang bằng
- **Tin nhắn khích lệ** — những nhắc nhở theo ngữ cảnh dựa trên hoạt động của bạn

### Vô Hiệu Hóa Thống Kê

Đặt biến môi trường `GAC_DISABLE_STATS` thành giá trị truthy:

```sh
# Vô hiệu hóa theo dõi thống kê
export GAC_DISABLE_STATS=true

# Hoặc trong .gac.env
GAC_DISABLE_STATS=true
```

Giá trị falsy (`false`, `0`, `no`, `off`, rỗng) giữ thống kê được bật — giống như để biến không xác định.

Khi bị vô hiệu hóa, gac bỏ qua tất cả việc ghi thống kê — không có đọc hoặc ghi tệp nào xảy ra. Dữ liệu hiện có được bảo tồn nhưng sẽ không được cập nhật cho đến khi bạn bật lại.

---

## Nhận Trợ Giúp

- Để thiết lập MCP server (tích hợp AI agent), xem [docs/MCP.md](MCP.md)
- Đối với gợi ý hệ thống tùy chỉnh, xem [docs/CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md)
- Để thiết lập Claude Code OAuth, xem [CLAUDE_CODE.md](CLAUDE_CODE.md)
- Để thiết lập ChatGPT OAuth, xem [CHATGPT_OAUTH.md](CHATGPT_OAUTH.md)
- Để thiết lập GitHub Copilot, xem [GITHUB_COPILOT.md](GITHUB_COPILOT.md)
- Đối với xử lý sự cố và mẹo nâng cao, xem [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Đối với cài đặt và cấu hình, xem [README.md#installation-and-configuration](README.md#installation-and-configuration)
- Để đóng góp, xem [docs/CONTRIBUTING.md](CONTRIBUTING.md)
- Thông tin giấy phép: [LICENSE](../LICENSE)
