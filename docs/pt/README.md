<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

# 🚀 Git Auto Commit (gac)

[![PyPI version](https://img.shields.io/pypi/v/gac.svg)](https://pypi.org/project/gac/)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/pt/CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](../../README.md) | [简体中文](../zh-CN/README.md) | [繁體中文](../zh-TW/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [हिन्दी](../hi/README.md) | [Tiếng Việt](../vi/README.md) | [Français](../fr/README.md) | [Русский](../ru/README.md) | [Español](../es/README.md) | **Português** | [Norsk](../no/README.md) | [Svenska](../sv/README.md) | [Deutsch](../de/README.md) | [Nederlands](../nl/README.md) | [Italiano](../it/README.md)

**Mensagens de commit alimentadas por LLM que entendem seu código!**

**Automatize seus commits!** Substitua `git commit -m "..."` por `gac` para mensagens de commit contextuais e bem formatadas geradas por modelos de linguagem grandes!

---

## O Que Você Obtém

Mensagens inteligentes e contextuais que explicam o **porquê** por trás de suas alterações:

![GAC gerando uma mensagem de commit contextual](../../assets/gac-simple-usage.pt.png)

---

</div>

<!-- markdownlint-enable MD033 MD036 -->

## Início Rápido

### Use o gac sem instalar

```bash
uvx gac init   # Configure seu provedor, modelo e idioma
uvx gac  # Gere e envie commit com LLM
```

É isso! Revise a mensagem gerada e confirme com `y`.

### Instale e use o gac

```bash
uv tool install gac
gac init
gac
```

### Atualize o gac instalado

```bash
uv tool upgrade gac
```

---

## Recursos Principais

### 🌐 **25+ Provedores Suportados**

- **Anthropic** • **Azure OpenAI** • **Cerebras** • **Chutes.ai** • **Claude Code (OAuth)** • **ChatGPT (OAuth)**
- **DeepSeek** • **Fireworks** • **Gemini** • **Groq** • **Kimi for Coding** • **LM Studio**
- **MiniMax.io** • **Mistral AI** • **Moonshot AI** • **Ollama** • **OpenAI** • **OpenRouter**
- **Qwen Cloud (CN & INTL)** • **Replicate** • **Streamlake** • **Synthetic.new** • **Together AI**
- **Wafer.ai** • **Z.AI** • **Z.AI Coding** • **Custom Endpoints (Anthropic/OpenAI)**

### 🧠 **Análise Inteligente de LLM**

- **Entende a intenção**: Analisa estrutura, lógica e padrões do código para entender o "porquê" por trás de suas alterações, não apenas o que mudou
- **Consciência semântica**: Reconhece refatoração, correções de bugs, funcionalidades e alterações quebrando para gerar mensagens contextualmente apropriadas
- **Filtragem inteligente**: Prioriza alterações significativas enquanto ignora arquivos gerados, dependências e artefatos
- **Agrupamento inteligente de commits** - Agrupa automaticamente alterações relacionadas em múltiplos commits lógicos com `--group`

### 📝 **Múltiplos Formatos de Mensagem**

- **Uma linha** (flag -o): Mensagem de commit de uma única linha seguindo formato de commit convencional
- **Padrão** (padrão): Resumo com pontos de bullet explicando detalhes da implementação
- **Verboso** (flag -v): Explicações abrangentes incluindo motivação, abordagem técnica e análise de impacto
- **Regra 50/72** (bandeira --50-72): Impõe o formato clássico de mensagem de commit para legibilidade ótima no git log e GitHub UI
- **DCO/Signoff** (bandeira --signoff): Adiciona linha Signed-off-by para conformidade com Developer Certificate of Origin (exigido por Cherry Studio, Linux kernel e outros projetos)

### 🌍 **Suporte Multilíngue**

- **25+ idiomas**: Gere mensagens de commit em inglês, chinês, japonês, coreano, espanhol, francês, alemão e mais de 20 idiomas
- **Tradução flexível**: Escolha manter prefixos de commit convencionais em inglês para compatibilidade de ferramentas, ou traduza-os completamente
- **Múltiplos workflows**: Defina um idioma padrão com `gac language`, ou use a flag `-l <idioma>` para substituições únicas
- **Suporte a script nativo**: Suporte completo para scripts não-latinos incluindo CJK, cirílico, tailandês e mais

### 💻 **Experiência do Desenvolvedor**

- **Feedback interativo**: Digite `r` para rerolar, `e` para editar (TUI in-place por padrão, ou `$GAC_EDITOR` se definido), ou digite diretamente seu feedback como `make it shorter` ou `focus on the bug fix`
- **Questionamento interativo**: Use `--interactive` (`-i`) para responder a perguntas direcionadas sobre suas alterações para mensagens de commit mais contextuais
- **Workflows de um comando**: Workflows completos com flags como `gac -ayp` (adicionar tudo, auto-confirmar, push)
- **Integração Git**: Respeita hooks pre-commit e lefthook, executando-os antes de operações LLM caras
- **Servidor MCP**: Execute `gac serve` para expor ferramentas de commit para agentes de IA através do [Model Context Protocol](https://modelcontextprotocol.io/)

### 📊 **Estatísticas de Uso**

- **Acompanhe seus gacs**: Veja quantos commits você fez com gac, sua sequência atual, pico de atividade diária/semanal e projetos principais
- **Rastreamento de tokens**: Tokens de prompt e completion totais por dia, semana, projeto e modelo — com troféus de recorde para uso de tokens também
- **Modelos principais**: Veja quais modelos você mais usa e quantos tokens cada um consome
- **Estatísticas por projeto**: Veja as estatísticas do repositório atual com `gac stats project`
- **Celebrações de recordes**: 🏆 troféus quando você estabelece novos recordes diários, semanais, de tokens ou de sequência; 🥈 por empatá-los
- **Opt-in durante a configuração**: `gac init` pergunta se você deseja ativar as estatísticas e explica exatamente o que é armazenado
- **Opt-out a qualquer momento**: Defina `GAC_DISABLE_STATS=true` (ou `1`/`yes`/`on`) para desativar. Definir como `false`/`0`/`no` (ou não definir) mantém as estatísticas ativadas
- **Privacidade em primeiro lugar**: Armazenado localmente em `~/.gac_stats.json`. Apenas contagens, datas, nomes de projetos e nomes de modelos — sem mensagens de commit, código ou dados pessoais. Sem telemetria

### 🛡️ **Segurança Integrada**

- **Detecção automática de segredos**: Examina em busca de chaves API, senhas e tokens antes de commitar
- **Proteção interativa**: Solicita antes de cometer dados potencialmente sensíveis com claras opções de remediação
- **Filtragem inteligente**: Ignora arquivos de exemplo, arquivos de template e texto placeholder para reduzir falsos positivos

---

## Exemplos de Uso

### Workflow Básico

```bash
# Prepare suas alterações
git add .

# Gere e envie commit com LLM
gac

# Revise → y (commit) | n (cancelar) | r (rerolar) | e (editar) | ou digite feedback
```

### Comandos Comuns

| Comando         | Descrição                                                             |
| --------------- | --------------------------------------------------------------------- |
| `gac`           | Gerar mensagem de commit                                              |
| `gac -y`        | Auto-confirmar (sem necessidade de revisão)                           |
| `gac -a`        | Adicionar tudo antes de gerar mensagem de commit                      |
| `gac -o`        | Mensagem de uma linha para alterações triviais                        |
| `gac -v`        | Formato verboso com Motivação, Abordagem Técnica e Análise de Impacto |
| `gac -h "hint"` | Adicionar contexto para LLM (ex: `gac -h "bug fix"`)                  |
| `gac -s`        | Incluir escopo (ex: feat(auth):)                                      |
| `gac -i`        | Fazer perguntas sobre alterações para melhor contexto                 |
| `gac -g`        | Agrupar alterações em múltiplos commits lógicos                       |
| `gac -p`        | Fazer commit e push                                                   |
| `gac stats`     | Veja suas estatísticas de uso do gac                                  |

### Exemplos para Usuários Avançados

```bash
# Workflow completo em um comando
# Veja suas estatísticas de commits
gac stats

# Estatísticas do projeto atual apenas
gac stats project

gac -ayp -h "preparação de release"

# Explicação detalhada com escopo
gac -v -s

# Mensagem rápida de uma linha para pequenas alterações
gac -o

# Agrupe alterações em commits logicamente relacionados
gac -ag

# Modo interativo com saída detalhada para explicações detalhadas
gac -iv

# Debugue o que o LLM vê
gac --show-prompt

# Pule verificação de segurança (use com cuidado)
gac --skip-secret-scan

# Adicionar signoff para conformidade DCO (Cherry Studio, Linux kernel, etc.)
gac --signoff
```

### Sistema de Feedback Interativo

Não satisfeito com o resultado? Você tem várias opções:

```bash
# Reroll simples (sem feedback)
r

# Edite a mensagem de commit
e
# Por padrão: TUI in-place com keybindings vi/emacs
# Pressione Esc+Enter ou Ctrl+S para enviar, Ctrl+C para cancelar

# Defina GAC_EDITOR para abrir o seu editor preferido:
# GAC_EDITOR=code gac → abre VS Code (--wait aplicado automaticamente)
# GAC_EDITOR=vim gac → abre vim
# GAC_EDITOR=nano gac → abre nano

# Ou simplesmente digite seu feedback diretamente!
make it shorter and focus on the performance improvement
use conventional commit format with scope
explain the security implications

# Pressione Enter em entrada vazia para ver o prompt novamente
```

O recurso de edição (`e`) permite refinar a mensagem de commit:

- **Por padrão (TUI in-place)**: Edição multi-linha com keybindings vi/emacs — corrigir erros de digitação, ajustar redação, reestruturar
- **Com `GAC_EDITOR`**: Abre o seu editor preferido (`code`, `vim`, `nano`, etc.) — poder total do editor incluindo localizar/substituir, macros, etc.

Editores GUI como VS Code são tratados automaticamente: gac insere `--wait` para que o processo bloqueie até você fechar a aba do editor. Nenhuma configuração extra necessária.

---

## Configuração

Execute `gac init` para configurar seu provedor interativamente, ou defina variáveis de ambiente:

Precisa mudar provedores ou modelos depois sem tocar nas configurações de idioma? Use `gac model` para um fluxo simplificado que pula os prompts de idioma.

```bash
# Exemplo de configuração
GAC_MODEL=anthropic:your-model-name
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Veja `.gac.env.example` para todas as opções disponíveis.

**Quer mensagens de commit em outro idioma?** Execute `gac language` para selecionar entre 25+ idiomas incluindo Español, Français, 日本語, e mais.

**Quer personalizar o estilo da mensagem de commit?** Veja [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/pt/CUSTOM_SYSTEM_PROMPTS.md) para orientação sobre como escrever prompts de sistema personalizados.

---

## Obtendo Ajuda

- **Documentação completa**: [USAGE.md](docs/pt/USAGE.md) - Referência completa da CLI
- **Servidor MCP**: [docs/MCP.md](MCP.md) - Use o GAC como servidor MCP para agentes de IA
- **Claude Code OAuth**: [docs/CLAUDE_CODE.md](docs/pt/CLAUDE_CODE.md) - Configuração e autenticação do Claude Code
- **ChatGPT OAuth**: [docs/CHATGPT_OAUTH.md](docs/pt/CHATGPT_OAUTH.md) - Configuração e autenticação do ChatGPT OAuth
- **Prompts personalizados**: [CUSTOM_SYSTEM_PROMPTS.md](docs/pt/CUSTOM_SYSTEM_PROMPTS.md) - Personalize o estilo da mensagem de commit
- **Estatísticas de uso**: Veja `gac stats --help` ou a [documentação completa](docs/pt/USAGE.md#estatísticas-de-uso)
- **Solução de problemas**: [TROUBLESHOOTING.md](docs/pt/TROUBLESHOOTING.md) - Problemas comuns e soluções
- **Contribuindo**: [CONTRIBUTING.md](docs/pt/CONTRIBUTING.md) - Configuração de desenvolvimento e diretrizes

---

<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

[⭐ Nos dê uma estrela no GitHub](https://github.com/cellwebb/gac) • [🐛 Reporte problemas](https://github.com/cellwebb/gac/issues) • [📖 Documentação completa](docs/pt/USAGE.md)

</div>

<!-- markdownlint-enable MD033 MD036 -->
