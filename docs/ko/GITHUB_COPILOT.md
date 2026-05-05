# GAC 에서 GitHub Copilot 사용하기

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | **한국어** | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC 는 GitHub Copilot 을 통한 인증을 지원하며, Copilot 구독을 사용하여 OpenAI, Anthropic, Google 등의 모델에 액세스할 수 있습니다 — 모두 GitHub Copilot 플랜에 포함되어 있습니다.

## GitHub Copilot OAuth 란?

GitHub Copilot OAuth 는 **Device Flow** 를 사용합니다 — 로컬 콜백 서버가 필요 없는 안전한 브라우저 기반 인증 방식입니다. URL 을 방문하여 일회성 코드를 입력하고, GAC 가 Copilot 액세스를 사용하도록 승인합니다. 백그라운드에서 GAC 은 장수명 GitHub OAuth 토큰을 Copilot API 에 대한 액세스 권한을 부여하는 단수명 Copilot 세션 토큰(약 30분)으로 교환합니다.

이를 통해 단일 구독으로 여러 제공업체의 모델에 액세스할 수 있습니다:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## 장점

- **멀티 제공업체 액세스**: 단일 구독으로 OpenAI, Anthropic, Google 의 모델 사용
- **비용 효율적**: 별도의 API 키 결제 대신 기존 Copilot 구독 사용
- **API 키 관리 불필요**: Device Flow 인증 — 회전하거나 저장할 키 없음
- **GitHub Enterprise 지원**: `--host` 플래그로 GHE 인스턴스 지원

## 설정

### 옵션 1: 초기 설정 중 (권장)

`gac init` 을 실행할 때 제공업체로 "Copilot"을 선택하기만 하면 됩니다:

```bash
gac init
```

마법사가 다음을 수행합니다:

1. 제공업체 목록에서 "Copilot"을 선택하도록 요청합니다
2. 일회성 코드를 표시하고 Device Flow 인증을 위해 브라우저를 엽니다
3. OAuth 토큰을 `~/.gac/oauth/copilot.json` 에 저장합니다
4. 기본 모델을 설정합니다

### 옵션 2: 나중에 Copilot 으로 전환

이미 GAC 을 다른 제공업체로 구성한 경우:

```bash
gac model
```

제공업체 목록에서 "Copilot"을 선택하고 인증합니다.

### 옵션 3: 직접 로그인

기본 모델을 변경하지 않고 직접 인증합니다:

```bash
gac auth copilot login
```

### 일반적으로 GAC 사용하기

인증 후 평소와 같이 GAC 을 사용합니다:

