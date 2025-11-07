# Risoluzione Problemi

[English](../en/TROUBLESHOOTING.md) | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | [한국어](../ko/TROUBLESHOOTING.md) | [हिन्दी](../hi/TROUBLESHOOTING.md) | [Tiếng Việt](../vi/TROUBLESHOOTING.md) | [Français](../fr/TROUBLESHOOTING.md) | [Русский](../ru/TROUBLESHOOTING.md) | [Español](../es/TROUBLESHOOTING.md) | [Português](../pt/TROUBLESHOOTING.md) | [Norsk](../no/TROUBLESHOOTING.md) | [Svenska](../sv/TROUBLESHOOTING.md) | [Deutsch](../de/TROUBLESHOOTING.md) | [Nederlands](../nl/TROUBLESHOOTING.md) | **Italiano**

Questa guida ti aiuterà a risolvere problemi comuni con `gac`.

## Sommario

- [Risoluzione Problemi](#risoluzione-problemi)
  - [Sommario](#sommario)
  - [Problemi di Installazione](#problemi-di-installazione)
    - [uvx non trovato](#uvx-non-trovato)
    - [Errore di permessi](#errore-di-permessi)
    - [Versione Python non supportata](#versione-python-non-supportata)
  - [Problemi di Configurazione](#problemi-di-configurazione)
    - [Chiave API non funzionante](#chiave-api-non-funzionante)
    - [Provider non riconosciuto](#provider-non-riconosciuto)
    - [Modello non valido](#modello-non-valido)
  - [Problemi di Esecuzione](#problemi-di-esecuzione)
    - [Nessuna modifica staged](#nessuna-modifica-staged)
    - [Errore di rete](#errore-di-rete)
    - [Timeout dell'API](#timeout-dellapi)
    - [Messaggio di commit vuoto](#messaggio-di-commit-vuoto)
  - [Problemi di Output](#problemi-di-output)
    - [Output in lingua errata](#output-in-lingua-errata)
    - [Formato non convenzionale](#formato-non-convenzionale)
    - [Messaggio troppo lungo/corto](#messaggio-troppo-lungocorto)
  - [Problemi di Git](#problemi-di-git)
    - [Git non configurato](#git-non-configurato)
    - [Hook pre-commit falliti](#hook-pre-commit-falliti)
    - [Repository dirty](#repository-dirty)
  - [Problemi di Performance](#problemi-di-performance)
    - [Esecuzione lenta](#esecuzione-lenta)
    - [Uso elevato della memoria](#uso-elevato-della-memoria)
  - [Debug e Diagnostica](#debug-e-diagnostica)
    - [Modalità verbose](#modalità-verbose)
    - [Mostra prompt](#mostra-prompt)
    - [Log di debug](#log-di-debug)

## Problemi di Installazione

### uvx non trovato

**Errore**: `command not found: uvx`

**Soluzione**:

```bash
# Installa uv (include uvx)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Oppure usa pip
pip install uv
```

### Errore di permessi

**Errore**: `Permission denied` durante l'installazione

**Soluzione**:

```bash
# Usa ambiente virtuale
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

# Installa nell'ambiente virtuale
pip install gac
```

### Versione Python non supportata

**Errore**: `Python 3.10+ is required`

**Soluzione**:

```bash
# Controlla la tua versione
python --version

# Installa una versione supportata (3.10+)
# Su macOS con Homebrew:
brew install python@3.11

# Su Ubuntu/Debian:
sudo apt update
sudo apt install python3.11
```

## Problemi di Configurazione

### Chiave API non funzionante

**Errore**: `Authentication failed` o `Invalid API key`

**Soluzione**:

1. **Verifica la chiave API**:

   ```bash
   echo $OPENAI_API_KEY  # o altra variabile
   ```

2. **Controlla il formato della variabile d'ambiente**:

   ```bash
   # Corretto
   export OPENAI_API_KEY="sk-..."

   # Errato (spazi extra)
   export OPENAI_API_KEY=" sk-..."
   ```

3. **Verifica il nome della variabile**:

   ```bash
   # Provider comuni e le loro variabili
   OPENAI_API_KEY=          # OpenAI
   ANTHROPIC_API_KEY=       # Anthropic
   GEMINI_API_KEY=          # Google Gemini
   GROQ_API_KEY=            # Groq
   ```

4. **Testa la chiave API**:

   ```bash
   # Per OpenAI
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

5. **Per scadenza token di Claude Code**: Esegui `gac auth` per autenticarti di nuovo rapidamente e aggiornare il tuo token. Il tuo browser si aprirà automaticamente per OAuth.

6. **Per altri problemi OAuth di Claude Code**, consulta la [guida alla configurazione di Claude Code](CLAUDE_CODE.md) per la risoluzione completa dei problemi.

### Provider non riconosciuto

**Errore**: `Unknown provider: xxx`

**Soluzione**:

1. **Controlla i provider supportati**:

   ```bash
   gac --help
   ```

2. **Verifica il nome del provider**:

   ```bash
   # Nomi corretti
   gac init  # mostra la lista completa

   # Esempi comuni
   openai
   anthropic
   gemini
   groq
   ```

3. **Usa il formato corretto nel modello**:

   ```bash
   # Corretto
   export GAC_MODEL="openai:gpt-4"

   # Errato
   export GAC_MODEL="openai_gpt_4"
   ```

### Modello non valido

**Errore**: `Invalid model: xxx`

**Soluzione**:

1. **Verifica i modelli disponibili** per il tuo provider:

   ```bash
   # OpenAI
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models

   # Anthropic
   curl -H "x-api-key: $ANTHROPIC_API_KEY" \
        https://api.anthropic.com/v1/messages
   ```

2. **Usa modelli comuni testati**:

   ```bash
   # OpenAI
   export GAC_MODEL="openai:gpt-4"
   export GAC_MODEL="openai:gpt-3.5-turbo"

   # Anthropic
   export GAC_MODEL="anthropic:claude-3-sonnet-20240229"
   export GAC_MODEL="anthropic:claude-3-haiku-20240307"
   ```

## Problemi di Esecuzione

### Nessuna modifica staged

**Errore**: `No staged changes found`

**Soluzione**:

```bash
# Aggiungi le modifiche
git add .

# O aggiungi file specifici
git add file1.py file2.js

# Verifica le modifiche staged
git status --staged
```

### Errore di rete

**Errore**: `Connection failed` o `Network error`

**Soluzione**:

1. **Verifica la connessione internet**:

   ```bash
   ping google.com
   ```

2. **Controlla proxy/firewall**:

   ```bash
   # Se usi un proxy
   export HTTP_PROXY="http://proxy.company.com:8080"
   export HTTPS_PROXY="http://proxy.company.com:8080"
   ```

3. **Prova un provider diverso**:

   ```bash
   gac model  # cambia provider
   ```

### Timeout dell'API

**Errore**: `Request timeout` o `Operation timed out`

**Soluzione**:

1. **Aumenta il timeout** (se supportato):

   ```bash
   # Alcuni provider permettono timeout personalizzati
   export GAC_TIMEOUT=120
   ```

2. **Prova un modello più veloce**:

   ```bash
   # Da GPT-4 a GPT-3.5-turbo
   export GAC_MODEL="openai:gpt-3.5-turbo"
   ```

3. **Riduci la dimensione del diff**:

   ```bash
   # Fai commit di modifiche più piccole
   git add file-specifico.py
   gac
   ```

### Messaggio di commit vuoto

**Errore**: `Empty commit message generated`

**Soluzione**:

1. **Verifica che ci siano modifiche significative**:

   ```bash
   git diff --staged
   ```

2. **Aggiungi contesto con l'opzione -h**:

   ```bash
   gac -h "correggi bug di autenticazione"
   ```

3. **Prova un formato diverso**:

   ```bash
   gac -v  # formato verbose
   gac -o  # one-liner
   ```

## Problemi di Output

### Output in lingua errata

**Problema**: Messaggi in inglese invece che in italiano

**Soluzione**:

1. **Configura la lingua**:

   ```bash
   gac language
   # Seleziona "Italiano" dalla lista
   ```

2. **Oppure usa il flag -l**:

   ```bash
   gac -l it
   ```

3. **Verifica la configurazione**:

   ```bash
   gac --show-config
   ```

### Formato non convenzionale

**Problema**: Output non segue il formato conventional commit

**Soluzione**:

1. **Usa l'opzione -s per scope**:

   ```bash
   gac -s
   ```

2. **Aggiungi un hint specifico**:

   ```bash
   gac -h "usa formato conventional commit"
   ```

3. **Crea un prompt personalizzato**:

   ```bash
   # Vedi CUSTOM_SYSTEM_PROMPTS.md
   echo "Il tuo prompt personalizzato" > ~/.gac-custom-prompt.txt
   export GAC_CUSTOM_PROMPT="~/.gac-custom-prompt.txt"
   ```

### Messaggio troppo lungo/corto

**Problema**: Messaggio di dimensioni inappropriate

**Soluzione**:

1. **Per messaggi troppo lunghi**:

   ```bash
   gac -o  # one-liner
   gac -h "sii conciso"
   ```

2. **Per messaggi troppo corti**:

   ```bash
   gac -v  # verbose
   gac -h "spiega i dettagli tecnici"
   ```

3. **Usa feedback interattivo**:

   ```bash
   gac
   # Quando richiesto, digita:
   rendilo più dettagliato
   # o
   rendilo più breve
   ```

## Problemi di Git

### Git non configurato

**Errore**: `Please tell me who you are`

**Soluzione**:

```bash
git config --global user.name "Il Tuo Nome"
git config --global user.email "tua.email@example.com"
```

### Hook pre-commit falliti

**Errore**: `pre-commit hook failed`

**Soluzione**:

1. **Esegui gli hook manualmente**:

   ```bash
   lefthook run pre-commit
   ```

2. **Correggi i problemi identificati**:

   ```bash
   # Esempio: formatta il codice
   make format

   # Esempio: correggi linting
   make lint
   ```

3. **Salta gli hook (solo se necessario)**:

   ```bash
   gac --skip-hooks
   # o
   git commit --no-verify
   ```

### Repository dirty

**Errore**: `Working directory not clean`

**Soluzione**:

```bash
# Controlla lo stato
git status

# Fai commit o stash delle modifiche
git add .
git commit -m "commit temporaneo"
# o
git stash

# Poi riprova gac
gac
```

## Problemi di Performance

### Esecuzione lenta

**Problema**: `gac` impiega molto tempo

**Soluzione**:

1. **Usa un modello più veloce**:

   ```bash
   export GAC_MODEL="openai:gpt-3.5-turbo"
   ```

2. **Riduci la dimensione del diff**:

   ```bash
   # Fai commit più frequenti con meno modifiche
   git add subset-di-file/
   gac
   ```

3. **Usa cache locale (se disponibile)**:

   ```bash
   # Alcuni provider supportano cache
   export GAC_CACHE_ENABLED=true
   ```

### Uso elevato della memoria

**Problema**: `gac` usa troppa memoria

**Soluzione**:

1. **Limita il contesto**:

   ```bash
   gac --context-lines 50  # riduci le linee di contesto
   ```

2. **Escludi file grandi**:

   ```bash
   # Aggiungi a .gitignore se non necessario
   echo "file-grande.json" >> .gitignore
   git reset HEAD file-grande.json
   ```

## Debug e Diagnostica

### Modalità verbose

**Uso**: Mostra informazioni dettagliate sull'esecuzione

```bash
gac -v
# o
gac --verbose
```

**Mostra**:

- Passaggi di elaborazione
- Informazioni API
- Tempo di esecuzione

### Mostra prompt

**Uso**: Vedi cosa viene inviato all'AI

```bash
gac --show-prompt
```

**Utile per**:

- Debug del prompt personalizzato
- Verifica del contesto inviato
- Understanding del formato

### Log di debug

**Uso**: Abilita logging dettagliato

```bash
export GAC_DEBUG=true
gac
```

**Mostra**:

- Chiamate API
- Risposte del server
- Errori dettagliati

---

## Ottenere Aiuto Aggiuntivo

Se nessuna di queste soluzioni funziona:

1. **Controlla gli issue su GitHub**: [github.com/cellwebb/gac/issues](https://github.com/cellwebb/gac/issues)
2. **Crea un nuovo issue** con:
   - Sistema operativo
   - Versione di Python e gac
   - Messaggio di errore completo
   - Passaggi per riprodurre il problema
3. **Unisciti alla discussione** su GitHub Discussions

---

## Comandi Utili per Diagnostica

```bash
# Mostra configurazione corrente
gac --show-config

# Verifica installazione
gac --version

# Test connessione API (se disponibile)
gac --test-api

# Mostra provider supportati
gac --list-providers

# Elenca lingue disponibili
gac --list-languages
```

Ricorda: La maggior parte dei problemi sono legati alla configurazione delle chiavi API o alla connessione di rete. Controlla sempre questi aspetti per primi!
