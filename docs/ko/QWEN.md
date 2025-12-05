[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | **한국어** | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# GAC와 함께 Qwen.ai 사용하기

GAC는 Qwen.ai OAuth를 통한 인증을 지원하여 Qwen.ai 계정을 사용하여 커밋 메시지를 생성할 수 있도록 합니다. 이는 원활한 로그인 경험을 위해 OAuth 디바이스 흐름 인증을 사용합니다.

## Qwen.ai란 무엇인가요?

Qwen.ai는 Qwen 대규모 언어 모델 제품군에 대한 액세스를 제공하는 Alibaba Cloud의 AI 플랫폼입니다. GAC는 OAuth 기반 인증을 지원하여 API 키를 수동으로 관리할 필요 없이 Qwen.ai 계정을 사용할 수 있도록 합니다.

## 이점

- **간편한 인증**: OAuth 디바이스 흐름 - 브라우저로 로그인하기만 하면 됩니다
- **API 키 관리 불필요**: 인증이 자동으로 처리됩니다
- **Qwen 모델 액세스**: 강력한 Qwen 모델을 사용하여 커밋 메시지 생성

## 설정

GAC에는 디바이스 흐름을 사용하는 Qwen.ai용 내장 OAuth 인증이 포함되어 있습니다. 설정 과정에서 코드가 표시되고 인증을 위해 브라우저가 열립니다.

### 옵션 1: 초기 설정 중 (권장)

`gac init`을 실행할 때 공급자 목록에서 "Qwen.ai (OAuth)"를 선택하기만 하면 됩니다:

```bash
gac init
```

마법사는 다음을 수행합니다:

1. 공급자 목록에서 "Qwen.ai (OAuth)"를 선택하도록 요청
2. 디바이스 코드를 표시하고 브라우저 열기
3. Qwen.ai에서 인증하고 코드 입력
4. 액세스 토큰을 안전하게 저장
5. 기본 모델 설정

### 옵션 2: 나중에 Qwen.ai로 전환

이미 다른 공급자로 GAC를 구성했고 Qwen.ai로 전환하려는 경우:

```bash
gac model
```

그런 다음:

1. 공급자 목록에서 "Qwen.ai (OAuth)" 선택
2. 디바이스 코드 인증 흐름 따르기
3. 토큰이 `~/.gac/oauth/qwen.json`에 안전하게 저장됨
4. 모델이 자동으로 구성됨

### 옵션 3: 직접 로그인

다음 명령을 사용하여 직접 인증할 수도 있습니다:

```bash
gac auth qwen login
```

그러면:

1. 디바이스 코드 표시
2. Qwen.ai 인증 페이지로 브라우저 열기
3. 인증 후 토큰이 자동으로 저장됨

### GAC 정상 사용

인증되면 평소와 같이 GAC를 사용하세요:

```bash
# 변경 사항 스테이징
git add .

# Qwen.ai로 생성 및 커밋
gac

# 또는 단일 커밋에 대해 모델 재정의
gac -m qwen:qwen3-coder-plus
```

## 사용 가능한 모델

Qwen.ai OAuth 통합은 다음을 사용합니다:

- `qwen3-coder-plus` - 코딩 작업에 최적화됨 (기본값)

이는 portal.qwen.ai OAuth 엔드포인트를 통해 사용할 수 있는 모델입니다. 다른 Qwen 모델의 경우 추가 Qwen 모델 옵션을 제공하는 OpenRouter 공급자를 사용하는 것을 고려해 보세요.

## 인증 명령

GAC는 Qwen.ai 인증 관리를 위한 몇 가지 명령을 제공합니다:

```bash
# Qwen.ai 로그인
gac auth qwen login

# 인증 상태 확인
gac auth qwen status

# 로그아웃 및 저장된 토큰 제거
gac auth qwen logout

# 모든 OAuth 공급자 상태 확인
gac auth
```

### 로그인 옵션

```bash
# 표준 로그인 (자동으로 브라우저 열기)
gac auth qwen login

# 브라우저를 열지 않고 로그인 (수동으로 방문할 URL 표시)
gac auth qwen login --no-browser

# 조용한 모드 (최소 출력)
gac auth qwen login --quiet
```

## 문제 해결

### 토큰 만료됨

인증 오류가 표시되면 토큰이 만료되었을 수 있습니다. 다음을 실행하여 다시 인증하세요:

```bash
gac auth qwen login
```

디바이스 코드 흐름이 시작되고 재인증을 위해 브라우저가 열립니다.

### 인증 상태 확인

현재 인증되어 있는지 확인하려면:

```bash
gac auth qwen status
```

또는 모든 공급자를 한 번에 확인하세요:

```bash
gac auth
```

### 로그아웃

저장된 토큰을 제거하려면:

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (Qwen 인증을 찾을 수 없음)

이는 GAC가 액세스 토큰을 찾을 수 없음을 의미합니다. 다음을 실행하여 인증하세요:

```bash
gac auth qwen login
```

또는 `gac model`을 실행하고 공급자 목록에서 "Qwen.ai (OAuth)"를 선택하세요.

### "Authentication failed" (인증 실패)

OAuth 인증이 실패하는 경우:

1. Qwen.ai 계정이 있는지 확인하세요
2. 브라우저가 올바르게 열리는지 확인하세요
3. 디바이스 코드를 올바르게 입력했는지 확인하세요
4. 문제가 지속되면 다른 브라우저를 사용해 보세요
5. `qwen.ai`에 대한 네트워크 연결을 확인하세요

### 디바이스 코드가 작동하지 않음

디바이스 코드 인증이 작동하지 않는 경우:

1. 코드가 만료되지 않았는지 확인하세요 (코드는 제한된 시간 동안 유효함)
2. `gac auth qwen login`을 다시 실행하여 새 코드를 받으세요
3. 브라우저 열기에 실패하면 `--no-browser` 플래그를 사용하여 URL을 수동으로 방문하세요

## 보안 참고 사항

- **절대 액세스 토큰을 버전 관리에 커밋하지 마세요**
- GAC는 토큰을 `~/.gac/oauth/qwen.json` (프로젝트 디렉터리 외부)에 자동으로 저장합니다
- 토큰 파일에는 제한된 권한이 있습니다 (소유자만 읽기 가능)
- 토큰은 만료될 수 있으며 재인증이 필요합니다
- OAuth 디바이스 흐름은 헤드리스 시스템에서의 안전한 인증을 위해 설계되었습니다

## 같이 보기

- [메인 문서](USAGE.md)
- [Claude Code 설정](CLAUDE_CODE.md)
- [문제 해결 가이드](TROUBLESHOOTING.md)
- [Qwen.ai 문서](https://qwen.ai)
