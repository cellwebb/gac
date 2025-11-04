# gac에 기여하기

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | **한국어** | [हिन्दी](../hi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md)

이 프로젝트에 기여해 주셔서 관심을 가져주셔서 감사합니다! 여러분의 도움은 감사합니다. 모든 분들을 위해 과정을 원활하게 만들기 위해 다음 가이드라인을 따라주세요.

## 목차

- [gac에 기여하기](#gac에-기여하기)
  - [목차](#목차)
  - [개발 환경 설정](#개발-환경-설정)
    - [빠른 설정](#빠른-설정)
    - [대체 설정 (단계별 설정 선호 시)](#대체-설정-단계별-설정-선호-시)
    - [사용 가능한 명령어](#사용-가능한-명령어)
  - [버전 업그레이드](#버전-업그레이드)
    - [버전을 업그레이드하는 방법](#버전을-업그레이드하는-방법)
    - [릴리즈 프로세스](#릴리즈-프로세스)
    - [bump-my-version 사용 (선택사항)](#bump-my-version-사용-선택사항)
  - [새로운 AI 프로바이더 추가](#새로운-ai-프로바이더-추가)
    - [새로운 프로바이더 추가 체크리스트](#새로운-프로바이더-추가-체크리스트)
    - [예제 구현](#예제-구현)
    - [핵심 포인트](#핵심-포인트)
  - [코딩 표준](#코딩-표준)
  - [Git Hooks (Lefthook)](#git-hooks-lefthook)
    - [설정](#설정)
    - [Git Hooks 건너뛰기](#git-hooks-건너뛰기)
  - [테스트 가이드라인](#테스트-가이드라인)
    - [테스트 실행](#테스트-실행)
      - [프로바이더 통합 테스트](#프로바이더-통합-테스트)
  - [행동 강령](#행동-강령)
  - [라이선스](#라이선스)
  - [도움받을 곳](#도움받을-곳)

## 개발 환경 설정

이 프로젝트는 의존성 관리를 위해 `uv`를 사용하며 공통 개발 작업을 위해 Makefile을 제공합니다:

### 빠른 설정

```bash
# Lefthook hooks를 포함한 모든 것을 설정하는 하나의 명령어
make dev
```

이 명령어는 다음을 수행합니다:

- 개발 의존성 설치
- git hooks 설치
- 모든 파일에서 Lefthook hooks를 실행하여 기존 문제 수정

### 대체 설정 (단계별 설정 선호 시)

```bash
# 가상 환경 생성 및 의존성 설치
make setup

# 개발 의존성 설치
make dev

# Lefthook hooks 설치
brew install lefthook  # 또는 아래 문서에서 대안 확인
lefthook install
lefthook run pre-commit --all
```

### 사용 가능한 명령어

- `make setup` - 가상 환경 생성 및 모든 의존성 설치
- `make dev` - **완전한 개발 설정** - Lefthook hooks 포함
- `make test` - 기본 테스트 실행 (통합 테스트 제외)
- `make test-integration` - 통합 테스트만 실행 (API 키 필요)
- `make test-all` - 모든 테스트 실행
- `make test-cov` - 커버리지 리포트와 함께 테스트 실행
- `make lint` - 코드 품질 확인 (ruff, prettier, markdownlint)
- `make format` - 코드 포맷팅 문제 자동 수정

## 버전 업그레이드

**중요**: PR에는 릴리즈되어야 할 변경 사항이 포함될 때 `src/gac/__version__.py`의 버전 업그레이드가 포함되어야 합니다.

### 버전을 업그레이드하는 방법

1. `src/gac/__version__.py`를 편집하고 버전 번호를 증가시킵니다
2. [Semantic Versioning](https://semver.org/)을 따르세요:
   - **Patch** (1.6.X): 버그 수정, 작은 개선사항
   - **Minor** (1.X.0): 새로운 기능, 호환성 있는 변경사항 (예: 새로운 프로바이더 추가)
   - **Major** (X.0.0): 호환성 깨지는 변경사항

### 릴리즈 프로세스

릴리즈는 버전 태그를 푸시하여 트리거됩니다:

1. 버전 업그레이드가 있는 PR들을 main에 병합
2. 태그 생성: `git tag v1.6.1`
3. 태그 푸시: `git push origin v1.6.1`
4. GitHub Actions가 자동으로 PyPI에 게시

예시:

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # 1.6.0에서 업그레이드됨
```

### bump-my-version 사용 (선택사항)

`bump-my-version`이 설치되어 있다면 로컬에서 사용할 수 있습니다:

```bash
# 버그 수정용:
bump-my-version bump patch

# 새로운 기능용:
bump-my-version bump minor

# 호환성 깨지는 변경용:
bump-my-version bump major
```

## 새로운 AI 프로바이더 추가

새로운 AI 프로바이더를 추가할 때, 코드베이스 전체의 여러 파일을 업데이트해야 합니다. 이 포괄적인 체크리스트를 따르세요:

### 새로운 프로바이더 추가 체크리스트

- [ ] **1. 프로바이더 구현 생성** (`src/gac/providers/<provider_name>.py`)

  - 프로바이더 이름으로 새 파일 생성 (예: `minimax.py`)
  - `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str` 구현
  - 프로바이더가 지원하는 경우 OpenAI 호환 형식 사용
  - 환경 변수 `<PROVIDER>_API_KEY`에서 API 키 처리
  - `AIError` 타입으로 적절한 에러 처리 포함:
    - `AIError.authentication_error()` 인증 문제용
    - `AIError.rate_limit_error()` 속도 제한용 (HTTP 429)
    - `AIError.timeout_error()` 타임아웃용
    - `AIError.model_error()` 모델 에러 및 비어있는/null 컨텐츠용
  - API 엔드포인트 URL 설정
  - HTTP 요청에 120초 타임아웃 사용

- [ ] **2. 패키지에 프로바이더 등록** (`src/gac/providers/__init__.py`)

  - 임포트 추가: `from .<provider> import call_<provider>_api`
  - `__all__` 리스트에 추가: `"call_<provider>_api"`

- [ ] **3. AI 모듈에 프로바이더 등록** (`src/gac/ai.py`)

  - `from gac.providers import (...)` 섹션에 임포트 추가
  - `provider_funcs` 딕셔너리에 추가: `"provider-name": call_<provider>_api`

- [ ] **4. 지원되는 프로바이더 리스트에 추가** (`src/gac/ai_utils.py`)

  - `generate_with_retries()`의 `supported_providers` 리스트에 `"provider-name"` 추가
  - 리스트를 알파벳순으로 정렬된 상태로 유지

- [ ] **5. 대화형 설정에 추가** (`src/gac/init_cli.py`)

  - `providers` 리스트에 튜플 추가: `("Provider Name", "default-model-name")`
  - 리스트를 알파벳순으로 정렬된 상태로 유지
  - 필요한 경우 특별 처리 추가 (Ollama/LM Studio와 같은 로컬 프로바이더용)

- [ ] **6. 예제 구성 업데이트** (`.gac.env.example`)

  - 형식으로 예제 모델 구성 추가: `# GAC_MODEL=provider:model-name`
  - API 키 항목 추가: `# <PROVIDER>_API_KEY=your_key_here`
  - 항목을 알파벳순으로 정렬된 상태로 유지
  - 해당하는 경우 선택적 키에 대한 주석 추가

- [ ] **7. 문서 업데이트** (`README.md` 및 `README.zh-CN.md`)

  - 영어 및 중국어 README 모두의 "Supported Providers" 섹션에 프로바이더 이름 추가
  - 글 머리 기호 내에서 알파벳순으로 정렬된 상태로 유지

- [ ] **8. 포괄적인 테스트 생성** (`tests/providers/test_<provider>.py`)

  - 명명 규칙을 따르는 테스트 파일 생성
  - 다음 테스트 클래스 포함:
    - `Test<Provider>Imports` - 모듈 및 함수 임포트 테스트
    - `Test<Provider>APIKeyValidation` - 누락된 API 키 에러 테스트
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - 9개 표준 테스트를 위해 `BaseProviderTest` 상속
    - `Test<Provider>EdgeCases` - null 컨텐츠 및 기타 엣지 케이스 테스트
    - `Test<Provider>Integration` - 실제 API 호출 테스트 (`@pytest.mark.integration`으로 마크)
  - 모의 테스트 클래스에서 필수 속성 구현:
    - `provider_name` - 프로바이더 이름 (소문자)
    - `provider_module` - 전체 모듈 경로
    - `api_function` - API 함수 참조
    - `api_key_env_var` - API 키용 환경 변수 이름 (또는 로컬 프로바이더용 None)
    - `model_name` - 테스트용 기본 모델 이름
    - `success_response` - 모의 성공적인 API 응답
    - `empty_content_response` - 모의 비어있는 컨텐츠 응답

- [ ] **9. 버전 업그레이드** (`src/gac/__version__.py`)
  - **마이너** 버전을 증가시키세요 (예: 1.10.2 → 1.11.0)
  - 프로바이더 추가는 새로운 기능이며 마이너 버전 업그레이드가 필요합니다

### 예제 구현

참고용으로 MiniMax 프로바이더 구현을 확인하세요:

- 프로바이더: `src/gac/providers/minimax.py`
- 테스트: `tests/providers/test_minimax.py`

### 핵심 포인트

1. **에러 처리**: 다른 에러 시나리오에 대해 항상 적절한 `AIError` 타입 사용
2. **Null/비어있는 컨텐츠**: 응답에서 `None` 및 비어있는 문자열 컨텐츠 모두 확인
3. **테스팅**: `BaseProviderTest` 클래스는 모든 프로바이더가 상속해야 하는 9개 표준 테스트 제공
4. **알파벳순**: 유지보수성을 위해 프로바이더 리스트를 알파벳순으로 정렬된 상태로 유지
5. **API 키 명명**: `<PROVIDER>_API_KEY` 형식 사용 (모두 대문자, 공백은 밑줄)
6. **프로바이더 이름 형식**: 여러 단어 이름에는 소문자와 하이픈 사용 (예: "lm-studio")
7. **버전 업그레이드**: 프로바이더 추가는 **마이너** 버전 업그레이드 필요 (새로운 기능)

## 코딩 표준

- Python 3.10+ 타겟 (3.10, 3.11, 3.12, 3.13, 3.14)
- 모든 함수 파라미터 및 반환값에 타입 힌트 사용
- 코드를 깨끗하고, 컴팩트하고, 읽기 쉽게 유지
- 불필요한 복잡성 피하기
- print 문 대신 로깅 사용
- 포맷팅은 `ruff`로 처리 (린트, 포맷팅, 임포트 정렬을 한 도구로; 최대 라인 길이: 120)
- `pytest`로 최소한의 효과적인 테스트 작성

## Git Hooks (Lefthook)

이 프로젝트는 코드 품질 검사를 빠르고 일관되게 유지하기 위해 [Lefthook](https://github.com/evilmartians/lefthook)를 사용합니다. 구성된 hooks는 이전 pre-commit 설정을 미러링합니다:

- `ruff` - Python 린트 및 포맷팅 (black, isort, flake8 대체)
- `markdownlint-cli2` - Markdown 린트
- `prettier` - 파일 포맷팅 (markdown, yaml, json)
- `check-upstream` - 업스트림 변경 확인을 위한 커스텀 hook

### 설정

**권장 접근법:**

```bash
make dev
```

**수동 설정 (단계별 설정 선호 시):**

1. Lefthook 설치 (설정에 맞는 옵션 선택):

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # 또는
   cargo install lefthook         # Rust toolchain
   # 또는
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. git hooks 설치:

   ```sh
   lefthook install
   ```

3. (선택사항) 모든 파일에 대해 실행:

   ```sh
   lefthook run pre-commit --all
   ```

이제 hooks가 각 커밋마다 자동으로 실행됩니다. 검사가 실패하면 커밋하기 전에 문제를 수정해야 합니다.

### Git Hooks 건너뛰기

Lefthook 검사를 일시적으로 건너뛰어야 하는 경우, `--no-verify` 플래그 사용:

```sh
git commit --no-verify -m "Your commit message"
```

참고: 이것은 중요한 코드 품질 검사를 우회하므로 절대적으로 필요할 때만 사용해야 합니다.

## 테스트 가이드라인

프로젝트는 테스트를 위해 pytest를 사용합니다. 새로운 기능을 추가하거나 버그를 수정할 때, 변경 사항을 포함하는 테스트를 포함해주세요.

`scripts/` 디렉토리에는 pytest로 쉽게 테스트할 수 없는 기능에 대한 테스트 스크립트가 포함되어 있습니다. 복잡한 시나리오나 표준 pytest 프레임워크로 구현하기 어려운 통합 테스트를 여기에 추가해 자유롭게 추가하세요.

### 테스트 실행

```sh
# 기본 테스트 실행 (실제 API 호출과 함께 통합 테스트 제외)
make test

# 프로바이더 통합 테스트만 실행 (API 키 필요)
make test-integration

# 프로바이더 통합 테스트를 포함한 모든 테스트 실행
make test-all

# 커버리지와 함께 테스트 실행
make test-cov

# 특정 테스트 파일 실행
uv run -- pytest tests/test_prompt.py

# 특정 테스트 실행
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### 프로바이더 통합 테스트

프로바이더 통합 테스트는 프로바이더 구현이 실제 API와 올바르게 작동하는지 확인하기 위해 실제 API 호출을 수행합니다. 이 테스트들은 `@pytest.mark.integration`으로 마크되어 있으며 기본적으로 건너뜁니다:

- 정기 개발 중 API 크레디트 소비 방지
- API 키가 구성되지 않은 경우 테스트 실패 방지
- 빠른 반복을 위해 테스트 실행 속도 유지

프로바이더 통합 테스트 실행:

1. **테스트할 프로바이더의 API 키 설정**:

   ```sh
   export ANTHROPIC_API_KEY="your-key"
   export CEREBRAS_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export GROQ_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export OPENROUTER_API_KEY="your-key"
   export STREAMLAKE_API_KEY="your-key"
   export ZAI_API_KEY="your-key"
   # LM Studio와 Ollama는 로컬 인스턴스 실행 필요
   # LM Studio와 Ollama용 API 키는 배포에서 인증을 강제하지 않는 경우 선택사항
   ```

2. **프로바이더 테스트 실행**:

   ```sh
   make test-integration
   ```

테스트는 API 키가 구성되지 않은 프로바이더를 건너뜁니다. 이 테스트들은 API 변경 사항을 조기에 감지하고 프로바이더 API와의 호환성을 보장하는 데 도움이 됩니다.

## 행동 강령

존중하고 건설적이어주세요. 괴롭힘이나 악의적인 행동은 용납되지 않습니다.

## 라이선스

기여함으로써, 여러분의 기여는 프로젝트와 동일한 라이선스로 라이선스될 것에 동의합니다.

---

## 도움받을 곳

- 문제 해결을 위해 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 참조
- 사용법 및 CLI 옵션을 위해 [USAGE.md](USAGE.md) 참조
- 라이선스 세부사항을 위해 [../../LICENSE](../../LICENSE) 참조

gac 개선을 도와주셔서 감사합니다!
