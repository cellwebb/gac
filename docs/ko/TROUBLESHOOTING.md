# gac 문제 해결

[English](../en/TROUBLESHOOTING.md) | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | **한국어** | [हिन्दी](../hi/TROUBLESHOOTING.md) | [Tiếng Việt](../vi/TROUBLESHOOTING.md) | [Français](../fr/TROUBLESHOOTING.md) | [Русский](../ru/TROUBLESHOOTING.md) | [Español](../es/TROUBLESHOOTING.md) | [Português](../pt/TROUBLESHOOTING.md) | [Deutsch](../de/TROUBLESHOOTING.md) | [Nederlands](../nl/TROUBLESHOOTING.md)

이 가이드는 gac의 설치, 구성 및 실행에 대한 일반적인 문제와 해결책을 다룹니다.

## 목차

- [gac 문제 해결](#gac-문제-해결)
  - [목차](#목차)
  - [1. 설치 문제](#1-설치-문제)
  - [2. 구성 문제](#2-구성-문제)
  - [3. 프로바이더/API 에러](#3-프로바이더api-에러)
  - [4. 커밋 그룹화 문제](#4-커밋-그룹화-문제)
  - [5. 보안 및 비밀 감지](#5-보안-및-비밀-감지)
  - [6. Pre-commit 및 Lefthook Hook 문제](#6-pre-commit-및-lefthook-hook-문제)
  - [7. 일반적인 워크플로우 문제](#7-일반적인-워크플로우-문제)
  - [8. 일반적인 디버깅](#8-일반적인-디버깅)
  - [여전히 막혀있나요?](#여전히-막혀있나요)
  - [추가 도움받을 곳](#추가-도움받을-곳)

## 1. 설치 문제

**문제:** 설치 후 `gac` 명령을 찾을 수 없음

- `uv tool install gac` 또는 `uvx gac`로 설치했는지 확인
- `uv tool install`을 사용한 경우, `uv tool list`로 설치 확인
- `uv`가 설치되어 있고 `$PATH`에 있는지 확인
- 설치 후 터미널 재시작

**문제:** 권한 거부 또는 파일을 쓸 수 없음

- 디렉토리 권한 확인
- 적절한 권한으로 실행하거나 디렉토리 소유권 변경 시도

## 2. 구성 문제

**문제:** gac가 API 키나 모델을 찾을 수 없음

- 새로운 경우, `gac init`를 실행하여 프로바이더, 모델 및 API 키를 대화형으로 설정
- `.gac.env` 또는 환경 변수가 올바르게 설정되었는지 확인
- `gac --log-level=debug`를 실행하여 어떤 구성 파일이 로드되는지 확인하고 구성 문제를 디버그
- 변수명의 오타 확인 (예: `GAC_GROQ_API_KEY`)

**문제:** 사용자 레벨 `$HOME/.gac.env` 변경 사항이 적용되지 않음

- OS에 맞는 올바른 파일을 편집하고 있는지 확인:
  - macOS/Linux: `$HOME/.gac.env` (보통 `/Users/<your-username>/.gac.env` 또는 `/home/<your-username>/.gac.env`)
  - Windows: `$HOME/.gac.env` (보통 `C:\Users\<your-username>\.gac.env` 또는 `%USERPROFILE%` 사용)
- `gac --log-level=debug`를 실행하여 사용자 레벨 구성이 로드되는지 확인
- 터미널을 재시작하거나 셸을 다시 실행하여 환경 변수 다시 로드
- 여전히 작동하지 않으면 오타와 파일 권한 확인

**문제:** 프로젝트 레벨 `.gac.env` 변경 사항이 적용되지 않음

- 프로젝트 루트 디렉토리 (`.git` 폴더 옆)에 `.gac.env` 파일이 있는지 확인
- `gac --log-level=debug`를 실행하여 프로젝트 레벨 구성이 로드되는지 확인
- `.gac.env`를 편집한 경우, 터미널을 재시작하거나 셸을 다시 실행하여 환경 변수 다시 로드
- 여전히 작동하지 않으면 오타와 파일 권한 확인

**문제:** 커밋 메시지용 언어를 설정하거나 변경할 수 없음

- `gac language` (또는 `gac lang`)를 실행하여 25개 이상의 지원되는 언어에서 대화형으로 선택
- `-l <language>` 플래그를 사용하여 단일 커밋에 대한 언어 재정의 (예: `gac -l zh-CN`, `gac -l Spanish`)
- `gac config show`로 현재 언어 설정 확인
- 언어 설정은 `.gac.env` 파일의 `GAC_LANGUAGE`에 저장됨

## 3. 프로바이더/API 에러

**문제:** 인증 또는 API 에러

- 선택한 모델에 대해 올바른 API 키가 설정되었는지 확인 (예: `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- API 키와 프로바이더 계정 상태를 다시 확인
- Ollama와 LM Studio의 경우, API URL이 로컬 인스턴스와 일치하는지 확인. 인증을 활성화한 경우에만 API 키가 필요합니다.

**문제:** 모델을 사용할 수 없거나 지원되지 않음

- Streamlake는 모델 이름 대신 추론 엔드포인트 ID를 사용합니다. 콘솔에서 얻은 엔드포인트 ID를 제공해야 합니다.
- 모델 이름이 올바르고 프로바이더가 지원하는지 확인
- 사용 가능한 모델을 위해 프로바이더 문서 확인

## 4. 커밋 그룹화 문제

**문제:** `--group` 플래그가 예상대로 작동하지 않음

- `--group` 플래그는 자동으로 스테이징된 변경 사항을 분석하고 여러 논리적 커밋을 생성할 수 있습니다
- `--group`을 사용하더라도 LLM은 스테이징된 변경 세트에 단일 커밋이 합리적이라고 결정할 수 있습니다
- 이는 의도된 동작입니다 - LLM은 수량이 아닌 논리적 관계를 기반으로 변경 사항을 그룹화합니다
- 최상의 결과를 위해 여러 관련 없는 변경 사항을 스테이징했는지 확인 (예: 버그 수정 + 기능 추가)
- `gac --show-prompt`를 사용하여 LLM이 보고 있는 것을 디버그

**문제:** 커밋이 잘못 그룹화되거나 예상할 때 그룹화되지 않음

- 그룹화는 LLM의 변경 사항 분석에 의해 결정됩니다
- LLM은 변경 사항이 논리적으로 관련되어 있다고 판단하면 단일 커밋을 생성할 수 있습니다
- `-h "hint"`로 힌트를 추가하여 그룹화 로직을 안내해보세요 (예: `-h "separate bug fix from refactoring"`)
- 확인하기 전에 생성된 그룹 검토
- 그룹화가 사용 사례에 맞지 않으면 대신 변경 사항을 별도로 커밋

## 5. 보안 및 비밀 감지

**문제:** 오탐: 비밀 스캔이 비밀이 아닌 것을 감지

- 보안 스캐너는 API 키, 토큰 및 비밀번호와 유사한 패턴을 찾습니다
- 예제 코드, 테스트 픽스처 또는 자리 표시자 키가 있는 문서를 커밋하는 경우 오탐을 볼 수 있습니다
- 변경 사항이 안전하다고 확신하면 `--skip-secret-scan`을 사용하여 스캔을 우회
- 커밋에서 테스트/예제 파일을 제외하거나 명확하게 표시된 자리 표시자 사용 고려

**문제:** 비밀 스캔이 실제 비밀을 감지하지 못함

- 스캐너는 패턴 일치를 사용하며 모든 비밀 타입을 포착하지 못할 수 있습니다
- 커밋하기 전에 항상 `git diff --staged`로 스테이징된 변경 사항 검토
- 포괄적인 보호를 위해 `git-secrets`나 `gitleaks`와 같은 추가 보안 도구 사용 고려
- 감지를 개선하기 위해 놓친 패턴을 이슈로 보고

**문제:** 비밀 스캔을 영구적으로 비활성화해야 함

- `.gac.env` 파일에서 `GAC_SKIP_SECRET_SCAN=true` 설정
- `gac config set GAC_SKIP_SECRET_SCAN true` 사용
- 참고: 다른 보안 조치가 있는 경우에만 비활성화

## 6. Pre-commit 및 Lefthook Hook 문제

**문제:** Pre-commit 또는 lefthook hooks가 실패하고 커밋을 차단

- `gac --no-verify`를 사용하여 모든 pre-commit 및 lefthook hooks를 일시적으로 건너뛰기
- hooks가 실패하게 만드는 근본적인 문제 해결
- hooks가 너무 엄격한 경우 pre-commit 또는 lefthook 구성 조정 고려

**문제:** Pre-commit 또는 lefthook hooks가 너무 오래 걸리거나 워크플로우를 방해

- `gac --no-verify`를 사용하여 모든 pre-commit 및 lefthook hooks를 일시적으로 건너뛰기
- `.pre-commit-config.yaml`의 pre-commit hooks 또는 `.lefthook.yml`의 lefthook hooks를 워크플로우에 덜 공격적으로 구성 고려
- 성능 최적화를 위해 hook 구성 검토

## 7. 일반적인 워크플로우 문제

**문제:** 커밋할 변경 사항 없음 / 스테이징된 것이 없음

- gac는 커밋 메시지를 생성하기 위해 스테이징된 변경 사항이 필요합니다
- `git add <files>`를 사용하여 변경 사항을 스테이징하거나, `gac -a`를 사용하여 모든 변경 사항을 자동으로 스테이징
- 수정된 파일을 보려면 `git status` 확인
- 변경 사항의 필터링된 뷰를 보려면 `gac diff` 사용

**문제:** 커밋 메시지가 예상과 다름

- 대화형 피드백 시스템 사용: `r`을 타이핑하여 재롤링, `e`를 타이핑하여 편집, 또는 자연어 피드백 제공
- `-h "your hint"`로 컨텍스트 추가하여 LLM 안내
- 더 간단한 한 줄 메시지에는 `-o` 사용, 더 상세한 메시지에는 `-v` 사용
- `--show-prompt`를 사용하여 LLM이 받는 정보 확인

**문제:** gac가 너무 느림

- `gac -y`를 사용하여 확인 프롬프트 건너뛰기
- `gac -q`를 사용하여 출력이 적은 조용한 모드
- 일상적인 커밋에는 더 빠르고 저렴한 모델 사용 고려
- hooks가 속도를 늦추는 경우 `gac --no-verify`로 hooks 건너뛰기

**문제:** 메시지 생성 후 편집하거나 피드백을 제공할 수 없음

- 프롬프트에서 `e`를 타이핑하여 편집 모드 진입 (vi/emacs 키바인딩 지원)
- 피드백 없이 재생성하려면 `r` 타이핑
- 또는 피드백을 직접 타이핑 (예: "make it shorter", "focus on the bug fix")
- 빈 입력에서 엔터를 눌러 프롬프트 다시 표시

## 8. 일반적인 디버깅

- 구성을 재설정하거나 업데이트하려면 `gac init` 사용
- 상세한 디버그 출력과 로깅을 위해 `gac --log-level=debug` 사용
- LLM에 보내진 프롬프트를 보려면 `gac --show-prompt` 사용
- 사용 가능한 모든 명령줄 플래그를 보려면 `gac --help` 사용
- 모든 현재 구성 값을 보려면 `gac config show` 사용
- 에러 메시지와 스택 트레이스를 위해 로그 확인
- 기능, 예제 및 빠른 시작 지침은 메인 [README.md](../README.md) 확인

## 여전히 막혀있나요?

- [GitHub 저장소](https://github.com/cellwebb/gac)에서 기존 이슈 검색 또는 새로운 이슈 열기
- OS, Python 버전, gac 버전, 프로바이더 및 에러 출력에 대한 세부 정보 포함
- 제공하는 세부 정보가 많을수록 이슈를 더 빨리 해결할 수 있습니다

## 추가 도움받을 곳

- 기능 및 사용 예제는 메인 [README.md](../README.md) 참조
- 커스텀 시스템 프롬프트는 [CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md) 참조
- 기여 가이드라인은 [CONTRIBUTING.md](../CONTRIBUTING.md) 참조
- 라이선스 정보는 [../LICENSE](../LICENSE) 참조
