# Uso da Linha de Comando gac

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | **Português** | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

Este documento descreve todas as flags e opções disponíveis para a ferramenta CLI `gac`.

## Índice

- [Uso da Linha de Comando gac](#uso-da-linha-de-comando-gac)
  - [Índice](#índice)
  - [Uso Básico](#uso-básico)
  - [Flags Principais do Fluxo de Trabalho](#flags-principais-do-fluxo-de-trabalho)
  - [Personalização de Mensagens](#personalização-de-mensagens)
  - [Saída e Verbosity](#saída-e-verbosity)
  - [Ajuda e Versão](#ajuda-e-versão)
  - [Exemplos de Fluxos de Trabalho](#exemplos-de-fluxos-de-trabalho)
  - [Avançado](#avançado)
    - [Integração com scripts e processamento externo](#integração-com-scripts-e-processamento-externo)
    - [Ignorando Hooks Pre-commit e Lefthook](#ignorando-hooks-pre-commit-e-lefthook)
    - [Varredura de Segurança](#varredura-de-segurança)
    - [Verificação de Certificado SSL](#verificação-de-certificado-ssl)
  - [Notas de Configuração](#notas-de-configuração)
    - [Opções Avançadas de Configuração](#opções-avançadas-de-configuração)
    - [Subcomandos de Configuração](#subcomandos-de-configuração)
  - [Modo Interativo](#modo-interativo)
    - [Como Funciona](#como-funciona)
    - [Quando Usar o Modo Interativo](#quando-usar-o-modo-interativo)
    - [Exemplos de Uso](#exemplos-de-uso)
    - [Fluxo de Perguntas e Respostas](#fluxo-de-perguntas-e-respostas)
    - [Combinação com Outras Flags](#combinação-com-outras-flags)
    - [Melhores Práticas](#melhores-práticas)
  - [Obtendo Ajuda](#obtendo-ajuda)

## Uso Básico

```sh
gac init
# Depois siga os prompts para configurar seu provider, modelo e chaves de API interativamente
gac
```

Gera uma mensagem de commit alimentada por LLM para alterações em stage e solicita confirmação. O prompt de confirmação aceita:

- `y` ou `yes` - Prosseguir com o commit
- `n` ou `no` - Cancelar o commit
- `r` ou `reroll` - Regenerar a mensagem de commit com o mesmo contexto
- `e` ou `edit` - Editar a mensagem de commit in-place com edição rica no terminal (keybindings vi/emacs)
- Qualquer outro texto - Regenerar com esse texto como feedback (ex: `make it shorter`, `focus on performance`)
- Entrada vazia (apenas Enter) - Mostrar o prompt novamente

---

## Flags Principais do Fluxo de Trabalho

| Flag / Opção         | Short | Descrição                                                               |
| -------------------- | ----- | ----------------------------------------------------------------------- |
| `--add-all`          | `-a`  | Fazer stage de todas as alterações antes do commit                      |
| `--group`            | `-g`  | Agrupar alterações em stage em múltiplos commits lógicos                |
| `--push`             | `-p`  | Push das alterações para o remoto após o commit                         |
| `--yes`              | `-y`  | Confirmar commit automaticamente sem prompting                          |
| `--dry-run`          |       | Mostrar o que aconteceria sem fazer nenhuma alteração                   |
| `--message-only`     |       | Exibir apenas a mensagem de commit gerada sem realizar o commit         |
| `--no-verify`        |       | Ignorar hooks pre-commit e lefthook ao fazer commit                     |
| `--skip-secret-scan` |       | Ignorar varredura de segurança para segredos nas alterações em stage    |
| `--no-verify-ssl`    |       | Ignorar verificação de certificado SSL (útil para proxies corporativos) |
| `--interactive`      | `-i`  | Fazer perguntas sobre as alterações para melhores commits               |

**Nota:** Combine `-a` e `-g` (ou seja, `-ag`) para fazer stage de TODAS as alterações primeiro, depois agrupá-las em commits.

**Nota:** Ao usar `--group`, o limite máximo de tokens de saída é escalado automaticamente com base no número de arquivos sendo commitados (2x para 1-9 arquivos, 3x para 10-19 arquivos, 4x para 20-29 arquivos, 5x para 30+ arquivos). Isso garante que o LLM tenha tokens suficientes para gerar todos os commits agrupados sem truncamento, mesmo para grandes conjuntos de alterações.

**Nota:** `--message-only` e `--group` são mutuamente excludentes. Use `--message-only` quando quiser obter a mensagem de commit para processamento externo, e `--group` quando quiser organizar múltiplos commits dentro do fluxo de trabalho git atual.

**Nota:** A flag `--interactive` fornece contexto adicional ao LLM ao fazer perguntas sobre suas alterações, resultando em mensagens de commit mais precisas e detalhadas. Isso é especialmente útil para alterações complexas ou quando você quer garantir que a mensagem de commit capture o contexto completo do seu trabalho.

## Personalização de Mensagens

| Flag / Opção        | Short | Descrição                                                                 |
| ------------------- | ----- | ------------------------------------------------------------------------- |
| `--one-liner`       | `-o`  | Gerar uma mensagem de commit de única linha                               |
| `--verbose`         | `-v`  | Gerar mensagens de commit detalhadas com motivação, arquitetura e impacto |
| `--hint <text>`     | `-h`  | Adicionar uma dica para guiar o LLM                                       |
| `--model <model>`   | `-m`  | Especificar o modelo para usar para este commit                           |
| `--language <lang>` | `-l`  | Sobrescrever o idioma (nome ou código: 'Spanish', 'es', 'zh-CN', 'ja')    |
| `--scope`           | `-s`  | Inferir um escopo apropriado para o commit                                |

**Nota:** Você pode fornecer feedback interativamente simplesmente digitando-o no prompt de confirmação - não há necessidade de prefixar com 'r'. Digite `r` para um reroll simples, `e` para editar in-place com keybindings vi/emacs, ou digite seu feedback diretamente como `torne mais curto`.

## Saída e Verbosity

| Flag / Opção          | Short | Descrição                                                         |
| --------------------- | ----- | ----------------------------------------------------------------- |
| `--quiet`             | `-q`  | Suprimir toda saída exceto erros                                  |
| `--log-level <level>` |       | Definir nível de log (debug, info, warning, error)                |
| `--show-prompt`       |       | Imprimir o prompt do LLM usado para geração de mensagem de commit |

## Ajuda e Versão

| Flag / Opção | Short | Descrição                        |
| ------------ | ----- | -------------------------------- |
| `--version`  |       | Mostrar versão do gac e sair     |
| `--help`     |       | Mostrar mensagem de ajuda e sair |

---

## Exemplos de Fluxos de Trabalho

- **Fazer stage de todas as alterações e commit:**

  ```sh
  gac -a
  ```

- **Commit e push em um passo:**

  ```sh
  gac -ap
  ```

- **Gerar uma mensagem de commit de única linha:**

  ```sh
  gac -o
  ```

- **Gerar uma mensagem de commit detalhada com seções estruturadas:**

  ```sh
  gac -v
  ```

- **Adicionar uma dica para o LLM:**

  ```sh
  gac -h "Refactor authentication logic"
  ```

- **Inferir escopo para o commit:**

  ```sh
  gac -s
  ```

- **Agrupar alterações em stage em commits lógicos:**

  ```sh
  gac -g
  # Agrupa apenas os arquivos que você já fez stage
  ```

- **Agrupar todas as alterações (em stage + não em stage) e auto-confirmar:**

  ```sh
  gac -agy
  # Faz stage de tudo, agrupa e auto-confirma
  ```

- **Usar um modelo específico apenas para este commit:**

  ```sh
  gac -m anthropic:claude-haiku-4-5
  ```

- **Gerar mensagem de commit em um idioma específico:**

  ```sh
  # Usando códigos de idioma (mais curto)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # Usando nomes completos
  gac -l "Simplified Chinese"
  gac -l Japanese
  gac -l Spanish
  ```

- **Dry run (ver o que aconteceria):**

  ```sh
  gac --dry-run
  ```

- **Obter apenas a mensagem de commit (para integração com scripts):**

  ```sh
  gac --message-only
  # Saída: feat: add user authentication system
  ```

- **Obter a mensagem de commit em formato de linha única:**

  ```sh
  gac --message-only --one-liner
  # Saída: feat: add user authentication system
  ```

- **Usar modo interativo para fornecer contexto:**

  ```sh
  gac -i
  # Qual é o propósito principal dessas alterações?
  # Qual problema você está resolvendo?
  # Há detalhes de implementação para mencionar?
  ```

- **Modo interativo com saída detalhada:**

  ```sh
  gac -i -v
  # Fazer perguntas e gerar mensagens de commit detalhadas
  ```

## Avançado

- Combine flags para fluxos de trabalho mais poderosos (ex: `gac -ayp` para fazer stage, auto-confirmar e push)
- Use `--show-prompt` para debugar ou revisar o prompt enviado ao LLM
- Ajuste a verbosity com `--log-level` ou `--quiet`
- Use `--message-only` para integração com scripts e workflows automatizados

### Integração com scripts e processamento externo

A flag `--message-only` foi projetada para integração com scripts e workflows de ferramentas externas. Ela exibe apenas a mensagem de commit bruta, sem formatação adicional, spinners ou elementos extras de UI.

**Casos de uso:**

- **Integração com agentes:** Permitir que agentes de IA obtenham mensagens de commit e gerenciem os commits por conta própria
- **VCS alternativos:** Usar mensagens geradas com outros sistemas de controle de versão (Mercurial, Jujutsu, etc.)
- **Workflows de commit personalizados:** Processar ou modificar a mensagem antes de fazer o commit
- **Pipelines de CI/CD:** Extrair mensagens de commit para processos automatizados

**Exemplo de uso em script:**

```sh
#!/bin/bash
# Obter a mensagem de commit e usá-la com uma função de commit personalizada
MESSAGE=$(gac --message-only --add-all --yes)
git commit -m "$MESSAGE"
```

```python
# Exemplo de integração em Python
import subprocess


def get_commit_message() -> str:
    result = subprocess.run(
        ["gac", "--message-only", "--yes"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


message = get_commit_message()
print(f"Generated message: {message}")
```

**Principais características para uso em scripts:**

- Saída limpa, sem formatação Rich ou spinners
- Ignora automaticamente os prompts de confirmação
- Nenhum commit real é feito no git
- Funciona com `--one-liner` para saída simplificada
- Pode ser combinada com outras flags como `--hint`, `--model`, etc.

### Ignorando Hooks Pre-commit e Lefthook

A flag `--no-verify` permite ignorar quaisquer hooks pre-commit ou lefthook configurados no seu projeto:

```sh
gac --no-verify  # Ignorar todos os hooks pre-commit e lefthook
```

**Use `--no-verify` quando:**

- Hooks pre-commit ou lefthook estiverem falhando temporariamente
- Trabalhando com hooks demorados
- Fazendo commit de código em andamento que ainda não passa em todas as verificações

**Nota:** Use com cautela, pois esses hooks mantêm padrões de qualidade de código.

### Varredura de Segurança

gac inclui varredura de segurança integrada que detecta automaticamente segredos potenciais e chaves de API nas suas alterações em stage antes do commit. Isso ajuda a prevenir o commit acidental de informações sensíveis.

**Ignorando varreduras de segurança:**

```sh
gac --skip-secret-scan  # Ignorar varredura de segurança para este commit
```

**Para desativar permanentemente:** Defina `GAC_SKIP_SECRET_SCAN=true` no seu arquivo `.gac.env`.

**Quando ignorar:**

- Fazer commit de código de exemplo com chaves placeholder
- Trabalhando com fixtures de teste que contêm credenciais falsas
- Quando você verificou que as alterações são seguras

**Nota:** O varredor usa correspondência de padrões para detectar formatos comuns de segredos. Sempre revise suas alterações em stage antes do commit.

### Verificação de Certificado SSL

O flag `--no-verify-ssl` permite ignorar a verificação de certificado SSL para chamadas de API:

```sh
gac --no-verify-ssl  # Ignorar verificação SSL para este commit
```

**Para configurar permanentemente:** Defina `GAC_NO_VERIFY_SSL=true` no seu arquivo `.gac.env`.

**Use `--no-verify-ssl` quando:**

- Proxies corporativos interceptam tráfego SSL (proxies MITM)
- Ambientes de desenvolvimento usam certificados auto-assinados
- Você encontra erros de certificado SSL devido a configurações de segurança de rede

**Nota:** Use esta opção apenas em ambientes de rede confiáveis. Desativar a verificação SSL reduz a segurança e pode tornar suas solicitações de API vulneráveis a ataques man-in-the-middle.

## Notas de Configuração

- A maneira recomendada de configurar o gac é executar `gac init` e seguir os prompts interativos.
- Já configurou o idioma e só precisa mudar de provider ou modelo? Execute `gac model` para repetir a configuração sem perguntas de idioma.
- **Usando Claude Code?** Consulte o [guia de configuração do Claude Code](CLAUDE_CODE.md) para instruções de autenticação OAuth.
- **Usando Qwen.ai?** Consulte o [guia de configuração do Qwen.ai](QWEN.md) para obter instruções de autenticação OAuth.
- gac carrega configuração na seguinte ordem de precedência:
  1. Flags da CLI
  2. Variáveis de ambiente
  3. Nível de projeto `.gac.env`
  4. Nível de usuário `~/.gac.env`

### Opções Avançadas de Configuração

Você pode personalizar o comportamento do gac com estas variáveis de ambiente opcionais:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Inferir e incluir automaticamente escopo nas mensagens de commit (ex: `feat(auth):` vs `feat:`)
- `GAC_VERBOSE=true` - Gerar mensagens de commit detalhadas com seções de motivação, arquitetura e impacto
- `GAC_TEMPERATURE=0.7` - Controlar criatividade do LLM (0.0-1.0, menor = mais focado)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Máximo de tokens para mensagens geradas (automaticamente escalado 2-5x ao usar `--group` com base no número de arquivos; substitua para ir mais alto ou mais baixo)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Avisar quando prompts excederem esta contagem de tokens
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Usar um prompt de sistema personalizado para geração de mensagem de commit
- `GAC_LANGUAGE=Spanish` - Gerar mensagens de commit em um idioma específico (ex: Spanish, French, Japanese, German). Suporta nomes completos ou códigos ISO (es, fr, ja, de, zh-CN). Use `gac language` para seleção interativa
- `GAC_TRANSLATE_PREFIXES=true` - Traduzir prefixos de commit convencionais (feat, fix, etc.) para o idioma alvo (padrão: false, mantém prefixos em inglês)
- `GAC_SKIP_SECRET_SCAN=true` - Desativar varredura de segurança automática para segredos nas alterações em stage (use com cautela)
- `GAC_NO_VERIFY_SSL=true` - Ignorar verificação de certificado SSL para chamadas de API (útil para proxies corporativos que interceptam tráfego SSL)
- `GAC_NO_TIKTOKEN=true` - Permanecer completamente offline ignorando a etapa de download do `tiktoken` e usando o estimador de tokens aproximado integrado

Veja `.gac.env.example` para um modelo de configuração completo.

Para orientação detalhada sobre criação de prompts de sistema personalizados, veja [docs/CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md).

### Subcomandos de Configuração

Os seguintes subcomandos estão disponíveis:

- `gac init` — Assistente de configuração interativo para provedor, modelo e idioma
- `gac model` — Configuração de provedor/modelo/chave API sem prompts de idioma (ideal para mudanças rápidas)
- `gac auth` — Mostrar status de autenticação OAuth para todos os provedores
- `gac auth claude-code login` — Login no Claude Code usando OAuth (abre navegador)
- `gac auth claude-code logout` — Logout do Claude Code e remover token armazenado
- `gac auth claude-code status` — Verificar status de autenticação do Claude Code
- `gac auth qwen login` — Login no Qwen usando fluxo de dispositivo OAuth (abre navegador)
- `gac auth qwen logout` — Logout do Qwen e remover token armazenado
- `gac auth qwen status` — Verificar status de autenticação do Qwen
- `gac config show` — Mostrar configuração atual
- `gac config set KEY VALUE` — Definir chave de configuração em `$HOME/.gac.env`
- `gac config get KEY` — Obter valor de configuração
- `gac config unset KEY` — Remover chave de configuração de `$HOME/.gac.env`
- `gac language` (ou `gac lang`) — Seletor de idioma interativo para mensagens de commit (define GAC_LANGUAGE)
- `gac diff` — Mostrar git diff filtrado com opções para mudanças preparadas/não preparadas, cor e truncamento

## Modo Interativo

A flag `--interactive` (`-i`) melhora a geração de mensagens de commit do gac ao fazer perguntas direcionadas sobre suas alterações. Este contexto adicional ajuda o LLM a criar mensagens de commit mais precisas, detalhadas e contextualmente apropriadas.

### Como Funciona

Quando você usa `--interactive`, o gac fará perguntas como:

- **Qual é o propósito principal dessas alterações?** - Ajuda a entender o objetivo de alto nível
- **Qual problema você está resolvendo?** - Fornece contexto sobre a motivação
- **Há detalhes de implementação para mencionar?** - Captura especificações técnicas
- **Há breaking changes?** - Identifica potenciais problemas de impacto
- **Isso está relacionado a alguma issue ou ticket?** - Conecta ao gerenciamento de projetos

### Quando Usar o Modo Interativo

O modo interativo é especialmente útil para:

- **Alterações complexas** onde o contexto não é claro apenas pelo diff
- **Trabalho de refactoring** que se estende por múltiplos arquivos e conceitos
- **Novas funcionalidades** que exigem explicação do propósito geral
- **Correções de bugs** onde a causa raiz não é imediatamente visível
- **Otimização de performance** onde a lógica não é óbvia
- **Preparação para code review** - as perguntas ajudam você a pensar sobre suas alterações

### Exemplos de Uso

**Modo interativo básico:**

```sh
gac -i
```

Isso fará:

1. Mostrar um resumo das alterações em stage
2. Fazer perguntas sobre as alterações
3. Gerar uma mensagem de commit com suas respostas
4. Pedir confirmação (ou confirmar automaticamente quando combinado com `-y`)

**Modo interativo com alterações em stage:**

```sh
gac -ai
# Fazer stage de todas as alterações, depois fazer perguntas para melhor contexto
```

**Modo interativo com hints específicos:**

```sh
gac -i -h "Migração de banco de dados para perfis de usuário"
# Fazer perguntas enquanto fornece um hint específico para focar o LLM
```

**Modo interativo com saída detalhada:**

```sh
gac -i -v
# Fazer perguntas e gerar uma mensagem de commit detalhada e estruturada
```

**Modo interativo com confirmação automática:**

```sh
gac -i -y
# Fazer perguntas mas confirmar o commit resultante automaticamente
```

### Fluxo de Perguntas e Respostas

O workflow interativo segue este padrão:

1. **Revisão das alterações** - gac mostra um resumo do que você está cometendo
2. **Responder perguntas** - responda a cada prompt com detalhes relevantes
3. **Melhoria do contexto** - suas respostas são adicionadas ao prompt do LLM
4. **Geração da mensagem** - o LLM cria uma mensagem de commit com contexto completo
5. **Confirmação** - revise e confirme o commit (ou automaticamente com `-y`)

**Dicas para respostas úteis:**

- **Conciso mas completo** - forneça detalhes importantes sem ser excessivamente verboso
- **Foque no "porquê"** - explique o raciocínio por trás de suas alterações
- **Mencione limitações** - note limitações ou considerações especiais
- **Conecte ao contexto externo** - referencie issues, documentação ou documentos de design
- **Respostas vazias são ok** - se uma pergunta não se aplica, apenas pressione Enter

### Combinação com Outras Flags

O modo interativo funciona bem com a maioria das outras flags:

```sh
# Fazer stage de todas as alterações e fazer perguntas
gac -ai

# Fazer perguntas com saída detalhada
gac -i -v
```

### Melhores Práticas

- **Use para PRs complexos** - especialmente útil para pull requests que precisam de explicações detalhadas
- **Colaboração em equipe** - as perguntas ajudam você a pensar sobre alterações que outros revisarão
- **Preparação de documentação** - suas respostas podem ajudar a formar a base para release notes
- **Ferramenta de aprendizado** - as perguntas reforçam boas práticas de mensagens de commit
- **Pule para alterações simples** - para correções triviais, o modo básico pode ser mais rápido

## Obtendo Ajuda

- Para prompts de sistema personalizados, veja [docs/CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)
- Para solução de problemas e dicas avançadas, veja [docs/TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- Para instalação e configuração, veja [README.md#installation-and-configuration](../README.md#installation-and-configuration)
- Para contribuir, veja [docs/CONTRIBUTING.md](../CONTRIBUTING.md)
- Informações de licença: [LICENSE](../LICENSE)
