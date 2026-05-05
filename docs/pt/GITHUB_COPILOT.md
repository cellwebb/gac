# Usando o GitHub Copilot com o GAC

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | **Português** | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

O GAC suporta autenticação via GitHub Copilot, permitindo que você use sua assinatura do Copilot para acessar modelos da OpenAI, Anthropic, Google e mais — tudo incluído no seu plano do GitHub Copilot.

## O que é o GitHub Copilot OAuth?

O GitHub Copilot OAuth usa o **Device Flow** — um método de autenticação seguro baseado em navegador que não requer um servidor de callback local. Você visita uma URL, insere um código de uso único e autoriza o GAC a usar seu acesso ao Copilot. Nos bastidores, o GAC troca seu token OAuth do GitHub de longa duração por tokens de sessão do Copilot de curta duração (~30 min) que concedem acesso à API do Copilot.

Isso lhe dá acesso a modelos de múltiplos provedores através de uma única assinatura:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Benefícios

- **Acesso multi-provedor**: Use modelos da OpenAI, Anthropic e Google através de uma única assinatura
- **Custo-benefício**: Use sua assinatura existente do Copilot em vez de pagar por chaves de API separadas
- **Sem gerenciamento de chave de API**: Autenticação Device Flow — sem chaves para rotacionar ou armazenar
- **Suporte ao GitHub Enterprise**: Funciona com instâncias GHE através do flag `--host`

## Configuração

### Opção 1: Durante a configuração inicial (Recomendado)

Ao executar `gac init`, basta selecionar «Copilot» como seu provedor:

```bash
gac init
```

O assistente:

1. Pedirá que você selecione «Copilot» na lista de provedores
2. Exibirá um código de uso único e abrirá seu navegador para autenticação Device Flow
3. Salvará seu token OAuth em `~/.gac/oauth/copilot.json`
4. Definirá o modelo padrão

### Opção 2: Mudar para o Copilot mais tarde

Se você já configurou o GAC com outro provedor:

```bash
gac model
```

Em seguida, selecione «Copilot» na lista de provedores e autentique-se.

### Opção 3: Login direto

Autentique-se diretamente sem alterar seu modelo padrão:

```bash
gac auth copilot login
```

### Usar o GAC normalmente

Após a autenticação, use o GAC como de costume:

