# GAC에서 Claude Code 사용하기

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | **한국어** | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC은 Claude Code 구독을 통한 인증을 지원하며, 비싼 Anthropic API를 지불하는 대신 Claude Code 구독을 사용할 수 있습니다. 이는 이미 구독을 통해 Claude Code 액세스 권한을 가진 사용자에게 완벽합니다.

## Claude Code란?

Claude Code는 Anthropic의 구독 서비스로, OAuth 기반의 Claude 모델 액세스를 제공합니다. API 키(토큰당 과금)를 사용하는 대신, Claude Code는 구독의 OAuth 토큰을 사용합니다.

## 이점

- **비용 효율성**: 기존 Claude Code 구독을 사용하고 API 액세스를 별도로 지불할 필요가 없습니다
- **동일한 모델**: 동일한 Claude 모델(예: `claude-sonnet-4-5`)에 액세스할 수 있습니다
- **별도 과금**: Claude Code 사용은 Anthropic API 과금과 분리되어 있습니다

## 설정

GAC에는 Claude Code용 내장 OAuth 인증이 포함되어 있습니다. 설정 프로세스는 완전 자동화되어 있으며 인증을 위해 브라우저를 열 것입니다.

### 옵션 1: 초기 설정 중 (권장)

`gac init`를 실행할 때, 공급자로 "Claude Code"를 선택하기만 하면 됩니다:

```bash
gac init
```

마법사는 다음을 수행합니다:

1. 공급자 목록에서 "Claude Code"를 선택하도록 요청합니다
2. OAuth 인증을 위해 브라우저를 자동으로 엽니다
3. 액세스 토큰을 `~/.gac.env`에 저장합니다
4. 기본 모델을 설정합니다

### 옵션 2: 나중에 Claude Code로 전환

다른 공급자로 GAC를 이미 설정했고 Claude Code로 전환하려는 경우:

```bash
gac model
```

그런 다음:

1. 공급자 목록에서 "Claude Code"를 선택합니다
2. OAuth 인증을 위해 브라우저가 자동으로 열립니다
3. 토큰이 `~/.gac.env`에 저장됩니다
4. 모델이 자동으로 설정됩니다

### GAC 정상적으로 사용

인증되면 평소처럼 GAC를 사용할 수 있습니다:

```bash
# 변경 사항을 스테이징
git add .

# Claude Code로 생성하고 커밋
gac

# 또는 단일 커밋을 위해 모델을 재정의
gac -m claude-code:claude-sonnet-4-5
```

## 사용 가능한 모델

Claude Code는 Anthropic API와 동일한 모델 액세스를 제공합니다. 현재 Claude 4.5 패밀리 모델은 다음을 포함합니다:

- `claude-sonnet-4-5` - 최신이고 가장 지능적인 Sonnet 모델, 코딩에 최적
- `claude-haiku-4-5` - 빠르고 효율적
- `claude-opus-4-1` - 복잡한 추론에서 가장 강력한 모델

사용 가능한 모델의 전체 목록은 [Claude 문서](https://docs.claude.com/en/docs/about-claude/models/overview)를 확인하세요.

## 문제 해결

### 토큰 만료됨

인증 오류가 표시되면 토큰이 만료되었을 수 있습니다. 다음을 실행하여 재인증하세요:

```bash
gac model
```

그런 다음 "Claude Code"를 선택하고 "재인증 (새 토큰 받기)"를 선택하세요. 새 OAuth 인증을 위해 브라우저가 열릴 것입니다.

### "CLAUDE_CODE_ACCESS_TOKEN을 찾을 수 없음"

이는 GAC가 액세스 토큰을 찾을 수 없다는 의미입니다. 다음을 실행하여 인증하세요:

```bash
gac model
```

그런 다음 공급자 목록에서 "Claude Code"를 선택하세요. OAuth 플로우가 자동으로 시작될 것입니다.

### "인증 실패"

OAuth 인증이 실패하면:

1. 활성 Claude Code 구독이 있는지 확인하세요
2. 브라우저가 올바르게 열리는지 확인하세요
3. 문제가 지속되면 다른 브라우저를 시도하세요
4. `claude.ai`로의 네트워크 연결을 확인하세요
5. 포트 8765-8795가 로컬 콜백 서버에 사용 가능한지 확인하세요

## Anthropic 공급자와의 차이점

| 기능      | Anthropic (`anthropic:`)     | Claude Code (`claude-code:`)                       |
| --------- | ---------------------------- | -------------------------------------------------- |
| 인증      | API 키 (`ANTHROPIC_API_KEY`) | OAuth (자동 브라우저 플로우)                       |
| 과금      | 토큰당 API 과금              | 구독 기반                                          |
| 설정      | 수동 API 키 입력             | `gac init` 또는 `gac model`를 통한 자동 OAuth      |
| 토큰 관리 | 장기 API 키                  | OAuth 토큰 (만료될 수 있음, `model`로 쉬운 재인증) |
| 모델      | 동일한 모델                  | 동일한 모델                                        |

## 보안 참고사항

- **액세스 토큰을 버전 관리에 커밋하지 마세요**
- GAC는 토큰을 `~/.gac.env` (프로젝트 디렉토리 외부)에 자동으로 저장합니다
- 토큰은 만료될 수 있으며 `gac model`을 통한 재인증이 필요할 수 있습니다
- OAuth 플로우는 보안 강화를 위해 PKCE (Proof Key for Code Exchange)를 사용합니다
- 로컬 콜백 서버는 로컬호스트에서만 실행됩니다 (포트 8765-8795)

## 참고 자료

- [메인 문서](USAGE.md)
- [문제 해결 가이드](TROUBLESHOOTING.md)
- [Claude Code 문서](https://claude.ai/code)
