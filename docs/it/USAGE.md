# Guida all'Uso di gac

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | **Italiano**

Guida completa all'uso della command line interface di `gac`.

## Sommario

- [Guida all'Uso di gac](#guida-alluso-di-gac)
  - [Sommario](#sommario)
  - [Installazione](#installazione)
    - [Con uvx (consigliato)](#con-uvx-consigliato)
    - [Con pip](#con-pip)
    - [Con strumenti del sistema operativo](#con-strumenti-del-sistema-operativo)
  - [Configurazione Iniziale](#configurazione-iniziale)
    - [Setup Interattivo](#setup-interattivo)
    - [Configurazione Manuale](#configurazione-manuale)
    - [Verifica Configurazione](#verifica-configurazione)
  - [Comandi Base](#comandi-base)
    - [gac](#gac)
    - [gac init](#gac-init)
    - [gac model](#gac-model)
    - [gac language](#gac-language)
  - [Opzioni della Linea di Comando](#opzioni-della-linea-di-comando)
    - [Opzioni di Staging](#opzioni-di-staging)
    - [Opzioni di Formato](#opzioni-di-formato)
    - [Opzioni di Contesto](#opzioni-di-contesto)
    - [Opzioni di Commit](#opzioni-di-commit)
    - [Opzioni di Debug](#opzioni-di-debug)
  - [Workflow Comuni](#workflow-comuni)
    - [Workflow Base](#workflow-base)
    - [Workflow Rapido](#workflow-rapido)
    - [Workflow Dettagliato](#workflow-dettagliato)
    - [Workflow di Gruppo](#workflow-di-gruppo)
  - [Provider AI Supportati](#provider-ai-supportati)
    - [Provider Cloud](#provider-cloud)
    - [Provider Locali](#provider-locali)
    - [Endpoint Personalizzati](#endpoint-personalizzati)
  - [Configurazione Avanzata](#configurazione-avanzata)
    - [Variabili d'Ambiente](#variabili-dambiente)
    - [File di Configurazione](#file-di-configurazione)
    - [Prompt Personalizzati](#prompt-personalizzati)
  - [Integrazione Git](#integrazione-git)
    - [Hook Pre-commit](#hook-pre-commit)
    - [Lefthook](#lefthook)
    - [Configurazione Git](#configurazione-git)
  - [Esempi Pratici](#esempi-pratici)
    - [Sviluppo Frontend](#sviluppo-frontend)
    - [Sviluppo Backend](#sviluppo-backend)
    - [Sviluppo Python](#sviluppo-python)
    - [Correzioni di Bug](#correzioni-di-bug)
  - [Risoluzione Problemi](#risoluzione-problemi)
    - [Problemi Comuni](#problemi-comuni)
    - [Debug](#debug)
  - [Riferimento Comandi](#riferimento-comandi)

## Installazione

### Con uvx (consigliato)

```bash
# Usa gac senza installazione permanente
uvx gac

# Oppure installa come tool
uv tool install gac
```

### Con pip

```bash
pip install gac
```

### Con strumenti del sistema operativo

```bash
# macOS con Homebrew
brew install gac

# Altre piattaforme
pipx install gac
```

## Configurazione Iniziale

### Setup Interattivo

```bash
# Configura provider, modello e lingua
gac init

# Solo provider e modello (salta configurazione lingua)
gac model
```

Il setup interattivo ti guiderà attraverso:

1. Scelta del provider AI
2. Selezione del modello
3. Configurazione della lingua di output
4. Impostazione delle chiavi API

### Configurazione Manuale

```bash
# Imposta provider e modello
export GAC_MODEL="openai:gpt-4"

# Imposta chiave API
export OPENAI_API_KEY="tua-chiave-api"

# Imposta lingua
export GAC_LANGUAGE="it"
```

### Verifica Configurazione

```bash
# Mostra configurazione corrente
gac --show-config

# Verifica connessione API
gac --test-api
```

## Comandi Base

### gac

Genera un messaggio di commit per le modifiche staged.

```bash
# Uso base
gac

# Con opzioni
gac -y -a -s
```

### gac init

Configura gac interattivamente.

```bash
# Setup completo
gac init

# Reconfigura solo provider/modello
gac model
```

### gac model

Cambia rapidamente provider e modello.

```bash
# Cambia provider/modello
gac model

# Elenca provider disponibili
gac --list-providers
```

### gac language

Configura la lingua dei messaggi di commit.

```bash
# Configura lingua
gac language

# Elenca lingue disponibili
gac --list-languages
```

## Opzioni della Linea di Comando

### Opzioni di Staging

#### `-a, --all`

Fai lo staging di tutte le modifiche prima di generare il commit.

```bash
# Equivalente a: git add . && gac
gac -a
```

#### `--interactive`

Seleziona interattivamente quali file fare lo staging.

```bash
# Mostra menu di selezione file
gac --interactive
```

### Opzioni di Formato

#### `-o, --one-liner`

Genera un messaggio di commit su una sola riga.

```bash
# Output: feat(auth): aggiungi OAuth2
gac -o
```

#### `-v, --verbose`

Genera un messaggio dettagliato con sezioni multiple.

```bash
# Output con motivazione, approccio tecnico, impatto
gac -v
```

#### `-s, --scope`

Includi automaticamente lo scope nel commit.

```bash
# Output: feat(api): aggiungi endpoint utenti
gac -s
```

### Opzioni di Contesto

#### `-h, --hint <TEXT>`

Aggiungi contesto o hint per l'AI.

```bash
# Fornisci contesto specifico
gac -h "correggi bug di autenticazione"
gac -h "implementa OAuth2 per Google"
gac -h "ottimizza query database"
```

#### `-l, --language <LANG>`

Sovrascrivi la lingua di output per questo commit.

```bash
# Genera commit in inglese
gac -l en

# Genera commit in italiano
gac -l it
```

#### `--context-lines <N>`

Controlla quante linee di contesto includere nel diff.

```bash
# Più contesto (default: 200)
gac --context-lines 500

# Meno contesto per modifiche mirate
gac --context-lines 50
```

### Opzioni di Commit

#### `-y, --yes`

Conferma automaticamente il commit senza revisione.

```bash
# Salta revisione interattiva
gac -y
```

#### `-p, --push`

Fai il push del commit dopo averlo creato.

```bash
# Commit e push in un comando
gac -p
```

#### `--group`

Raggruppa modifiche correlate in commit multipli.

```bash
# Analizza e crea commit logici multipli
gac --group
```

### Opzioni di Debug

#### `--show-prompt`

Mostra il prompt inviato all'AI senza eseguire il commit.

```bash
# Debug del prompt generato
gac --show-prompt
```

#### `--dry-run`

Mostra cosa sarebbe fatto senza eseguire.

```bash
# Simula senza commit
gac --dry-run
```

#### `--skip-secret-scan`

Salta la scansione di sicurezza per segreti.

```bash
# Usa con cautela
gac --skip-secret-scan
```

## Workflow Comuni

### Workflow Base

```bash
# 1. Fai modifiche ai file
# 2. Fai lo staging
git add .

# 3. Genera commit con AI
gac

# 4. Rivedi e conferma
# y (commit) | n (annulla) | r (rilancia) | e (modifica)
```

### Workflow Rapido

```bash
# Staging tutto, auto-conferma, push
gac -ayp

# One-liner rapido
gac -ao

# Con contesto specifico
gac -ay -h "correggi critico"
```

### Workflow Dettagliato

```bash
# Messaggio dettagliato con scope
gac -vs

# Con hint specifico
gac -v -h "implementa nuova funzionalità"

# Revisione manuale dopo generazione
gac -v  # poi 'e' per modificare se necessario
```

### Workflow di Gruppo

```bash
# Raggruppa modifiche correlate
gac -ag

# Con revisione
gac -ag --interactive

# Push automatico dopo grouping
gac -agp
```

## Provider AI Supportati

### Provider Cloud

| Provider      | Modelli Comuni                  | Variabile Ambiente   |
| ------------- | ------------------------------- | -------------------- |
| OpenAI        | gpt-4, gpt-3.5-turbo            | `OPENAI_API_KEY`     |
| Anthropic     | claude-3-sonnet, claude-3-haiku | `ANTHROPIC_API_KEY`  |
| Google Gemini | gemini-pro                      | `GEMINI_API_KEY`     |
| Groq          | llama3-70b, mixtral             | `GROQ_API_KEY`       |
| Cerebras      | llama3.1-70b                    | `CEREBRAS_API_KEY`   |
| DeepSeek      | deepseek-chat                   | `DEEPSEEK_API_KEY`   |
| Fireworks     | llama-v3p1-70b                  | `FIREWORKS_API_KEY`  |
| MiniMax       | abab6.5-chat                    | `MINIMAX_API_KEY`    |
| Mistral       | mistral-large                   | `MISTRAL_API_KEY`    |
| OpenRouter    | vari modelli                    | `OPENROUTER_API_KEY` |
| Streamlake    | various                         | `STREAMLAKE_API_KEY` |
| Together AI   | vari                            | `TOGETHER_API_KEY`   |
| Z.AI          | zai-lite                        | `ZAI_API_KEY`        |

### Provider Locali

| Provider  | Configurazione                  | Note                             |
| --------- | ------------------------------- | -------------------------------- |
| Ollama    | `GAC_MODEL="ollama:modello"`    | Richiede Ollama in esecuzione    |
| LM Studio | `GAC_MODEL="lm-studio:modello"` | Richiede LM Studio in esecuzione |

### Endpoint Personalizzati

```bash
# Endpoint OpenAI compatibile
export GAC_MODEL="custom:http://localhost:8080:modello"

# Endpoint Anthropic compatibile
export GAC_MODEL="anthropic-custom:http://api.company.com:modello"
```

## Configurazione Avanzata

- **Stai usando Claude Code?** Consulta la [guida alla configurazione di Claude Code](CLAUDE_CODE.md) per le istruzioni di autenticazione OAuth.

### Variabili d'Ambiente

```bash
# Configurazione base
GAC_MODEL="provider:modello"
GAC_LANGUAGE="it"

# Chiavi API (provider-specifiche)
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
GEMINI_API_KEY="..."

# Opzioni avanzate
GAC_TIMEOUT=120          # Timeout in secondi
GAC_MAX_TOKENS=1000      # Token massimi per response
GAC_TEMPERATURE=0.3      # Creatività (0.0-1.0)
```

### File di Configurazione

Crea `.gac.env` nella root del progetto:

```bash
# .gac.env
GAC_MODEL="anthropic:claude-3-sonnet-20240229"
GAC_LANGUAGE="it"
OPENAI_API_KEY="sk-..."
```

### Prompt Personalizzati

```bash
# File di prompt personalizzato
export GAC_CUSTOM_PROMPT="~/.gac-prompt.txt"

# Vedi CUSTOM_SYSTEM_PROMPTS.md per esempi
```

## Integrazione Git

### Hook Pre-commit

gac rispetta automaticamente gli hook pre-commit:

```bash
# Gli hook vengono eseguiti prima del commit
gac -y  # esegue hook pre-commit
```

### Lefthook

Integrazione completa con Lefthook:

```bash
# Configurazione lefthook.yml
pre-commit:
  commands:
    - run: gac --dry-run
      glob: "*.{py,js,ts}"
```

### Configurazione Git

```bash
# Alias git per gac
git config --global alias.gac '!gac'

# Configura editor predefinito
git config --global core.editor "code --wait"
```

## Esempi Pratici

### Sviluppo Frontend

```bash
# Componente React
git add src/components/NewComponent.jsx
gac -h "nuovo componente React con TypeScript"

# Stili CSS
git add src/styles/button.css
gac -h "aggiungi stili per pulsante primario"

# Fix di bug UI
git add src/components/Header.jsx
gac -h "correggi bug menu mobile"
```

### Sviluppo Backend

```bash
# Nuovo endpoint API
git add api/routes/users.py
gac -s -h "nuovo endpoint GET /api/users"

# Migrazione database
git add migrations/001_add_users_table.sql
gac -h "migrazione per tabella utenti"

# Fix di sicurezza
git add auth/middleware.py
gac -h "correggi vulnerabilità XSS"
```

### Sviluppo Python

```bash
# Nuovo modulo
git add src/utils/helpers.py
gac -h "aggiungi funzioni utility comuni"

# Test unitari
git add tests/test_helpers.py
gac -h "test per modulo helpers"

# Refactoring
git add src/models/user.py
git add tests/test_user.py
gac -v -h "refactoring modello user"
```

### Correzioni di Bug

```bash
# Bug critico
git add src/payment/processor.py
gac -h "correggi bug elaborazione pagamenti"

# Bug minor
git add src/ui/validation.js
gac -o -h "fix validazione form"

# Debug
git add src/debug/logger.py
gac -h "aggiungi logging per debug"
```

## Risoluzione Problemi

### Problemi Comuni

```bash
# Nessuna modifica staged
git add .
gac

# Errore autenticazione
export OPENAI_API_KEY="chiave-corretta"
gac

# Timeout
gac -h "sii conciso"  # riduci complessità
```

### Debug

```bash
# Mostra prompt
gac --show-prompt

# Modalità verbose
gac -v

# Test configurazione
gac --show-config
```

## Riferimento Comandi

### Comandi Principali

| Comando        | Descrizione                |
| -------------- | -------------------------- |
| `gac`          | Genera messaggio di commit |
| `gac init`     | Configurazione iniziale    |
| `gac model`    | Cambia provider/modello    |
| `gac language` | Configura lingua           |

### Opzioni Comuni

| Opzione           | Descrizione                   |
| ----------------- | ----------------------------- |
| `-a, --all`       | Staging di tutte le modifiche |
| `-y, --yes`       | Auto-conferma commit          |
| `-o, --one-liner` | Messaggio su una riga         |
| `-v, --verbose`   | Messaggio dettagliato         |
| `-s, --scope`     | Includi scope                 |
| `-p, --push`      | Push dopo commit              |
| `-h, --hint`      | Aggiungi contesto             |
| `-l, --language`  | Sovrascrivi lingua            |

### Opzioni Avanzate

| Opzione              | Descrizione                   |
| -------------------- | ----------------------------- |
| `--group`            | Raggruppa modifiche correlate |
| `--show-prompt`      | Mostra prompt generato        |
| `--dry-run`          | Simula senza commit           |
| `--skip-secret-scan` | Salta scansione sicurezza     |
| `--context-lines`    | Linee di contesto nel diff    |

---

## Tips Pro

### 1. Alias Personalizzati

```bash
# Aggiungi al tuo .bashrc/.zshrc
alias gc='gac -y'
alias gcv='gac -v'
alias gco='gac -o'
alias gcp='gac -p'
```

### 2. Workflow di Team

```bash
# Standard di team
gac -vs -h "implementa user story #123"

# Convenzioni di commit
gac -s -h "segue conventional commits"
```

### 3. Integrazione IDE

```bash
# VS Code tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Git Auto Commit",
      "type": "shell",
      "command": "gac",
      "group": "build"
    }
  ]
}
```

### 4. Automazione

```bash
# Script per commit automatici
#!/bin/bash
git add .
gac -y -h "auto-commit $(date +%Y-%m-%d)"
```

Per più informazioni, controlla la [documentazione completa](https://github.com/cellwebb/gac) o crea un issue su GitHub.