```bash
# 변경 사항 스테이징
git add .

# Copilot 으로 생성 및 커밋
gac

# 또는 단일 커밋에 대해 모델 재정의
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## 사용 가능한 모델

Copilot 은 여러 제공업체의 모델에 대한 액세스를 제공합니다. 현재 모델은 다음과 같습니다:

| 제공업체  | 모델                                                                                           |
| --------- | ---------------------------------------------------------------------------------------------- |
| OpenAI    | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google    | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **참고:** 로그인 후 표시되는 모델 목록은 참고용이며, GitHub 가 새로운 모델을 추가함에 따라 구식이 될 수 있습니다. 최신 사용 가능한 모델은 [GitHub Copilot 문서](https://docs.github.com/en/copilot) 를 확인하세요.

## GitHub Enterprise

GitHub Enterprise 인스턴스로 인증하려면:

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC 은 GHE 인스턴스에 적합한 Device Flow 및 API 엔드포인트를 자동으로 사용합니다. 세션 토큰은 호스트별로 캐시되므로 다른 GHE 인스턴스가 개별적으로 처리됩니다.

## CLI 명령

GAC 은 Copilot 인증 관리를 위한 전용 CLI 명령을 제공합니다:

### 로그인

GitHub Copilot 로 인증 또는 재인증합니다:

```bash
gac auth copilot login
```

Device Flow 페이지에서 일회성 코드를 입력하기 위해 브라우저가 열립니다. 이미 인증된 경우 재인증 여부를 확인합니다.

GitHub Enterprise 의 경우:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### 로그아웃

저장된 Copilot 토큰을 제거합니다:

```bash
gac auth copilot logout
```

이렇게 하면 `~/.gac/oauth/copilot.json` 에 저장된 토큰 파일과 세션 캐시가 삭제됩니다.

### 상태

현재 Copilot 인증 상태를 확인합니다:

```bash
gac auth copilot status
```

또는 모든 제공업체를 한 번에 확인합니다:

```bash
gac auth
```

## 작동 방식

Copilot 인증 플로우는 ChatGPT 및 Claude Code OAuth 와 다릅니다:

1. **Device Flow** — GAC 이 GitHub 에 디바이스 코드를 요청하고 표시합니다
2. **브라우저 승인** — URL 을 방문하여 코드를 입력합니다
3. **토큰 폴링** — 승인이 완료될 때까지 GAC 이 GitHub 을 폴링합니다
4. **세션 토큰 교환** — GitHub OAuth 토큰이 단수명 Copilot 세션 토큰으로 교환됩니다
5. **자동 새로 고침** — 세션 토큰(약 30분)은 캐시된 OAuth 토큰에서 자동으로 갱신됩니다

PKCE 기반 OAuth(ChatGPT/Claude Code) 와 달리 Device Flow 는 로컬 콜백 서버나 포트 관리가 필요하지 않습니다.

## 문제 해결

### "Copilot 인증을 찾을 수 없음"

인증하려면 로그인 명령을 실행하세요:

```bash
gac auth copilot login
```

### "Copilot 세션 토큰을 가져올 수 없음"

이는 GAC 이 GitHub OAuth 토큰을 받았지만 Copilot 세션 토큰으로 교환할 수 없었음을 의미합니다. 일반적으로 다음 이유 때문입니다:

1. **Copilot 구독 없음** — GitHub 계정에 활성 Copilot 구독이 없음
2. **토큰 취소** — OAuth 토큰이 취소되었습니다. `gac auth copilot login` 으로 재인증하세요

### 세션 토큰 만료

세션 토큰은 약 30분 후에 만료됩니다. GAC 은 캐시된 OAuth 토큰에서 자동으로 갱신하므로 빈번한 재인증이 필요하지 않습니다. 자동 갱신이 실패하는 경우:

```bash
gac auth copilot login
```

### "잘못되거나 안전하지 않은 호스트 이름"

`--host` 플래그는 SSRF 공격을 방지하기 위해 호스트 이름을 엄격하게 검증합니다. 이 오류가 표시되면:

- 호스트 이름에 포트가 포함되지 않았는지 확인하세요 (예: `ghe.company.com:8080` 대신 `ghe.company.com` 사용)
- 프로토콜이나 경로를 포함하지 마세요 (예: `https://ghe.company.com/api` 대신 `ghe.company.com` 사용)
- 프라이빗 IP 주소와 `localhost` 는 보안상의 이유로 차단됩니다

### GitHub Enterprise 문제

GHE 인증이 실패하는 경우:

1. GHE 인스턴스에서 Copilot 이 활성화되어 있는지 확인하세요
2. GHE 호스트 이름이 컴퓨터에서 접근 가능한지 확인하세요
3. GHE 계정에 Copilot 라이선스가 있는지 확인하세요
4. `--host` 플래그를 명시적으로 시도하세요: `gac auth copilot login --host ghe.mycompany.com`

## 다른 OAuth 제공업체와의 차이점

| 기능      | ChatGPT OAuth           | Claude Code          | Copilot                                     |
| --------- | ----------------------- | -------------------- | ------------------------------------------- |
| 인증 방식 | PKCE (브라우저 콜백)    | PKCE (브라우저 콜백) | Device Flow (일회성 코드)                   |
| 콜백 서버 | 포트 1455-1465          | 포트 8765-8795       | 불필요                                      |
| 토큰 수명 | 장수명 (자동 새로 고침) | 만료 (재인증)        | 세션 약 30분 (자동 새로 고침)               |
| 모델      | Codex 최적화 OpenAI     | Claude 패밀리        | 멀티 제공업체 (OpenAI + Anthropic + Google) |
| GHE 지원  | 아니요                  | 아니요               | 예 (`--host` 플래그)                        |

## 보안 참고 사항

- **OAuth 토큰을 버전 관리에 커밋하지 마십시오**
- GAC 은 OAuth 토큰을 `~/.gac/oauth/copilot.json` 에 저장합니다 (프로젝트 디렉토리 외부)
- 세션 토큰은 `0o600` 권한으로 `~/.gac/oauth/copilot_session.json` 에 캐시됩니다
- 호스트 이름은 SSRF 및 URL 인젝션 공격을 방지하기 위해 엄격하게 검증됩니다
- 프라이빗 IP 주소, 루프백 주소 및 `localhost` 는 호스트 이름으로 차단됩니다
- Device Flow 는 로컬 포트를 노출하지 않아 공격 표면이 감소합니다

## 관련 링크

- [메인 문서](USAGE.md)
- [문제 해결 가이드](TROUBLESHOOTING.md)
- [ChatGPT OAuth 설정 가이드](CHATGPT_OAUTH.md)
- [Claude Code 설정 가이드](CLAUDE_CODE.md)
- [GitHub Copilot 문서](https://docs.github.com/en/copilot)
