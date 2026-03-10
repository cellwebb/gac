# GAC를 MCP 서버로 사용하기

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | **한국어** | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC는 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 서버로 실행할 수 있으며, AI 에이전트와 에디터가 셸 명령 대신 구조화된 도구 호출을 통해 커밋을 생성할 수 있습니다.

## 목차

- [GAC를 MCP 서버로 사용하기](#gac를-mcp-서버로-사용하기)
  - [목차](#목차)
  - [MCP란?](#mcp란)
  - [이점](#이점)
  - [설정](#설정)
    - [Claude Code](#claude-code)
    - [Cursor](#cursor)
    - [기타 MCP 클라이언트](#기타-mcp-클라이언트)
  - [사용 가능한 도구](#사용-가능한-도구)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [워크플로우](#워크플로우)
    - [기본 커밋](#기본-커밋)
    - [커밋 전 미리보기](#커밋-전-미리보기)
    - [그룹 커밋](#그룹-커밋)
    - [컨텍스트가 포함된 커밋](#컨텍스트가-포함된-커밋)
  - [구성](#구성)
  - [문제 해결](#문제-해결)
  - [참고 자료](#참고-자료)

## MCP란?

Model Context Protocol은 AI 애플리케이션이 구조화된 인터페이스를 통해 외부 도구를 호출할 수 있게 해주는 개방형 표준입니다. GAC를 MCP 서버로 실행하면 MCP 호환 클라이언트가 셸 명령을 직접 호출하지 않고도 저장소 상태를 검사하고 AI 기반 커밋을 생성할 수 있습니다.

## 이점

- **구조화된 상호작용**: 에이전트가 셸 출력을 파싱하는 대신 검증된 매개변수를 가진 타입이 지정된 도구를 호출합니다
- **두 도구 워크플로우**: `gac_status`로 검사하고 `gac_commit`으로 실행 - 에이전트 추론에 자연스러운 구조
- **전체 GAC 기능**: AI 커밋 메시지, 그룹 커밋, 비밀 스캔, 푸시 - 모두 MCP를 통해 사용 가능
- **제로 구성**: 서버는 기존 GAC 구성(`~/.gac.env`, 프로바이더 설정 등)을 사용합니다

## 설정

MCP 서버는 `gac serve`로 시작되며 표준 MCP 전송인 stdio를 통해 통신합니다.

### Claude Code

프로젝트의 `.mcp.json` 또는 전역 `~/.claude/claude_code_config.json`에 추가하세요:

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

또는 GAC가 전역으로 설치된 경우:

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

### Cursor

Cursor MCP 설정(`.cursor/mcp.json`)에 추가하세요:

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

### 기타 MCP 클라이언트

모든 MCP 호환 클라이언트에서 GAC를 사용할 수 있습니다. 서버 진입점은 다음과 같습니다:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

GAC가 설치되어 있다면 (`uv tool install gac`을 통해), `uvx gac` 대신 `gac`를 직접 사용할 수 있습니다.

## 사용 가능한 도구

서버는 두 가지 도구를 제공합니다:

### gac_status

저장소 상태를 검사합니다. 커밋하기 전에 무엇이 커밋될지 파악하기 위해 사용하세요.

**매개변수:**

| Parameter           | Type                                    | Default     | 설명                             |
| ------------------- | --------------------------------------- | ----------- | -------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | 출력 형식                        |
| `include_diff`      | bool                                    | `false`     | 전체 diff 내용 포함              |
| `include_stats`     | bool                                    | `true`      | 줄 변경 통계 포함                |
| `include_history`   | int                                     | `0`         | 포함할 최근 커밋 수              |
| `staged_only`       | bool                                    | `false`     | 스테이징된 변경 사항만 표시      |
| `include_untracked` | bool                                    | `true`      | 추적되지 않은 파일 포함          |
| `max_diff_lines`    | int                                     | `500`       | diff 출력 크기 제한 (0 = 무제한) |

**반환값:** 브랜치 이름, 파일 상태 (스테이징/비스테이징/미추적/충돌), 선택적 diff 내용, 선택적 통계, 선택적 커밋 이력.

### gac_commit

AI 기반 커밋 메시지를 생성하고 선택적으로 커밋을 실행합니다.

**매개변수:**

| Parameter          | Type           | Default | 설명                                           |
| ------------------ | -------------- | ------- | ---------------------------------------------- |
| `stage_all`        | bool           | `false` | 커밋 전 모든 변경 사항 스테이징 (`git add -A`) |
| `files`            | list[str]      | `[]`    | 스테이징할 특정 파일                           |
| `dry_run`          | bool           | `false` | 실행 없이 미리보기                             |
| `message_only`     | bool           | `false` | 커밋 없이 메시지만 생성                        |
| `push`             | bool           | `false` | 커밋 후 리모트에 푸시                          |
| `group`            | bool           | `false` | 변경 사항을 여러 논리적 커밋으로 분할          |
| `one_liner`        | bool           | `false` | 한 줄 커밋 메시지                              |
| `scope`            | string \| null | `null`  | 컨벤셔널 커밋 스코프 (미제공 시 자동 감지)     |
| `hint`             | string         | `""`    | 더 나은 메시지를 위한 추가 컨텍스트            |
| `model`            | string \| null | `null`  | AI 모델 재정의 (`provider:model_name`)         |
| `language`         | string \| null | `null`  | 커밋 메시지 언어 재정의                        |
| `skip_secret_scan` | bool           | `false` | 보안 스캔 건너뛰기                             |
| `no_verify`        | bool           | `false` | pre-commit hooks 건너뛰기                      |
| `auto_confirm`     | bool           | `false` | 확인 프롬프트 건너뛰기 (에이전트에 필수)       |

**반환값:** 성공 상태, 생성된 커밋 메시지, 커밋 해시 (커밋된 경우), 변경된 파일 목록, 경고.

## 워크플로우

### 기본 커밋

```text
1. gac_status()                              → 변경 사항 확인
2. gac_commit(stage_all=true, auto_confirm=true)  → 스테이징, 메시지 생성, 커밋
```

### 커밋 전 미리보기

```text
1. gac_status(include_diff=true, include_stats=true)  → 변경 사항 상세 검토
2. gac_commit(stage_all=true, dry_run=true)            → 커밋 메시지 미리보기
3. gac_commit(stage_all=true, auto_confirm=true)       → 커밋 실행
```

### 그룹 커밋

```text
1. gac_status()                                           → 모든 변경 사항 확인
2. gac_commit(stage_all=true, group=true, dry_run=true)   → 논리적 그룹화 미리보기
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → 그룹 커밋 실행
```

### 컨텍스트가 포함된 커밋

```text
1. gac_status(include_history=5)  → 스타일 참고를 위한 최근 커밋 확인
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## 구성

MCP 서버는 기존 GAC 구성을 사용합니다. 다음 외에 추가 설정이 필요하지 않습니다:

1. **프로바이더 및 모델**: `gac init` 또는 `gac model`을 실행하여 AI 프로바이더 구성
2. **API 키**: `~/.gac.env`에 저장 (`gac init` 중에 설정)
3. **선택적 설정**: 모든 GAC 환경 변수 적용 (`GAC_LANGUAGE`, `GAC_VERBOSE` 등)

모든 구성 옵션은 [메인 문서](USAGE.md#구성-노트)를 참조하세요.

## 문제 해결

### "No model configured"

MCP 서버를 사용하기 전에 `gac init`를 실행하여 AI 프로바이더와 모델을 설정하세요.

### "No staged changes found"

파일을 수동으로 스테이징하거나 (`git add`) `gac_commit` 호출에서 `stage_all=true`를 사용하세요.

### 서버가 시작되지 않음

GAC가 설치되어 있고 접근 가능한지 확인하세요:

```bash
uvx gac --version
# 또는
gac --version
```

`uvx`를 사용하는 경우 `uv`가 설치되어 있고 PATH에 포함되어 있는지 확인하세요.

### 에이전트가 서버를 찾을 수 없음

MCP 구성 파일이 클라이언트에 맞는 올바른 위치에 있고 `command` 경로가 셸 환경에서 접근 가능한지 확인하세요.

### Rich 출력 손상

MCP 서버는 stdio 프로토콜 손상을 방지하기 위해 모든 Rich 콘솔 출력을 자동으로 stderr로 리다이렉트합니다. 깨진 출력이 보이면 MCP 사용 시 `gac` 대신 `gac serve`를 실행하고 있는지 확인하세요.

## 참고 자료

- [메인 문서](USAGE.md)
- [Claude Code OAuth 설정](CLAUDE_CODE.md)
- [Qwen.ai OAuth 설정](QWEN.md)
- [문제 해결 가이드](TROUBLESHOOTING.md)
- [MCP 사양](https://modelcontextprotocol.io/)
