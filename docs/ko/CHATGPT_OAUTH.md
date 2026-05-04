# GAC 에서 ChatGPT OAuth 사용하기

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC 는 ChatGPT OAuth 를 통한 인증을 지원하며, OpenAI API 키를 별도로 지불하지 않고도 ChatGPT 구독을 사용하여 OpenAI 의 Codex API 에 액세스할 수 있습니다. 이는 OpenAI 의 Codex CLI 와 동일한 OAuth 플로우를 사용합니다.

> ⚠️ **주의 — 비공식 사용:** 이는 OpenAI 의 Codex CLI 와 동일한 OAuth 플로우를 사용하며, 현재는 작동하지만 OpenAI 는 언제든지 타사 토큰 사용을 제한할 수 있습니다. GAC 는 충분히 작아서 지금까지는 눈에 띄지 않았지만, 여기서 ChatGPT OAuth 를 사용하는 것은 타사 도구에 대해 **공식적으로 승인되지 않았으며** 언제든지 작동이 중단될 수 있습니다. 안정적인 커밋 메시지 생성이 필요한 경우 직접 API 제공업체 (`openai` 등) 를 사용하십시오. 현재 정책은 [OpenAI 의 Codex 문서](https://openai.com/codex) 를 참조하십시오.

## ChatGPT OAuth 란?

ChatGPT OAuth 를 사용하면 기존 ChatGPT Plus 또는 Pro 구독을 활용하여 커밋 메시지를 생성하기 위해 Codex API 에 액세스할 수 있습니다. API 키 및 토큰당 과금을 관리하는 대신 브라우저로 한 번 인증하면 GAC 가 토큰 수명 주기를 자동으로 처리합니다.

## 장점

- **비용 효율적**: 기존 ChatGPT Plus/Pro 구독을 사용하며 API 액세스를 별도로 지불할 필요가 없습니다
- **동일한 모델**: Codex 최적화 모델 (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`) 에 액세스할 수 있습니다
- **API 키 관리 불필요**: 브라우저 기반 OAuth 로 API 키를 로테이션하거나 저장할 필요가 없습니다
- **별도 청구**: ChatGPT OAuth 사용은 직접 OpenAI API 청구와 분리됩니다

## 설정

GAC 에는 ChatGPT 용 내장 OAuth 인증이 포함되어 있습니다. 설정 프로세스는 완전히 자동화되며 브라우저를 열어 인증합니다.

### 옵션 1: 초기 설정 중 (권장)

`gac init` 을 실행할 때 제공업체로 "ChatGPT OAuth"를 선택하기만 하면 됩니다:

```bash
gac init
```

마법사가 다음을 수행합니다:

1. 제공업체 목록에서 "ChatGPT OAuth"를 선택하도록 요청합니다
2. 브라우저를 자동으로 열어 OAuth 인증을 수행합니다
3. 액세스 토큰을 `~/.gac/oauth/chatgpt-oauth.json` 에 저장합니다
4. 기본 모델을 설정합니다

### 옵션 2: 나중에 ChatGPT OAuth 로 전환

이미 GAC 를 다른 제공업체로 구성했고 ChatGPT OAuth 로 전환하려는 경우:

```bash
gac model
```

그런 다음:

1. 제공업체 목록에서 "ChatGPT OAuth"를 선택합니다
2. 브라우저가 자동으로 열려 OAuth 인증을 수행합니다
3. 토큰은 `~/.gac/oauth/chatgpt-oauth.json` 에 저장됩니다
4. 모델이 자동으로 구성됩니다

### 일반적으로 GAC 사용하기

인증 후 평소와 같이 GAC 를 사용합니다:

```bash
# 변경 사항 스테이징
git add .

# ChatGPT OAuth 로 생성 및 커밋
gac

# 또는 단일 커밋에 대해 모델 재정의
gac -m chatgpt-oauth:gpt-5.5
```

## 사용 가능한 모델

ChatGPT OAuth 는 Codex 최적화 모델에 대한 액세스를 제공합니다. 현재 모델은 다음과 같습니다:

- `gpt-5.5` — 최신이며 가장 강력한 Codex 모델
- `gpt-5.4` — 이전 세대 Codex 모델
- `gpt-5.3-codex` — 3 세대 Codex 모델

사용 가능한 모델의 전체 목록은 [OpenAI 문서](https://platform.openai.com/docs/models) 를 확인하십시오.

## CLI 명령

GAC 는 ChatGPT OAuth 관리를 위한 전용 CLI 명령을 제공합니다:

### 로그인

ChatGPT OAuth 로 인증 또는 재인증합니다:

```bash
gac auth chatgpt login
```

브라우저가 자동으로 열려 OAuth 플로우가 완료됩니다. 이미 인증된 경우 토큰을 새로 고칩니다.

### 로그아웃

저장된 ChatGPT OAuth 토큰을 제거합니다:

```bash
gac auth chatgpt logout
```

이렇게 하면 `~/.gac/oauth/chatgpt-oauth.json` 에 저장된 토큰 파일이 삭제됩니다.

### 상태

현재 ChatGPT OAuth 인증 상태를 확인합니다:

```bash
gac auth chatgpt status
```

또는 모든 제공업체를 한 번에 확인합니다:

```bash
gac auth
```

## 문제 해결

### 토큰 만료

인증 오류가 표시되면 토큰이 만료되었을 수 있습니다. 다음 명령을 실행하여 재인증합니다:

```bash
gac auth chatgpt login
```

브라우저가 자동으로 열려 새 OAuth 인증이 수행됩니다. GAC 는 가능할 경우 리프레시 토큰을 사용하여 재인증 없이 액세스를 자동으로 갱신합니다.

### 인증 상태 확인

현재 인증되어 있는지 확인하려면:

```bash
gac auth chatgpt status
```

또는 모든 제공업체를 한 번에 확인합니다:

```bash
gac auth
```

### 로그아웃

저장된 토큰을 제거하려면:

```bash
gac auth chatgpt logout
```

### "ChatGPT OAuth 토큰을 찾을 수 없음"

이는 GAC 가 액세스 토큰을 찾을 수 없음을 의미합니다. 다음 명령을 실행하여 인증합니다:

```bash
gac model
```

그런 다음 제공업체 목록에서 "ChatGPT OAuth"를 선택합니다. OAuth 플로우가 자동으로 시작됩니다.

### "인증 실패"

OAuth 인증이 실패하는 경우:

1. 활성 ChatGPT Plus 또는 Pro 구독이 있는지 확인하십시오
2. 브라우저가 올바르게 열리는지 확인하십시오
3. 문제가 지속되면 다른 브라우저를 시도하십시오
4. `auth.openai.com` 에 대한 네트워크 연결을 확인하십시오
5. 로컬 콜백 서버에 포트 1455-1465 를 사용할 수 있는지 확인하십시오

### 포트가 이미 사용 중

OAuth 콜백 서버는 포트 1455-1465 를 자동으로 시도합니다. 모든 포트가 점유된 경우:

```bash
# macOS/Linux 에서:
lsof -ti:1455-1465 | xargs kill -9

# Windows (PowerShell) 에서:
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

그런 다음 `gac auth chatgpt login` 을 다시 실행합니다.

## OpenAI 제공업체와의 차이점

| 기능      | OpenAI (`openai:`)        | ChatGPT OAuth (`chatgpt-oauth:`)               |
| --------- | ------------------------- | ---------------------------------------------- |
| 인증      | API 키 (`OPENAI_API_KEY`) | OAuth (자동화된 브라우저 플로우)               |
| 청구      | 토큰당 API 청구           | 구독 기반 (ChatGPT Plus/Pro)                   |
| 설정      | 수동 API 키 입력          | `gac init` 또는 `gac model` 을 통한 자동 OAuth |
| 토큰 관리 | 장수명 API 키             | OAuth 토큰 (리프레시 토큰으로 자동 새로 고침)  |
| 모델      | 모든 OpenAI 모델          | Codex 최적화 모델                              |

## 보안 참고 사항

- **액세스 토큰을 버전 관리에 커밋하지 마십시오**
- GAC 는 OAuth 토큰을 `~/.gac/oauth/chatgpt-oauth.json` 에 저장합니다 (프로젝트 디렉토리 외부)
- OAuth 플로는 보안을 위해 PKCE (Proof Key for Code Exchange) 를 사용합니다
- 로컬 콜백 서버는 localhost 에서만 실행됩니다 (포트 1455-1465)
- 리프레시 토큰을 사용하여 재인증 없이 액세스를 자동으로 갱신합니다

## 관련 링크

- [메인 문서](USAGE.md)
- [문제 해결 가이드](TROUBLESHOOTING.md)
- [OpenAI 의 Codex 문서](https://openai.com/codex)
