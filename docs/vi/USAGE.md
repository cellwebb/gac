# Sử Dụng Dòng Lệnh gac

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | **Tiếng Việt** | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md)

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
  - [Ghi Chú Cấu Hình](#ghi-chú-cấu-hình)
    - [Tùy Chọn Cấu Hình Nâng Cao](#tùy-chọn-cấu-hình-nâng-cao)
    - [Lệnh Con Cấu Hình](#lệnh-con-cấu-hình)
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

| Flag / Tùy chọn      | Ngắn | Mô tả                                                           |
| -------------------- | ---- | --------------------------------------------------------------- |
| `--add-all`          | `-a` | Stage tất cả các thay đổi trước khi committing                  |
| `--group`            | `-g` | Nhóm các thay đổi đã staged thành nhiều commit logic            |
| `--push`             | `-p` | Push thay đổi đến remote sau khi committing                     |
| `--yes`              | `-y` | Tự động xác nhận commit mà không cần gợi ý                      |
| `--dry-run`          |      | Hiển thị những gì sẽ xảy ra mà không thực hiện thay đổi nào     |
| `--no-verify`        |      | Bỏ qua các hook pre-commit và lefthook khi committing           |
| `--skip-secret-scan` |      | Bỏ qua quét bảo mật cho các bí mật trong các thay đổi đã staged |

**Lưu ý:** Kết hợp `-a` và `-g` (tức là `-ag`) để stage TẤT CẢ các thay đổi trước, sau đó nhóm chúng vào các commit.

**Lưu ý:** Khi sử dụng `--group`, giới hạn token đầu ra tối đa được tự động scale dựa trên số lượng tệp đang được commit (2x cho 1-9 tệp, 3x cho 10-19 tệp, 4x cho 20-29 tệp, 5x cho 30+ tệp). Điều này đảm bảo LLM có đủ token để tạo tất cả các commit được nhóm mà không bị cắt ngắn, ngay cả với các thay đổi lớn.

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
  gac -m anthropic:claude-3-5-haiku-latest
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

## Ghi Chú Cấu Hình

- Cách được đề xuất để thiết lập gac là chạy `gac init` và làm theo các gợi ý tương tác.
- Đã cấu hình ngôn ngữ và chỉ cần chuyển đổi nhà cung cấp hoặc mô hình? Chạy `gac model` để lặp lại thiết lập mà không có câu hỏi ngôn ngữ.
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

Xem `.gac.env.example` cho mẫu cấu hình hoàn chỉnh.

Để được hướng dẫn chi tiết về việc tạo gợi ý hệ thống tùy chỉnh, xem [docs/CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md).

### Lệnh Con Cấu Hình

Các lệnh con sau đây có sẵn:

- `gac init` — Trình hướng dẫn thiết lập tương tác cho cấu hình nhà cung cấp, mô hình và ngôn ngữ
- `gac model` — Thiết lập nhà cung cấp/mô hình/khóa API mà không có gợi ý ngôn ngữ (lý tưởng cho việc chuyển nhanh)
- `gac config show` — Hiển thị cấu hình hiện tại
- `gac config set KEY VALUE` — Đặt khóa cấu hình trong `$HOME/.gac.env`
- `gac config get KEY` — Lấy giá trị cấu hình
- `gac config unset KEY` — Xóa khóa cấu hình khỏi `$HOME/.gac.env`
- `gac language` (hoặc `gac lang`) — Trình chọn ngôn ngữ tương tác cho thông điệp commit (đặt GAC_LANGUAGE)
- `gac diff` — Hiển thị git diff được lọc với các tùy chọn cho thay đổi staged/unstaged, màu sắc và cắt ngắn

## Nhận Trợ Giúp

- Đối với gợi ý hệ thống tùy chỉnh, xem [docs/CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md)
- Đối với xử lý sự cố và mẹo nâng cao, xem [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Đối với cài đặt và cấu hình, xem [README.md#installation-and-configuration](README.md#installation-and-configuration)
- Để đóng góp, xem [docs/CONTRIBUTING.md](CONTRIBUTING.md)
- Thông tin giấy phép: [LICENSE](../LICENSE)
