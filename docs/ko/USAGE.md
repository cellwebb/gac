# gac 명령줄 사용법

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | **한국어** | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

이 문서는 `gac` CLI 도구의 사용 가능한 모든 플래그와 옵션을 설명합니다.

## 목차

- [gac 명령줄 사용법](#gac-명령줄-사용법)
  - [목차](#목차)
  - [기본 사용법](#기본-사용법)
  - [핵심 워크플로우 플래그](#핵심-워크플로우-플래그)
  - [메시지 커스터마이징](#메시지-커스터마이징)
  - [출력 및 상세 수준](#출력-및-상세-수준)
  - [도움말 및 버전](#도움말-및-버전)
  - [예제 워크플로우](#예제-워크플로우)
  - [고급](#고급)
    - [Pre-commit 및 Lefthook Hooks 건너뛰기](#pre-commit-및-lefthook-hooks-건너뛰기)
  - [구성 노트](#구성-노트)
    - [고급 구성 옵션](#고급-구성-옵션)
    - [구성 하위 명령어](#구성-하위-명령어)
  - [도움말 얻기](#도움말-얻기)

## 기본 사용법

```sh
gac init
# 그런 다음 프롬프트를 따라 제공자, 모델 및 API 키를 대화형으로 구성하세요
gac
```

스테이징된 변경 사항에 대한 LLM 기반 커밋 메시지를 생성하고 확인을 요청합니다. 확인 프롬프트는 다음을 수락합니다:

- `y` 또는 `yes` - 커밋 진행
- `n` 또는 `no` - 커밋 취소
- `r` 또는 `reroll` - 동일한 컨텍스트로 커밋 메시지 재생성
- `e` 또는 `edit` - 풍부한 터미널 편집으로 커밋 메시지를 제자리 편집 (vi/emacs 키바인딩)
- 다른 텍스트 - 해당 텍스트를 피드백으로 재생성 (예: `make it shorter`, `focus on performance`)
- 빈 입력 (엔터만) - 프롬프트 다시 표시

---

## 핵심 워크플로우 플래그

| 플래그 / 옵션        | 단축 | 설명                                               |
| -------------------- | ---- | -------------------------------------------------- |
| `--add-all`          | `-a` | 커밋하기 전에 모든 변경 사항 스테이징              |
| `--group`            | `-g` | 스테이징된 변경 사항을 여러 논리적 커밋으로 그룹화 |
| `--push`             | `-p` | 커밋 후 원격으로 변경 사항 푸시                    |
| `--yes`              | `-y` | 프롬프트 없이 자동으로 커밋 확인                   |
| `--dry-run`          |      | 변경 없이 어떤 일이 발생할지 표시                  |
| `--no-verify`        |      | 커밋 시 pre-commit 및 lefthook hooks 건너뛰기      |
| `--skip-secret-scan` |      | 스테이징된 변경 사항의 비밀 검사 건너뛰기          |

**참고:** 먼저 모든 변경 사항을 스테이징한 다음 커밋으로 그룹화하려면 `-a`와 `-g`를 결합하세요 (즉, `-ag`).

**참고:** `--group`을 사용할 때, 최대 출력 토큰 제한은 커밋되는 파일 수에 따라 자동으로 조정됩니다 (1-9개 파일에 2배, 10-19개 파일에 3배, 20-29개 파일에 4배, 30개 이상 파일에 5배). 이는 LLM이 대량의 변경셋에도 잘림 없이 모든 그룹화된 커밋을 생성할 수 있도록 충분한 토큰을 확보합니다.

## 메시지 커스터마이징

| 플래그 / 옵션       | 단축 | 설명                                                         |
| ------------------- | ---- | ------------------------------------------------------------ |
| `--one-liner`       | `-o` | 한 줄 커밋 메시지 생성                                       |
| `--verbose`         | `-v` | 동기, 아키텍처 및 영향을 포함한 상세한 커밋 메시지 생성      |
| `--hint <text>`     | `-h` | LLM를 안내하기 위한 힌트 추가                                |
| `--model <model>`   | `-m` | 이 커밋에 사용할 모델 지정                                   |
| `--language <lang>` | `-l` | 언어 재정의 (이름 또는 코드: 'Spanish', 'es', 'zh-CN', 'ja') |
| `--scope`           | `-s` | 커밋에 적절한 스코프 추론                                    |

**참고:** 확인 프롬프트에 피드백을 타이핑하여 대화형으로 피드백을 제공할 수 있습니다 - 'r'로 접두사를 붙일 필요가 없습니다. 간단한 재롤링을 위해 `r`을 타이핑하고, vi/emacs 키바인딩으로 제자리 편집하려면 `e`를 타이핑하거나, `make it shorter`와 같이 피드백을 직접 타이핑하세요.

## 출력 및 상세 수준

| 플래그 / 옵션         | 단축 | 설명                                         |
| --------------------- | ---- | -------------------------------------------- |
| `--quiet`             | `-q` | 에러를 제외한 모든 출력 억제                 |
| `--log-level <level>` |      | 로그 레벨 설정 (debug, info, warning, error) |
| `--show-prompt`       |      | 커밋 메시지 생성에 사용된 LLM 프롬프트 출력  |

## 도움말 및 버전

| 플래그 / 옵션 | 단축 | 설명                       |
| ------------- | ---- | -------------------------- |
| `--version`   |      | gac 버전 표시 및 종료      |
| `--help`      |      | 도움말 메시지 표시 및 종료 |

---

## 예제 워크플로우

- **모든 변경 사항 스테이징 및 커밋:**

  ```sh
  gac -a
  ```

- **한 단계로 커밋 및 푸시:**

  ```sh
  gac -ap
  ```

- **한 줄 커밋 메시지 생성:**

  ```sh
  gac -o
  ```

- **구조화된 섹션으로 상세한 커밋 메시지 생성:**

  ```sh
  gac -v
  ```

- **LLM을 위한 힌트 추가:**

  ```sh
  gac -h "Refactor authentication logic"
  ```

- **커밋에 대한 스코프 추론:**

  ```sh
  gac -s
  ```

- **스테이징된 변경 사항을 논리적 커밋으로 그룹화:**

  ```sh
  gac -g
  # 이미 스테이징한 파일만 그룹화
  ```

- **모든 변경 사항 그룹화 (스테이징 + 스테이징되지 않음) 및 자동 확인:**

  ```sh
  gac -agy
  # 모든 것을 스테이징하고, 그룹화하며, 자동 확인
  ```

- **이 커밋에만 특정 모델 사용:**

  ```sh
  gac -m anthropic:claude-haiku-4-5
  ```

- **특정 언어로 커밋 메시지 생성:**

  ```sh
  # 언어 코드 사용 (더 짧게)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # 전체 이름 사용
  gac -l "Simplified Chinese"
  gac -l Japanese
  gac -l Spanish
  ```

- **드라이 런 (어떤 일이 발생할지 확인):**

  ```sh
  gac --dry-run
  ```

## 고급

- 더 강력한 워크플로우를 위해 플래그 결합 (예: `gac -ayp`로 스테이징, 자동 확인 및 푸시)
- LLM에 보낸 프롬프트를 디버그하거나 검토하려면 `--show-prompt` 사용
- `--log-level` 또는 `--quiet`로 상세 수준 조정

### Pre-commit 및 Lefthook Hooks 건너뛰기

`--no-verify` 플래그를 사용하면 프로젝트에 구성된 모든 pre-commit 또는 lefthook hooks를 건너뛸 수 있습니다:

```sh
gac --no-verify  # 모든 pre-commit 및 lefthook hooks 건너뛰기
```

**다음 경우에 `--no-verify` 사용:**

- Pre-commit 또는 lefthook hooks가 일시적으로 실패하는 경우
- 시간이 많이 걸리는 hooks로 작업하는 경우
- 아직 모든 검사를 통과하지 않는 진행 중인 작업을 커밋하는 경우

**참고:** 이 hooks는 코드 품질 표준을 유지하므로 주의해서 사용하세요.

### 보안 검사

gac에는 커밋하기 전에 스테이징된 변경 사항에서 잠재적인 비밀과 API 키를 자동으로 감지하는 내장 보안 검사가 포함되어 있습니다. 이는 민감한 정보를 실수로 커밋하는 것을 방지하는 데 도움이 됩니다.

**보안 검사 건너뛰기:**

```sh
gac --skip-secret-scan  # 이 커밋에 대한 보안 검사 건너뛰기
```

**영구적으로 비활성화:** `.gac.env` 파일에서 `GAC_SKIP_SECRET_SCAN=true` 설정.

**건너뛰는 경우:**

- 자리 표시자 키가 있는 예제 코드 커밋
- 더미 자격 증명이 포함된 테스트 픽스처로 작업
- 변경 사항이 안전하다고 확인한 경우

**참고:** 스캐너는 패턴 일치를 사용하여 일반적인 비밀 형식을 감지합니다. 커밋하기 전에는 항상 스테이징된 변경 사항을 검토하세요.

## 구성 노트

- gac를 설정하는 권장 방법은 `gac init`를 실행하고 대화형 프롬프트를 따르는 것입니다.
- 이미 언어가 구성되었고 프로바이더나 모델만 전환해야 하나요? 언어 질문 없이 설정을 반복하려면 `gac model`을 실행하세요.
- **Claude Code를 사용하시나요?** OAuth 인증 지침은 [Claude Code 설정 가이드](CLAUDE_CODE.md)를 참조하세요.
- gac는 다음 우선순위 순서로 구성을 로드합니다:
  1. CLI 플래그
  2. 환경 변수
  3. 프로젝트 레벨 `.gac.env`
  4. 사용자 레벨 `~/.gac.env`

### 고급 구성 옵션

선택적 환경 변수로 gac의 동작을 커스터마이즈할 수 있습니다:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - 커밋 메시지에 스코프를 자동으로 추론하고 포함 (예: `feat(auth):` 대신 `feat:`)
- `GAC_VERBOSE=true` - 동기, 아키텍처 및 영향 섹션으로 상세한 커밋 메시지 생성
- `GAC_TEMPERATURE=0.7` - LLM 창의성 제어 (0.0-1.0, 낮을수록 더 집중됨)
- `GAC_MAX_OUTPUT_TOKENS=4096` - 생성된 메시지용 최대 토큰 (`--group` 사용 시 파일 수에 따라 자동으로 2-5배 조정됨; 더 높거나 낮게 설정하려면 재정의)
- `GAC_WARNING_LIMIT_TOKENS=4096` - 프롬프트가 이 토큰 수를 초과하면 경고
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - 커밋 메시지 생성을 위해 커스텀 시스템 프롬프트 사용
- `GAC_LANGUAGE=Spanish` - 특정 언어로 커밋 메시지 생성 (예: Spanish, French, Japanese, German). 전체 이름 또는 ISO 코드 지원 (es, fr, ja, de, zh-CN). 대화형 선택을 위해 `gac language` 사용
- `GAC_TRANSLATE_PREFIXES=true` - 전통적인 커밋 접두사 (feat, fix 등)를 대상 언어로 번역 (기본값: false, 접두사를 영어로 유지)
- `GAC_SKIP_SECRET_SCAN=true` - 스테이징된 변경 사항의 비밀에 대한 자동 보안 스캔 비활성화 (주의해서 사용)

전체 구성 템플릿은 `.gac.env.example`을 참조하세요.

커스텀 시스템 프롬프트 생성에 대한 상세한 안내는 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)를 참조하세요.

### 구성 하위 명령어

다음 하위 명령을 사용할 수 있습니다:

- `gac init` — 공급자, 모델, 언어 구성을 위한 대화형 설정 마법사
- `gac model` — 언어 프롬프트 없는 공급자/모델/API 키 설정 (빠른 전환에 이상적)
- `gac auth` — Claude Code OAuth 토큰 인증 또는 재인증 (토큰 만료 시 유용)
- `gac config show` — 현재 구성 표시
- `gac config set KEY VALUE` — `$HOME/.gac.env`에서 구성 키 설정
- `gac config get KEY` — 구성 값 가져오기
- `gac config unset KEY` — `$HOME/.gac.env`에서 구성 키 제거
- `gac language` (또는 `gac lang`) — 커밋 메시지를 위한 대화형 언어 선택기 (GAC_LANGUAGE 설정)
- `gac diff` — 스테이징된/스테이징되지 않은 변경, 색상, 자르기 옵션으로 필터링된 git diff 표시

## 도움말 얻기

- 커스텀 시스템 프롬프트는 [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md) 참조
- 문제 해결 및 고급 팁은 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) 참조
- 설치 및 구성은 [README.md#installation-and-configuration](README.md#installation-and-configuration) 참조
- 기여하려면 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) 참조
- 라이선스 정보: [LICENSE](LICENSE)
