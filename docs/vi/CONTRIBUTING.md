# Đóng Góp cho gac

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | **Tiếng Việt** | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Norsk](../no/CONTRIBUTING.md) | [Svenska](../sv/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md) | [Italiano](../it/CONTRIBUTING.md)

Cảm ơn sự quan tâm của bạn trong việc đóng góp cho dự án này! Sự trợ giúp của bạn được đánh giá cao. Vui lòng làm theo các hướng dẫn này để
làm cho quy trình suôn sẻ cho mọi người.

## Mục Lục

- [Đóng Góp cho gac](#đóng-góp-cho-gac)
  - [Mục Lục](#mục-lục)
  - [Thiết Lập Môi Trường Phát Triển](#thiết-lập-môi-trường-phát-triển)
    - [Thiết Lập Nhanh](#thiết-lập-nhanh)
    - [Thiết Lập Thay Thế (nếu bạn thích từng bước)](#thiết-lập-thay-thể-nếu-bạn-thích-từng-bước)
    - [Các Lệnh Có Sẵn](#các-lệnh-có-sẵn)
  - [Tăng Phiên Bản](#tăng-phiên-bản)
    - [Cách tăng phiên bản](#cách-tăng-phiên-bản)
    - [Quy Trình Phát Hành](#quy-trình-phát-hành)
    - [Sử dụng bump-my-version (tùy chọn)](#sử-dụng-bump-my-version-tùy-chọn)
  - [Thêm Nhà Cung Cấp AI Mới](#thêm-nhà-cung-cấp-ai-mới)
    - [Checklist để Thêm Nhà Cung Cấp Mới](#checklist-để-thêm-nhà-cung-cấp-mới)
    - [Ví Dụ Triển Khai](#ví-dụ-triển-khai)
    - [Điểm Chính](#điểm-chính)
  - [Tiêu Chuẩn Lập Trình](#tiêu-chuẩn-lập-trình)
  - [Git Hooks (Lefthook)](#git-hooks-lefthook)
    - [Thiết Lập](#thiết-lập)
    - [Bỏ Qua Git Hooks](#bỏ-qua-git-hooks)
  - [Hướng Dẫn Kiểm Thử](#hướng-dẫn-kiểm-thử)
    - [Chạy Kiểm Thử](#chạy-kiểm-thử)
      - [Kiểm Thử Tích Hợp Nhà Cung Cấp](#kiểm-thử-tích-hợp-nhà-cung-cấp)
  - [Bộ Quy Tắc Ứng Xử](#bộ-quy-tắc-ứng-xử)
  - [Giấy Phép](#giấy-phép)
  - [Nơi để Nhận Trợ Giúp](#nơi-để-nhận-trợ-giúp)

## Thiết Lập Môi Trường Phát Triển

Dự án này sử dụng `uv` để quản lý phụ thuộc và cung cấp Makefile cho các tác vụ phát triển phổ biến:

### Thiết Lập Nhanh

```bash
# Một lệnh để thiết lập mọi thứ bao gồm cả Lefthook hooks
make dev
```

Lệnh này sẽ:

- Cài đặt phụ thuộc phát triển
- Cài đặt git hooks
- Chạy Lefthook hooks trên tất cả các tệp để sửa bất kỳ vấn đề hiện có nào

### Thiết Lập Thay Thể (nếu bạn thích từng bước)

```bash
# Tạo môi trường ảo và cài đặt phụ thuộc
make setup

# Cài đặt phụ thuộc phát triển
make dev

# Cài đặt Lefthook hooks
brew install lefthook  # hoặc xem tài liệu dưới đây cho các thay thế
lefthook install
lefthook run pre-commit --all
```

### Các Lệnh Có Sẵn

- `make setup` - Tạo môi trường ảo và cài đặt tất cả phụ thuộc
- `make dev` - **Thiết lập phát triển hoàn chỉnh** - bao gồm Lefthook hooks
- `make test` - Chạy kiểm thử tiêu chuẩn (loại trừ kiểm thử tích hợp)
- `make test-integration` - Chỉ chạy kiểm thử tích hợp (yêu cầu khóa API)
- `make test-all` - Chạy tất cả kiểm thử
- `make test-cov` - Chạy kiểm thử với báo cáo độ phủ
- `make lint` - Kiểm tra chất lượng mã (ruff, prettier, markdownlint)
- `make format` - Tự động sửa các vấn đề định dạng mã

## Tăng Phiên Bản

**Quan trọng**: PR nên bao gồm việc tăng phiên bản trong `src/gac/__version__.py` khi chúng chứa các thay đổi nên được phát hành.

### Cách Tăng Phiên Bản

1. Chỉnh sửa `src/gac/__version__.py` và tăng số phiên bản
2. Làm theo [Semantic Versioning](https://semver.org/):
   - **Patch** (1.6.X): Sửa lỗi, cải tiến nhỏ
   - **Minor** (1.X.0): Tính năng mới, thay đổi tương thích ngược (ví dụ, thêm nhà cung cấp mới)
   - **Major** (X.0.0): Thay đổi break

### Quy Trình Phát Hành

Các bản phát hành được kích hoạt bằng cách đẩy các tag phiên bản:

1. Hợp nhất PR(s) với tăng phiên bản vào main
2. Tạo tag: `git tag v1.6.1`
3. Đẩy tag: `git push origin v1.6.1`
4. GitHub Actions tự động phát hành lên PyPI

Ví dụ:

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # Tăng từ 1.6.0
```

### Sử dụng bump-my-version (tùy chọn)

Nếu bạn đã cài đặt `bump-my-version`, bạn có thể sử dụng nó tại địa phương:

```bash
# Đối với sửa lỗi:
bump-my-version bump patch

# Đối với tính năng mới:
bump-my-version bump minor

# Đối với thay đổi break:
bump-my-version bump major
```

## Thêm Nhà Cung Cấp AI Mới

Khi thêm nhà cung cấp AI mới, bạn cần cập nhật nhiều tệp trên toàn bộ codebase. Làm theo checklist toàn diện này:

### Checklist để Thêm Nhà Cung Cấp Mới

- [ ] **1. Tạo Triển Khai Nhà Cung Cấp** (`src/gac/providers/<provider_name>.py`)

  - Tạo tệp mới được đặt tên theo nhà cung cấp (ví dụ, `minimax.py`)
  - Triển khai `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str`
  - Sử dụng định dạng tương thích OpenAI nếu nhà cung cấp hỗ trợ nó
  - Xử lý khóa API từ biến môi trường `<PROVIDER>_API_KEY`
  - Bao gồm xử lý lỗi thích hợp với các loại `AIError`:
    - `AIError.authentication_error()` cho các vấn đề xác thực
    - `AIError.rate_limit_error()` cho giới hạn tốc độ (HTTP 429)
    - `AIError.timeout_error()` cho timeout
    - `AIError.model_error()` cho lỗi mô hình và nội dung rỗng/null
  - Đặt URL endpoint API
  - Sử dụng timeout 120 giây cho các yêu cầu HTTP

- [ ] **2. Đăng Ký Nhà Cung Cấp trong Gói** (`src/gac/providers/__init__.py`)

  - Thêm import: `from .<provider> import call_<provider>_api`
  - Thêm vào từ điển `PROVIDER_REGISTRY`: `"provider-name": call_<provider>_api`
  - Thêm vào danh sách `__all__`: `"call_<provider>_api"`

- [ ] **3. Cập Nhật Cấu Hình Ví Dụ** (`.gac.env.example`)

  - Thêm cấu hình mô hình ví dụ trong định dạng: `# GAC_MODEL=provider:model-name`
  - Thêm mục nhập khóa API: `# <PROVIDER>_API_KEY=your_key_here`
  - Giữ các mục nhập được sắp xếp theo bảng chữ cái
  - Thêm bình luận cho các khóa tùy chọn nếu áp dụng

- [ ] **4. Cập Nhật Tài Liệu** (`README.md` và tất cả các bản dịch `README.md` trong `docs/`)

  - Thêm tên nhà cung cấp vào phần "Nhà Cung Cấp Hỗ Trợ" trong tất cả các README dịch
  - Giữ danh sách được sắp xếp theo bảng chữ cái trong các dấu đầu dòng của nó

- [ ] **5. Thêm vào Thiết Lập Tương Tác** (`src/gac/init_cli.py`)

  - Thêm tuple vào danh sách `providers`: `("Provider Name", "default-model-name")`
  - Giữ danh sách được sắp xếp theo bảng chữ cái
  - **Quan trọng**: Nếu nhà cung cấp của bạn sử dụng tên khóa API không tiêu chuẩn (không phải `{PROVIDER_UPPERCASE}_API_KEY` được tạo tự động), hãy thêm xử lý đặc biệt:

    ```python
    elif provider_key == "your-provider-key":
        api_key_name = "YOUR_CUSTOM_API_KEY_NAME"
    ```

    Ví dụ: `kimi-for-coding` sử dụng `KIMI_CODING_API_KEY`, `moonshot-ai` sử dụng `MOONSHOT_API_KEY`

- [ ] **6. Tạo Kiểm Thử Toàn Diện** (`tests/providers/test_<provider>.py`)

  - Tạo tệp kiểm thử làm theo quy ước đặt tên
  - Bao gồm các lớp kiểm thử này:
    - `Test<Provider>Imports` - Kiểm thử nhập module và hàm
    - `Test<Provider>APIKeyValidation` - Kiểm thử lỗi khóa API bị thiếu
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - Kế thừa từ `BaseProviderTest` cho 9 kiểm thử tiêu chuẩn
    - `Test<Provider>EdgeCases` - Kiểm thử nội dung rỗng và các trường hợp cạnh khác
    - `Test<Provider>Integration` - Kiểm thử cuộc gọi API thực (đánh dấu với `@pytest.mark.integration`)
  - Triển khai các thuộc tính bắt buộc trong lớp kiểm thử mock:
    - `provider_name` - Tên nhà cung cấp (chữ thường)
    - `provider_module` - Đường dẫn module đầy đủ
    - `api_function` - Tham chiếu hàm API
    - `api_key_env_var` - Tên biến môi trường cho khóa API (hoặc None cho nhà cung cấp địa phương)
    - `model_name` - Tên mô hình mặc định để kiểm thử
    - `success_response` - Phản hồi API thành công mock
    - `empty_content_response` - Phản hồi nội dung rỗng mock

- [ ] **7. Tăng Phiên Bản** (`src/gac/__version__.py`)
  - Tăng phiên bản **thứ** (ví dụ, 1.10.2 → 1.11.0)
  - Thêm nhà cung cấp là một tính năng mới và yêu cầu tăng phiên bản thứ

### Ví Dụ Triển Khai

Xem triển khai nhà cung cấp MiniMax làm tài liệu tham khảo:

- Nhà cung cấp: `src/gac/providers/minimax.py`
- Kiểm thử: `tests/providers/test_minimax.py`

### Điểm Chính

1. **Xử Lỗi**: Luôn sử dụng loại `AIError` thích hợp cho các kịch bản lỗi khác nhau
2. **Nội Dung Rỗng**: Luôn kiểm tra cả nội dung `None` và chuỗi rỗng trong các phản hồi
3. **Kiểm Thử**: Lớp `BaseProviderTest` cung cấp 9 kiểm thử tiêu chuẩn mà mọi nhà cung cấp nên kế thừa
4. **Thứ Tự Bảng Chữ Cái**: Giữ danh sách nhà cung cấp được sắp xếp theo bảng chữ cái để dễ bảo trì
5. **Đặt Tên Khóa API**: Sử dụng định dạng `<PROVIDER>_API_KEY` (toàn bộ chữ hoa, gạch dưới cho khoảng trắng)
6. **Đăng Ký Nhà Cung Cấp**: Chỉ thay đổi `src/gac/providers/__init__.py` và `src/gac/init_cli.py` – `ai.py` và `ai_utils.py` tự động đọc từ registry
7. **Định Dạng Tên Nhà Cung Cấp**: Sử dụng chữ thường với dấu gạch ngang cho các tên nhiều từ (ví dụ, "lm-studio")
8. **Tăng Phiên Bản**: Thêm nhà cung cấp yêu cầu tăng phiên bản **thứ** (tính năng mới)

## Tiêu Chuẩn Lập Trình

- Target Python 3.10+ (3.10, 3.11, 3.12, 3.13, 3.14)
- Sử dụng type hints cho tất cả tham số hàm và giá trị trả về
- Giữ mã sạch, gọn và dễ đọc
- Tránh sự phức tạp không cần thiết
- Sử dụng logging thay vì các câu lệnh print
- Định dạng được xử lý bởi `ruff` (linting, định dạng và sắp xếp import trong một công cụ; độ dài dòng tối đa: 120)
- Viết kiểm thử tối thiểu, hiệu quả với `pytest`

## Git Hooks (Lefthook)

Dự án này sử dụng [Lefthook](https://github.com/evilmartians/lefthook) để giữ các kiểm tra chất lượng mã nhanh và nhất quán. Các hook được cấu hình phản ánh thiết lập pre-commit trước đây của chúng tôi:

- `ruff` - Linting và định dạng Python (thay thế black, isort và flake8)
- `markdownlint-cli2` - Linting Markdown
- `prettier` - Định dạng tệp (markdown, yaml, json)
- `check-upstream` - Hook tùy chỉnh để kiểm tra các thay đổi thượng nguồn

### Thiết Lập

**Cách tiếp cận được đề xuất:**

```bash
make dev
```

**Thiết lập thủ công (nếu bạn thích từng bước):**

1. Cài đặt Lefthook (lựa chọn tùy chọn phù hợp với thiết lập của bạn):

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # hoặc
   cargo install lefthook         # Rust toolchain
   # hoặc
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. Cài đặt các git hooks:

   ```sh
   lefthook install
   ```

3. (Tùy chọn) Chạy trên tất cả các tệp:

   ```sh
   lefthook run pre-commit --all
   ```

Các hook bây giờ sẽ chạy tự động trên mỗi commit. Nếu bất kỳ kiểm tra nào thất bại, bạn sẽ cần sửa các vấn đề trước khi commit.

### Bỏ Qua Git Hooks

Nếu bạn cần bỏ qua các kiểm tra Lefthook tạm thời, sử dụng flag `--no-verify`:

```sh
git commit --no-verify -m "Thông điệp commit của bạn"
```

Lưu ý: Chỉ nên sử dụng khi thực sự cần thiết, vì nó bỏ qua các kiểm tra chất lượng mã quan trọng.

## Hướng Dẫn Kiểm Thử

Dự án sử dụng pytest để kiểm thử. Khi thêm tính năng mới hoặc sửa lỗi, vui lòng bao gồm các kiểm thử bao gồm các thay đổi của bạn.

Lưu ý rằng thư mục `scripts/` chứa các kịch bản kiểm thử cho chức năng không thể dễ dàng kiểm thử với pytest. Cảm thấy tự do thêm các kịch bản ở đây để kiểm tra các kịch bản phức tạp hoặc kiểm thử tích hợp sẽ khó triển khai
sử dụng framework pytest tiêu chuẩn.

### Chạy Kiểm Thử

```sh
# Chạy kiểm thử tiêu chuẩn (loại trừ kiểm thử tích hợp với các cuộc gọi API thực)
make test

# Chỉ chạy kiểm thử tích hợp nhà cung cấp (yêu cầu khóa API)
make test-integration

# Chạy tất cả kiểm thử bao gồm kiểm thử tích hợp nhà cung cấp
make test-all

# Chạy kiểm thử với độ phủ
make test-cov

# Chạy tệp kiểm thử cụ thể
uv run -- pytest tests/test_prompt.py

# Chạy kiểm thử cụ thể
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### Kiểm Thử Tích Hợp Nhà Cung Cấp

Kiểm thử tích hợp nhà cung cấp thực hiện các cuộc gọi API thực để xác minh rằng các triển khai nhà cung cấp hoạt động chính xác với các API thực tế. Các kiểm thử này được đánh dấu với `@pytest.mark.integration` và bị bỏ qua theo mặc định để:

- Tránh tiêu thụ tín dụng API trong quá trình phát triển thông thường
- Ngăn ngừa thất bại kiểm thử khi các khóa API không được cấu hình
- Giữ thực hiện kiểm thử nhanh cho việc lặp lại nhanh chóng

Để chạy kiểm thử tích hợp nhà cung cấp:

1. **Thiết lập khóa API** cho các nhà cung cấp bạn muốn kiểm thử:

   ```sh
   export ANTHROPIC_API_KEY="your-key"
   export CEREBRAS_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export GROQ_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export OPENROUTER_API_KEY="your-key"
   export STREAMLAKE_API_KEY="your-key"
   export ZAI_API_KEY="your-key"
   # LM Studio và Ollama yêu cầu một phiên bản địa phương đang chạy
   # Khóa API cho LM Studio và Ollama là tùy chọn trừ khi triển khai của bạn thực thi xác thực
   ```

2. **Chạy kiểm thử nhà cung cấp**:

   ```sh
   make test-integration
   ```

Kiểm thử sẽ bỏ qua các nhà cung cấp nơi các khóa API không được cấu hình. Các kiểm thử này giúp phát hiện các thay đổi API sớm và đảm bảo tương thích với các API nhà cung cấp.

## Bộ Quy Tắc Ứng Xử

Tôn trọng và xây dựng. Sự quấy rối hoặc hành vi lạm dụng sẽ không được dung thứ.

## Giấy Phép

Bằng cách đóng góp, bạn đồng ý rằng các đóng góp của bạn sẽ được cấp phép dưới cùng giấy phép của dự án.

---

## Nơi để Nhận Trợ Giúp

- Đối với xử lý sự cố, xem [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Đối với việc sử dụng và các tùy chọn CLI, xem [USAGE.md](USAGE.md)
- Đối với chi tiết giấy phép, xem [../../LICENSE](../../LICENSE)

Cảm ơn đã giúp cải thiện gac!
