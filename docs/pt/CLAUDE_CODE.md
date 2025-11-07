# Usando Claude Code com GAC

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | **Português** | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC suporta autenticação através de assinaturas Claude Code, permitindo que você use sua assinatura Claude Code em vez de pagar pela API Anthropic cara. Isso é perfeito para usuários que já têm acesso a Claude Code através de sua assinatura.

## O que é Claude Code?

Claude Code é o serviço de assinatura da Anthropic que fornece acesso aos modelos Claude baseado em OAuth. Em vez de usar chaves API (que são cobradas por token), Claude Code usa tokens OAuth da sua assinatura.

## Benefícios

- **Custo-efetivo**: Use sua assinatura Claude Code existente em vez de pagar separadamente por acesso à API
- **Mesmos modelos**: Acesse os mesmos modelos Claude (ex., `claude-sonnet-4-5`)
- **Cobrança separada**: O uso do Claude Code é separado da cobrança da API Anthropic

## Configuração

GAC inclui autenticação OAuth integrada para Claude Code. O processo de configuração é totalmente automatizado e abrirá seu navegador para autenticação.

### Opção 1: Durante a Configuração Inicial (Recomendado)

Ao executar `gac init`, simplesmente selecione "Claude Code" como seu provedor:

```bash
gac init
```

O assistente irá:

1. Pedir que você selecione "Claude Code" da lista de provedores
2. Abrir automaticamente seu navegador para autenticação OAuth
3. Salvar seu token de acesso em `~/.gac.env`
4. Definir o modelo padrão

### Opção 2: Mudar para Claude Code Depois

Se você já tem GAC configurado com outro provedor e quer mudar para Claude Code:

```bash
gac model
```

Então:

1. Selecione "Claude Code" da lista de provedores
2. Seu navegador abrirá automaticamente para autenticação OAuth
3. Token salvo em `~/.gac.env`
4. Modelo configurado automaticamente

### Usar GAC Normalmente

Uma vez autenticado, use GAC como de costume:

```bash
# Prepare suas mudanças
git add .

# Gere e faça commit com Claude Code
gac

# Ou sobrescreva o modelo para um único commit
gac -m claude-code:claude-sonnet-4-5
```

## Modelos Disponíveis

Claude Code fornece acesso aos mesmos modelos que a API Anthropic. Os modelos atuais da família Claude 4.5 incluem:

- `claude-sonnet-4-5` - Modelo Sonnet mais recente e inteligente, melhor para codificação
- `claude-haiku-4-5` - Rápido e eficiente
- `claude-opus-4-1` - Modelo mais capaz para raciocínio complexo

Consulte a [documentação do Claude](https://docs.claude.com/en/docs/about-claude/models/overview) para a lista completa de modelos disponíveis.

## Solução de Problemas

### Token Expirado

Se você vir erros de autenticação, seu token pode ter expirado. Reautentique-se executando:

```bash
gac auth
```

Seu navegador abrirá automaticamente para uma nova autenticação OAuth. Alternativamente, você pode executar `gac model`, selecionar "Claude Code" e escolher "Reautenticar (obter novo token)".

### "CLAUDE_CODE_ACCESS_TOKEN não encontrado"

Isso significa que GAC não consegue encontrar seu token de acesso. Autentique-se executando:

```bash
gac model
```

Então selecione "Claude Code" da lista de provedores. O fluxo OAuth começará automaticamente.

### "Autenticação falhou"

Se a autenticação OAuth falhar:

1. Certifique-se de ter uma assinatura Claude Code ativa
2. Verifique se seu navegador abre corretamente
3. Tente um navegador diferente se os problemas persistirem
4. Verifique a conectividade de rede com `claude.ai`
5. Verifique se as portas 8765-8795 estão disponíveis para o servidor de callback local

## Diferenças do Provedor Anthropic

| Recurso                 | Anthropic (`anthropic:`)        | Claude Code (`claude-code:`)                                   |
| ----------------------- | ------------------------------- | -------------------------------------------------------------- |
| Autenticação            | Chave API (`ANTHROPIC_API_KEY`) | OAuth (fluxo automático do navegador)                          |
| Cobrança                | Cobrança API por token          | Baseada em assinatura                                          |
| Configuração            | Entrada manual de chave API     | OAuth automático via `gac init` ou `gac model`                 |
| Gerenciamento de Tokens | Chaves API de longa duração     | Tokens OAuth (podem expirar, fácil reautenticação via `model`) |
| Modelos                 | Mesmos modelos                  | Mesmos modelos                                                 |

## Notas de Segurança

- **Nunca faça commit do seu token de acesso** no controle de versão
- GAC armazena automaticamente tokens em `~/.gac.env` (fora do seu diretório de projeto)
- Tokens podem expirar e requererão reautenticação via `gac model`
- O fluxo OAuth usa PKCE (Proof Key for Code Exchange) para segurança aprimorada
- O servidor de callback local roda apenas em localhost (portas 8765-8795)

## Veja Também

- [Documentação Principal](USAGE.md)
- [Guia de Solução de Problemas](TROUBLESHOOTING.md)
- [Documentação Claude Code](https://claude.ai/code)
