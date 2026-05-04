# Usar o ChatGPT OAuth com o GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

O GAC suporta autenticação via ChatGPT OAuth, permitindo que você use sua assinatura do ChatGPT para acessar a API Codex da OpenAI em vez de pagar separadamente por chaves de API da OpenAI. Isso reflete o mesmo fluxo OAuth usado pelo CLI Codex da OpenAI.

> ⚠️ **Atenção — uso não autorizado:** Isso usa o mesmo fluxo OAuth que o CLI Codex da OpenAI e, embora funcione atualmente, a OpenAI pode restringir o uso de tokens de terceiros a qualquer momento. O GAC é pequeno o suficiente para ter passado despercebido até agora, mas o uso do ChatGPT OAuth aqui **não é oficialmente aprovado** para ferramentas de terceiros e pode parar de funcionar a qualquer momento. Se você precisar de geração confiável de mensagens de commit, use um provedor de API direto (`openai`, etc.). Consulte a [documentação do Codex da OpenAI](https://openai.com/codex) para conhecer a política atual.

## O que é o ChatGPT OAuth?

O ChatGPT OAuth permite que você aproveite sua assinatura existente do ChatGPT Plus ou Pro para acessar a API Codex para gerar mensagens de commit. Em vez de gerenciar chaves de API e cobrança por token, você se autentica uma vez através do seu navegador e o GAC gerencia automaticamente o ciclo de vida do token.

## Benefícios

- **Custo-benefício**: Use sua assinatura existente do ChatGPT Plus/Pro em vez de pagar separadamente pelo acesso à API
- **Mesmos modelos**: Acesse modelos otimizados para Codex (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **Sem gerenciamento de chave de API**: OAuth baseado em navegador significa que não há chaves de API para rotacionar ou armazenar
- **Cobrança separada**: O uso do ChatGPT OAuth é separado da cobrança direta da API da OpenAI

## Configuração

O GAC inclui autenticação OAuth integrada para o ChatGPT. O processo de configuração é totalmente automatizado e abrirá seu navegador para autenticação.

### Opção 1: Durante a configuração inicial (Recomendado)

Ao executar `gac init`, basta selecionar «ChatGPT OAuth» como seu provedor:

```bash
gac init
```

O assistente:

1. Pedirá que você selecione «ChatGPT OAuth» na lista de provedores
2. Abrirá automaticamente seu navegador para autenticação OAuth
3. Salvará seu token de acesso em `~/.gac/oauth/chatgpt-oauth.json`
4. Definirá o modelo padrão

### Opção 2: Mudar para o ChatGPT OAuth mais tarde

Se você já configurou o GAC com outro provedor e deseja mudar para o ChatGPT OAuth:

```bash
gac model
```

Em seguida:

1. Selecione «ChatGPT OAuth» na lista de provedores
2. Seu navegador será aberto automaticamente para autenticação OAuth
3. Token salvo em `~/.gac/oauth/chatgpt-oauth.json`
4. Modelo configurado automaticamente

### Usar o GAC normalmente

Após a autenticação, use o GAC como de costume:

```bash
# Prepare suas alterações
git add .

# Gere e faça commit com o ChatGPT OAuth
gac

# Ou substitua o modelo para um único commit
gac -m chatgpt-oauth:gpt-5.5
```

## Modelos disponíveis

O ChatGPT OAuth fornece acesso a modelos otimizados para Codex. Os modelos atuais incluem:

- `gpt-5.5` — Modelo Codex mais recente e capaz
- `gpt-5.4` — Modelo Codex de geração anterior
- `gpt-5.3-codex` — Modelo Codex de terceira geração

Consulte a [documentação da OpenAI](https://platform.openai.com/docs/models) para obter a lista completa de modelos disponíveis.

## Comandos de CLI

O GAC fornece comandos de CLI dedicados para gerenciamento do ChatGPT OAuth:

### Login

Autentique-se ou reautentique-se com o ChatGPT OAuth:

```bash
gac auth chatgpt login
```

Seu navegador será aberto automaticamente para concluir o fluxo OAuth. Se você já estiver autenticado, isso atualizará seus tokens.

### Logout

Remova os tokens do ChatGPT OAuth armazenados:

```bash
gac auth chatgpt logout
```

Isso exclui o arquivo de token armazenado em `~/.gac/oauth/chatgpt-oauth.json`.

### Status

Verifique seu status de autenticação do ChatGPT OAuth atual:

```bash
gac auth chatgpt status
```

Ou verifique todos os provedores de uma vez:

```bash
gac auth
```

## Solução de problemas

### Token expirado

Se você vir erros de autenticação, seu token pode ter expirado. Reautentique-se executando:

```bash
gac auth chatgpt login
```

Seu navegador será aberto automaticamente para nova autenticação OAuth. O GAC usa automaticamente tokens de atualização para renovar o acesso sem reautenticação quando possível.

### Verificar o status de autenticação

Para verificar se você está atualmente autenticado:

```bash
gac auth chatgpt status
```

Ou verifique todos os provedores de uma vez:

```bash
gac auth
```

### Logout

Para remover seu token armazenado:

```bash
gac auth chatgpt logout
```

### «Token do ChatGPT OAuth não encontrado»

Isso significa que o GAC não consegue encontrar seu token de acesso. Autentique-se executando:

```bash
gac model
```

Em seguida, selecione «ChatGPT OAuth» na lista de provedores. O fluxo OAuth será iniciado automaticamente.

### «Falha na autenticação»

Se a autenticação OAuth falhar:

1. Certifique-se de ter uma assinatura ativa do ChatGPT Plus ou Pro
2. Verifique se seu navegador abre corretamente
3. Tente um navegador diferente se os problemas persistirem
4. Verifique a conectividade de rede com `auth.openai.com`
5. Verifique se as portas 1455-1465 estão disponíveis para o servidor de retorno de chamada local

### Porta já em uso

O servidor de retorno de chamada do OAuth tenta automaticamente as portas 1455-1465. Se todas as portas estiverem ocupadas:

```bash
# No macOS/Linux:
lsof -ti:1455-1465 | xargs kill -9

# No Windows (PowerShell):
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Em seguida, execute novamente `gac auth chatgpt login`.

## Diferenças em relação ao provedor da OpenAI

| Recurso                 | OpenAI (`openai:`)              | ChatGPT OAuth (`chatgpt-oauth:`)                                |
| ----------------------- | ------------------------------- | --------------------------------------------------------------- |
| Autenticação            | Chave de API (`OPENAI_API_KEY`) | OAuth (fluxo de navegador automatizado)                         |
| Cobrança                | Cobrança de API por token       | Baseada em assinatura (ChatGPT Plus/Pro)                        |
| Configuração            | Inserção manual da chave de API | OAuth automático via `gac init` ou `gac model`                  |
| Gerenciamento de tokens | Chaves de API de longa duração  | Tokens OAuth (atualização automática com tokens de atualização) |
| Modelos                 | Todos os modelos da OpenAI      | Modelos otimizados para Codex                                   |

## Notas de segurança

- **Nunca faça commit do seu token de acesso** no controle de versão
- O GAC armazena tokens OAuth em `~/.gac/oauth/chatgpt-oauth.json` (fora do diretório do seu projeto)
- O fluxo OAuth usa PKCE (Proof Key for Code Exchange) para maior segurança
- O servidor de retorno de chamada local é executado apenas em localhost (portas 1455-1465)
- Tokens de atualização são usados para renovar automaticamente o acesso sem reautenticação

## Consulte também

- [Documentação principal](USAGE.md)
- [Guia de solução de problemas](TROUBLESHOOTING.md)
- [Documentação do Codex da OpenAI](https://openai.com/codex)