```bash
# Prepare suas alterações
git add .

# Gere e faça commit com o Copilot
gac

# Ou substitua o modelo para um único commit
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Modelos disponíveis

O Copilot fornece acesso a modelos de múltiplos provedores. Os modelos atuais incluem:

| Provedor  | Modelos                                                                                        |
| --------- | ---------------------------------------------------------------------------------------------- |
| OpenAI    | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google    | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Nota:** A lista de modelos mostrada após o login é informativa e pode ficar desatualizada conforme o GitHub adiciona novos modelos. Consulte a [documentação do GitHub Copilot](https://docs.github.com/en/copilot) para os modelos disponíveis mais recentes.

## GitHub Enterprise

Para autenticar com uma instância do GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

O GAC usará automaticamente o Device Flow correto e os endpoints de API para sua instância GHE. O token de sessão é armazenado em cache por host, portanto instâncias GHE diferentes são tratadas independentemente.

## Comandos de CLI

O GAC fornece comandos de CLI dedicados para gerenciamento de autenticação do Copilot:

### Login

Autentique-se ou reautentique-se com o GitHub Copilot:

```bash
gac auth copilot login
```

Seu navegador será aberto em uma página de Device Flow onde você insere um código de uso único. Se você já estiver autenticado, será perguntado se deseja reautenticar-se.

Para o GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Logout

Remova os tokens do Copilot armazenados:

```bash
gac auth copilot logout
```

Isso exclui o arquivo de token armazenado em `~/.gac/oauth/copilot.json` e o cache de sessão.

### Status

Verifique seu status de autenticação do Copilot atual:

```bash
gac auth copilot status
```

Ou verifique todos os provedores de uma vez:

```bash
gac auth
```

## Como Funciona

O fluxo de autenticação do Copilot difere do ChatGPT e do Claude Code OAuth:

1. **Device Flow** — O GAC solicita um código de dispositivo do GitHub e o exibe
2. **Autorização no navegador** — Você visita a URL e insere o código
3. **Polling de token** — O GAC faz polling do GitHub até você completar a autorização
4. **Troca de token de sessão** — O token OAuth do GitHub é trocado por um token de sessão do Copilot de curta duração
5. **Atualização automática** — Tokens de sessão (~30 min) são renovados automaticamente a partir do token OAuth em cache

Ao contrário do OAuth baseado em PKCE (ChatGPT/Claude Code), o Device Flow não requer um servidor de callback local ou gerenciamento de porta.

## Solução de problemas

### «Autenticação do Copilot não encontrada»

Execute o comando de login para autenticar-se:

```bash
gac auth copilot login
```

### «Não foi possível obter o token de sessão do Copilot»

Isso significa que o GAC obteve um token OAuth do GitHub, mas não conseguiu trocá-lo por um token de sessão do Copilot. Geralmente isso significa:

1. **Sem assinatura do Copilot** — Sua conta do GitHub não tem uma assinatura ativa do Copilot
2. **Token revogado** — O token OAuth foi revogado; reautentique-se com `gac auth copilot login`

### Token de sessão expirado

Tokens de sessão expiram após ~30 minutos. O GAC os renova automaticamente a partir do token OAuth em cache, então você não precisa reautenticar-se com frequência. Se a atualização automática falhar:

```bash
gac auth copilot login
```

### «Nome de host inválido ou inseguro»

O flag `--host` valida nomes de host estritamente para prevenir ataques SSRF. Se você vir este erro:

- Certifique-se de que o nome de host não inclui portas (ex: use `ghe.company.com` não `ghe.company.com:8080`)
- Não inclua protocolos ou caminhos (ex: use `ghe.company.com` não `https://ghe.company.com/api`)
- Endereços IP privados e `localhost` estão bloqueados por motivos de segurança

### Problemas com o GitHub Enterprise

Se a autenticação GHE falhar:

1. Verifique se sua instância GHE tem o Copilot habilitado
2. Verifique se o nome de host do GHE está acessível a partir da sua máquina
3. Certifique-se de que sua conta GHE tem uma licença do Copilot
4. Tente com o flag `--host` explicitamente: `gac auth copilot login --host ghe.mycompany.com`

## Diferenças em relação a outros provedores OAuth

| Recurso              | ChatGPT OAuth                   | Claude Code                  | Copilot                                      |
| -------------------- | ------------------------------- | ---------------------------- | -------------------------------------------- |
| Método de auth       | PKCE (callback do navegador)    | PKCE (callback do navegador) | Device Flow (código de uso único)            |
| Servidor de callback | Portas 1455-1465                | Portas 8765-8795             | Não necessário                               |
| Duração do token     | Longa duração (auto-atualizado) | Expirando (reautenticação)   | Sessão ~30 min (auto-atualizado)             |
| Modelos              | OpenAI otimizado para Codex     | Família Claude               | Multi-provedor (OpenAI + Anthropic + Google) |
| Suporte GHE          | Não                             | Não                          | Sim (flag `--host`)                          |

## Notas de segurança

- **Nunca faça commit do seu token OAuth** no controle de versão
- O GAC armazena tokens OAuth em `~/.gac/oauth/copilot.json` (fora do diretório do seu projeto)
- Tokens de sessão são armazenados em cache em `~/.gac/oauth/copilot_session.json` com permissões `0o600`
- Nomes de host são validados estritamente para prevenir ataques de SSRF e injeção de URL
- Endereços IP privados, endereços de loopback e `localhost` estão bloqueados como nomes de host
- O Device Flow não expõe portas locais, reduzindo a superfície de ataque

## Consulte também

- [Documentação principal](USAGE.md)
- [Guia de solução de problemas](TROUBLESHOOTING.md)
- [Guia do ChatGPT OAuth](CHATGPT_OAUTH.md)
- [Guia do Claude Code](CLAUDE_CODE.md)
- [Documentação do GitHub Copilot](https://docs.github.com/en/copilot)
