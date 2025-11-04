# Xử Lý Sự Cố gac

[English](../en/TROUBLESHOOTING.md) | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | [한국어](../ko/TROUBLESHOOTING.md) | [हिन्दी](../hi/TROUBLESHOOTING.md) | **Tiếng Việt** | [Français](../fr/TROUBLESHOOTING.md) | [Русский](../ru/TROUBLESHOOTING.md) | [Español](../es/TROUBLESHOOTING.md) | [Português](../pt/TROUBLESHOOTING.md) | [Norsk](../no/TROUBLESHOOTING.md) | [Svenska](../sv/TROUBLESHOOTING.md) | [Deutsch](../de/TROUBLESHOOTING.md) | [Nederlands](../nl/TROUBLESHOOTING.md) | [Italiano](../it/TROUBLESHOOTING.md)）

Hướng dẫn này bao gồm các vấn đề phổ biến và giải pháp cho việc cài đặt, cấu hình và chạy gac.

## Mục Lục

- [Xử Lý Sự Cố gac](#xử-lý-sự-cố-gac)
  - [Mục Lục](#mục-lục)
  - [1. Vấn Đề Cài Đặt](#1-vấn-đề-cài-đặt)
  - [2. Vấn Đề Cấu Hình](#2-vấn-đề-cấu-hình)
  - [3. Lỗi Nhà Cung Cấp/API](#3-lỗi-nhà-cung-cấpapi)
  - [4. Vấn Đề Nhóm Commit](#4-vấn-đề-nhóm-commit)
  - [5. Bảo Mật và Phát Hiện Bí Mật](#5-bảo-mật-và-phát-hiện-bí-mật)
  - [6. Vấn Đề Hooks Pre-commit và Lefthook](#6-vấn-đề-hooks-pre-commit-và-lefthook)
  - [7. Vấn Đề Quy Trình Phổ Biến](#common-workflow-issues)
  - [8. Gỡ Lỗi Chung](#8-gỡ-lỗi-chung)
  - [Vẫn Còn Kẹt?](#vẫn-còn-kẹt)
  - [Nơi để Nhận Trợ Giúp Thêm](#nơi-để-nhận-trợ-giúp-thêm)

## 1. Vấn Đề Cài Đặt

**Vấn đề:** Lệnh `gac` không tìm thấy sau khi cài đặt

- Đảm bảo bạn đã cài đặt với `uv tool install gac` hoặc `uvx gac`
- Nếu bạn đã sử dụng `uv tool install`, xác minh cài đặt với `uv tool list`
- Đảm bảo `uv` được cài đặt và trong `$PATH` của bạn
- Khởi động lại terminal của bạn sau khi cài đặt

**Vấn đề:** Từ chối quyền hoặc không thể ghi tệp

- Kiểm tra quyền thư mục
- Thử chạy với các quyền thích hợp hoặc thay đổi quyền sở hữu thư mục

## 2. Vấn Đề Cấu Hình

**Vấn đề:** gac không thể tìm thấy khóa API hoặc mô hình của bạn

- Nếu bạn mới, chạy `gac init` để thiết lập nhà cung cấp, mô hình và khóa API một cách tương tác
- Đảm bảo `.gac.env` hoặc các biến môi trường của bạn được đặt đúng
- Chạy `gac --log-level=debug` để xem các tệp cấu hình nào được tải và gỡ lỗi các vấn đề cấu hình
- Kiểm tra lỗi chính tả trong tên biến (ví dụ, `GAC_GROQ_API_KEY`)

**Vấn đề:** Thay đổi cấp người dùng `$HOME/.gac.env` không được nhận diện

- Đảm bảo bạn đang chỉnh sửa tệp đúng cho OS của bạn:
  - Trên macOS/Linux: `$HOME/.gac.env` (thường là `/Users/<tên-người-dùng-của-bạn>/.gac.env` hoặc `/home/<tên-người-dùng-của-bạn>/.gac.env`)
  - Trên Windows: `$HOME/.gac.env` (thường là `C:\Users\<tên-người-dùng-của-bạn>\.gac.env` hoặc sử dụng `%USERPROFILE%`)
- Chạy `gac --log-level=debug` để xác minh cấu hình cấp người dùng được tải
- Khởi động lại terminal hoặc chạy lại shell của bạn để tải lại các biến môi trường
- Nếu vẫn không hoạt động, kiểm tra lỗi chính tả và quyền tệp

**Vấn đề:** Thay đổi cấp dự án `.gac.env` không được nhận diện

- Đảm bảo dự án của bạn chứa tệp `.gac.env` trong thư mục gốc (tiếp theo với thư mục `.git` của bạn)
- Chạy `gac --log-level=debug` để xác minh cấu hình cấp dự án được tải
- Nếu bạn chỉnh sửa `.gac.env`, khởi động lại terminal hoặc chạy lại shell của bạn để tải lại các biến môi trường
- Nếu vẫn không hoạt động, kiểm tra lỗi chính tả và quyền tệp

**Vấn đề:** Không thể đặt hoặc thay đổi ngôn ngữ cho thông điệp commit

- Chạy `gac language` (hoặc `gac lang`) để chọn tương tác từ 25+ ngôn ngữ hỗ trợ
- Sử dụng flag `-l <language>` để ghi đè ngôn ngữ cho một commit duy nhất (ví dụ, `gac -l zh-CN`, `gac -l Spanish`)
- Kiểm tra cấu hình của bạn với `gac config show` để xem cài đặt ngôn ngữ hiện tại
- Cài đặt ngôn ngữ được lưu trữ trong `GAC_LANGUAGE` trong tệp `.gac.env` của bạn

## 3. Lỗi Nhà Cung Cấp/API

**Vấn đề:** Lỗi xác thực hoặc API

- Đảm bảo bạn đã đặt các khóa API đúng cho mô hình đã chọn (ví dụ, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- Kiểm tra lại khóa API và trạng thái tài khoản nhà cung cấp của bạn
- Đối với Ollama và LM Studio, xác nhận URL API khớp với phiên bản địa phương của bạn. Chỉ cần khóa API nếu bạn đã bật xác thực.

**Vấn đề:** Mô hình không có sẵn hoặc không được hỗ trợ

- Streamlake sử dụng ID endpoint suy luận thay vì tên mô hình. Đảm bảo bạn cung cấp ID endpoint từ console của họ.
- Xác minh tên mô hình là đúng và được nhà cung cấp của bạn hỗ trợ
- Kiểm tra tài liệu nhà cung cấp cho các mô hình có sẵn

## 4. Vấn Đề Nhóm Commit

**Vấn đề:** Flag `--group` không hoạt động như mong đợi

- Flag `--group` tự động phân tích các thay đổi đã staged và có thể tạo nhiều commit logic
- LLM có thể quyết định rằng một commit có ý nghĩa cho tập hợp các thay đổi đã staged của bạn, ngay cả với `--group`
- Đây là hành vi có chủ đích - LLM nhóm các thay đổi dựa trên các mối quan hệ logic, không chỉ số lượng
- Đảm bảo bạn có nhiều thay đổi không liên quan đã staged (ví dụ, sửa lỗi + thêm tính năng) để có kết quả tốt nhất
- Sử dụng `gac --show-prompt` để gỡ lỗi xem LLM đang thấy gì

**Vấn đề:** Các commit được nhóm không chính xác hoặc không được nhóm khi mong đợi

- Việc nhóm được xác định bởi phân tích của LLM về các thay đổi của bạn
- LLM có thể tạo một commit duy nhất nếu nó xác định rằng các thay đổi có liên quan logic
- Thử thêm gợi ý với `-h "gợi ý"` để hướng dẫn logic nhóm (ví dụ, `-h "tách sửa lỗi khỏi tái cấu trúc"`)
- Xem lại các nhóm đã tạo trước khi xác nhận
- Nếu nhóm không hoạt động tốt cho trường hợp sử dụng của bạn, hãy commit các thay đổi riêng biệt thay thế

## 5. Bảo Mật và Phát Hiện Bí Mật

**Vấn đề:** Dương tính giả: quét bí mật phát hiện các phi bí mật

- Trình quét bảo mật tìm kiếm các mẫu tương tự như khóa API, token và mật khẩu
- Nếu bạn đang commit mã ví dụ, test fixtures hoặc tài liệu với khóa giữ chỗ, bạn có thể thấy các dương tính giả
- Sử dụng `--skip-secret-scan` để bỏ qua quét nếu bạn chắc chắn các thay đổi an toàn
- Cân nhắc loại trừ các tệp ví dụ/test khỏi các commit, hoặc sử dụng các giữ chỗ được đánh dấu rõ ràng

**Vấn đề:** Quét bí mật không phát hiện các bí mật thực tế

- Trình quét sử dụng khớp mẫu và có thể không bắt được tất cả các loại bí mật
- Luôn xem lại các thay đổi đã staged của bạn với `git diff --staged` trước khi commit
- Cân nhắc sử dụng các công cụ bảo mật bổ sung như `git-secrets` hoặc `gitleaks` để bảo vệ toàn diện
- Báo cáo các mẫu bị bỏ lỡ dưới dạng vấn đề để giúp cải thiện phát hiện

**Vấn đề:** Cần vô hiệu hóa quét bí mật vĩnh viễn

- Đặt `GAC_SKIP_SECRET_SCAN=true` trong tệp `.gac.env` của bạn
- Sử dụng `gac config set GAC_SKIP_SECRET_SCAN true`
- Lưu ý: Chỉ vô hiệu hóa nếu bạn có các biện pháp bảo mật khác đã đặt

## 6. Vấn Đề Hooks Pre-commit và Lefthook

**Vấn đề:** Các hook pre-commit hoặc lefthook thất bại và chặn các commit

- Sử dụng `gac --no-verify` để bỏ qua tất cả các hook pre-commit và lefthook tạm thời
- Sửa các vấn đề cơ bản gây ra các hook thất bại
- Cân nhắc điều chỉnh cấu hình pre-commit hoặc lefthook của bạn nếu các hook quá nghiêm ngặt cho quy trình làm việc của bạn

**Vấn đề:** Các hook pre-commit hoặc lefthook mất quá nhiều thời gian hoặc can thiệp vào quy trình làm việc

- Sử dụng `gac --no-verify` để bỏ qua tất cả các hook pre-commit và lefthook tạm thời
- Cân nhắc cấu hình các hook pre-commit trong `.pre-commit-config.yaml` hoặc các hook lefthook trong `.lefthook.yml` để ít tích cực hơn cho quy trình làm việc của bạn
- Xem lại cấu hình hook của bạn để tối ưu hóa hiệu suất

## 7. Vấn Đề Quy Trình Phổ Biến {#common-workflow-issues}

**Vấn đề:** Không có thay đổi để commit / không có gì được staged

- gac yêu cầu các thay đổi đã staged để tạo thông điệp commit
- Sử dụng `git add <files>` để stage các thay đổi, hoặc sử dụng `gac -a` để tự động stage tất cả các thay đổi
- Kiểm tra `git status` để xem các tệp nào đã được sửa đổi
- Sử dụng `gac diff` để xem một chế độ xem được lọc của các thay đổi của bạn

**Vấn đề:** Thông điệp commit không như tôi mong đợi

- Sử dụng hệ thống phản hồi tương tác: gõ `r` để reroll, `e` để chỉnh sửa, hoặc cung cấp phản hồi ngôn ngữ tự nhiên
- Thêm ngữ cảnh với `-h "gợi ý của bạn"` để hướng dẫn LLM
- Sử dụng `-o` cho các thông điệp đơn giản hơn một dòng hoặc `-v` để có thêm thông điệp chi tiết
- Sử dụng `--show-prompt` để xem thông tin nào LLM đang nhận

**Vấn đề:** gac quá chậm

- Sử dụng `gac -y` để bỏ qua gợi ý xác nhận
- Sử dụng `gac -q` cho chế độ yên tĩnh với ít đầu ra hơn
- Cân nhắc sử dụng các mô hình nhanh hơn/rẻ hơn cho các commit thường xuyên
- Sử dụng `gac --no-verify` để bỏ qua các hook nếu chúng làm chậm bạn

**Vấn đề:** Không thể chỉnh sửa hoặc cung cấp phản hồi sau khi tạo thông điệp

- Tại gợi ý, gõ `e` để vào chế độ chỉnh sửa (hỗ trợ phím tắt vi/emacs)
- Gõ `r` để tạo lại mà không có phản hồi
- Hoặc chỉ cần gõ phản hồi của bạn trực tiếp (ví dụ, "làm nó ngắn hơn", "tập trung vào sửa lỗi")
- Nhấn Enter trên input trống để xem gợi ý lại

## 8. Gỡ Lỗi Chung

- Sử dụng `gac init` để đặt lại hoặc cập nhật cấu hình của bạn một cách tương tác
- Sử dụng `gac --log-level=debug` để có đầu ra gỡ lỗi chi tiết và logging
- Sử dụng `gac --show-prompt` để xem gợi ý nào đang được gửi đến LLM
- Sử dụng `gac --help` để xem tất cả các flag dòng lệnh có sẵn
- Sử dụng `gac config show` để xem tất cả các giá trị cấu hình hiện tại
- Kiểm tra log cho các thông điệp lỗi và stack traces
- Kiểm tra [README.md](../README.md) chính để biết tính năng, ví dụ và hướng dẫn bắt đầu nhanh

## Vẫn Còn Kẹt?

- Tìm kiếm các vấn đề hiện có hoặc mở một vấn đề mới trên [kho GitHub](https://github.com/cellwebb/gac)
- Bao gồm chi tiết về OS, phiên bản Python, phiên bản gac, nhà cung cấp và đầu ra lỗi của bạn
- Càng nhiều chi tiết bạn cung cấp, vấn đề của bạn có thể được giải quyết càng nhanh chóng

## Nơi để Nhận Trợ Giúp Thêm

- Đối với tính năng và ví dụ sử dụng, xem [README.md](../README.md) chính
- Đối với gợi ý hệ thống tùy chỉnh, xem [CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md)
- Đối với hướng dẫn đóng góp, xem [CONTRIBUTING.md](CONTRIBUTING.md)
- Đối với chi tiết giấy phép, xem [../LICENSE](../LICENSE)
