# Usando o GAC como Servidor MCP

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | **Português** | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

O GAC pode ser executado como um servidor do [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), permitindo que agentes de IA e editores gerem commits através de chamadas de ferramentas estruturadas em vez de comandos de shell.

## Índice

- [Usando o GAC como Servidor MCP](#usando-o-gac-como-servidor-mcp)
  - [Índice](#índice)
  - [O que é MCP?](#o-que-é-mcp)
  - [Benefícios](#benefícios)
  - [Configuração](#configuração)
    - [Claude Code](#claude-code)
    - [Claude Desktop](#claude-desktop)
    - [Cursor](#cursor)
    - [Outros Clientes MCP](#outros-clientes-mcp)
  - [Ferramentas Disponíveis](#ferramentas-disponíveis)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Fluxos de Trabalho](#fluxos-de-trabalho)
    - [Commit Básico](#commit-básico)
    - [Pré-visualizar Antes de Fazer Commit](#pré-visualizar-antes-de-fazer-commit)
    - [Commits Agrupados](#commits-agrupados)
    - [Commit com Contexto](#commit-com-contexto)
  - [Configuração do Servidor](#configuração-do-servidor)
  - [Solução de Problemas](#solução-de-problemas)
  - [Ver Também](#ver-também)

## O que é MCP?

O Model Context Protocol é um padrão aberto que permite que aplicações de IA chamem ferramentas externas através de uma interface estruturada. Ao executar o GAC como um servidor MCP, qualquer cliente compatível com MCP pode inspecionar o estado do repositório e criar commits alimentados por IA sem invocar comandos de shell diretamente.

## Benefícios

- **Interação estruturada**: Agentes chamam ferramentas tipadas com parâmetros validados em vez de analisar a saída do shell
- **Fluxo de trabalho de duas ferramentas**: `gac_status` para inspecionar, `gac_commit` para agir — um ajuste natural para o raciocínio de agentes
- **Capacidades completas do GAC**: Mensagens de commit com IA, commits agrupados, varredura de segredos e push — tudo disponível através do MCP
- **Sem configuração adicional**: O servidor usa sua configuração existente do GAC (`~/.gac.env`, configurações de provedores, etc.)

## Configuração

O servidor MCP é iniciado com `gac serve` e se comunica via stdio, o transporte padrão do MCP.

### Claude Code

Adicione ao `.mcp.json` do seu projeto ou ao `~/.claude/claude_code_config.json` global:

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

Ou se você tem o GAC instalado globalmente:

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

### Claude Desktop

Adicione ao seu arquivo de configuração do Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json` no macOS, `%APPDATA%\Claude\claude_desktop_config.json` no Windows):

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

### Cursor

Adicione às configurações MCP do Cursor (`.cursor/mcp.json`):

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

### Outros Clientes MCP

Qualquer cliente compatível com MCP pode usar o GAC. O ponto de entrada do servidor é:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

Se você tem o GAC instalado (via `uv tool install gac`), pode usar `gac` diretamente em vez de `uvx gac`.

## Ferramentas Disponíveis

O servidor expõe duas ferramentas:

### gac_status

Inspeciona o estado do repositório. Use antes de fazer commit para entender o que será commitado.

**Parâmetros:**

| Parameter           | Type                                    | Default     | Descrição                                        |
| ------------------- | --------------------------------------- | ----------- | ------------------------------------------------ |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Formato de saída                                 |
| `include_diff`      | bool                                    | `false`     | Incluir conteúdo completo do diff                |
| `include_stats`     | bool                                    | `true`      | Incluir estatísticas de alterações de linhas     |
| `include_history`   | int                                     | `0`         | Número de commits recentes a incluir             |
| `staged_only`       | bool                                    | `false`     | Mostrar apenas alterações preparadas             |
| `include_untracked` | bool                                    | `true`      | Incluir arquivos não rastreados                  |
| `max_diff_lines`    | int                                     | `500`       | Limitar tamanho da saída do diff (0 = ilimitado) |

**Retorna:** Nome da branch, status dos arquivos (preparados/não preparados/não rastreados/conflitos), conteúdo opcional do diff, estatísticas opcionais e histórico opcional de commits.

### gac_commit

Gera uma mensagem de commit alimentada por IA e opcionalmente executa o commit.

**Parâmetros:**

| Parameter          | Type           | Default | Descrição                                                      |
| ------------------ | -------------- | ------- | -------------------------------------------------------------- |
| `stage_all`        | bool           | `false` | Preparar todas as alterações antes de commitar (`git add -A`)  |
| `files`            | list[str]      | `[]`    | Arquivos específicos para preparar                             |
| `dry_run`          | bool           | `false` | Pré-visualizar sem executar                                    |
| `message_only`     | bool           | `false` | Gerar mensagem sem fazer commit                                |
| `push`             | bool           | `false` | Fazer push para o remoto após o commit                         |
| `group`            | bool           | `false` | Dividir alterações em múltiplos commits lógicos                |
| `one_liner`        | bool           | `false` | Mensagem de commit de uma única linha                          |
| `scope`            | string \| null | `null`  | Scope de commit convencional (auto-detectado se não fornecido) |
| `hint`             | string         | `""`    | Contexto adicional para melhores mensagens                     |
| `model`            | string \| null | `null`  | Sobrescrever modelo de IA (`provider:model_name`)              |
| `language`         | string \| null | `null`  | Sobrescrever idioma da mensagem de commit                      |
| `skip_secret_scan` | bool           | `false` | Pular varredura de segurança                                   |
| `no_verify`        | bool           | `false` | Pular hooks de pre-commit                                      |
| `auto_confirm`     | bool           | `false` | Pular confirmações (obrigatório para agentes)                  |

**Retorna:** Status de sucesso, mensagem de commit gerada, hash do commit (se commitado), lista de arquivos alterados e quaisquer avisos.

## Fluxos de Trabalho

### Commit Básico

```text
1. gac_status()                              → Ver o que mudou
2. gac_commit(stage_all=true, auto_confirm=true)  → Preparar, gerar mensagem e commitar
```

### Pré-visualizar Antes de Fazer Commit

```text
1. gac_status(include_diff=true, include_stats=true)  → Revisar alterações em detalhe
2. gac_commit(stage_all=true, dry_run=true)            → Pré-visualizar a mensagem de commit
3. gac_commit(stage_all=true, auto_confirm=true)       → Executar o commit
```

### Commits Agrupados

```text
1. gac_status()                                           → Ver todas as alterações
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Pré-visualizar agrupamentos lógicos
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Executar commits agrupados
```

### Commit com Contexto

```text
1. gac_status(include_history=5)  → Ver commits recentes como referência de estilo
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Configuração do Servidor

O servidor MCP usa sua configuração existente do GAC. Nenhuma configuração adicional é necessária além de:

1. **Provedor e modelo**: Execute `gac init` ou `gac model` para configurar seu provedor de IA
2. **Chaves API**: Armazenadas em `~/.gac.env` (configuradas durante `gac init`)
3. **Configurações opcionais**: Todas as variáveis de ambiente do GAC se aplicam (`GAC_LANGUAGE`, `GAC_VERBOSE`, etc.)

Consulte a [documentação principal](USAGE.md#notas-de-configuração) para todas as opções de configuração.

## Solução de Problemas

### "No model configured"

Execute `gac init` para configurar seu provedor de IA e modelo antes de usar o servidor MCP.

### "No staged changes found"

Prepare arquivos manualmente (`git add`) ou use `stage_all=true` na chamada ao `gac_commit`.

### O servidor não inicia

Verifique se o GAC está instalado e acessível:

```bash
uvx gac --version
# ou
gac --version
```

Se estiver usando `uvx`, certifique-se de que `uv` está instalado e no seu PATH.

### O agente não encontra o servidor

Certifique-se de que o arquivo de configuração MCP está na localização correta para o seu cliente e que o caminho do `command` está acessível a partir do seu ambiente de shell.

### Corrupção de saída Rich

O servidor MCP redireciona automaticamente toda a saída do console Rich para stderr para prevenir a corrupção do protocolo stdio. Se você vir saída ilegível, certifique-se de estar executando `gac serve` (não `gac` diretamente) ao usar MCP.

## Ver Também

- [Documentação Principal](USAGE.md)
- [Configuração OAuth do Claude Code](CLAUDE_CODE.md)
- [Configuração OAuth do Qwen.ai](QWEN.md)
- [Guia de Solução de Problemas](TROUBLESHOOTING.md)
- [Especificação MCP](https://modelcontextprotocol.io/)
