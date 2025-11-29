# Contribuire a gac

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Norsk](../no/CONTRIBUTING.md) | [Svenska](../sv/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md) | **Italiano**

Grazie per il tuo interesse a contribuire a questo progetto! Il tuo aiuto è apprezzato. Per favore segui queste linee guida per rendere il processo fluido per tutti.

## Sommario

- [Contribuire a gac](#contribuire-a-gac)
  - [Sommario](#sommario)
  - [Setup Ambiente di Sviluppo](#setup-ambiente-di-sviluppo)
    - [Setup Rapido](#setup-rapido)
    - [Setup Alternativo (se preferisci passo-passo)](#setup-alternativo-se-preferisci-passo-passo)
    - [Comandi Disponibili](#comandi-disponibili)
  - [Incremento Versione](#incremento-versione)
    - [Come incrementare la versione](#come-incrementare-la-versione)
    - [Processo di Release](#processo-di-release)
    - [Usare bump-my-version (opzionale)](#usare-bump-my-version-opzionale)
  - [Aggiungere un Nuovo Provider AI](#aggiungere-un-nuovo-provider-ai)
    - [Checklist per Aggiungere un Nuovo Provider](#checklist-per-aggiungere-un-nuovo-provider)
    - [Esempio di Implementazione](#esempio-di-implementazione)
    - [Punti Chiave](#punti-chiave)
  - [Standard di Codifica](#standard-di-codifica)
  - [Git Hooks (Lefthook)](#git-hooks-lefthook)
    - [Setup](#setup)
    - [Saltare Git Hooks](#saltare-git-hooks)
  - [Linee Guida per i Test](#linee-guida-per-i-test)
    - [Eseguire i Test](#eseguire-i-test)
      - [Test di Integrazione Provider](#test-di-integrazione-provider)
  - [Codice di Condotta](#codice-di-condotta)
  - [Licenza](#licenza)
  - [Dove Ottenere Aiuto](#dove-ottenere-aiuto)

## Setup Ambiente di Sviluppo

Questo progetto usa `uv` per la gestione delle dipendenze e fornisce un Makefile per compiti di sviluppo comuni:

### Setup Rapido

```bash
# Un comando per configurare tutto inclusi gli hook Lefthook
make dev
```

Questo comando:

- Installerà le dipendenze di sviluppo
- Installerà gli hook git
- Eseguirà gli hook Lefthook su tutti i file per correggere eventuali problemi esistenti

### Setup Alternativo (se preferisci passo-passo)

```bash
# Crea ambiente virtuale e installa dipendenze
make setup

# Installa dipendenze di sviluppo
make dev

# Installa hook Lefthook
brew install lefthook  # o vedi docs sotto per alternative
lefthook install
lefthook run pre-commit --all
```

### Comandi Disponibili

- `make setup` - Crea ambiente virtuale e installa tutte le dipendenze
- `make dev` - **Setup di sviluppo completo** - include hook Lefthook
- `make test` - Esegui test standard (esclude test di integrazione)
- `make test-integration` - Esegui solo test di integrazione (richiede chiavi API)
- `make test-all` - Esegui tutti i test
- `make test-cov` - Esegui test con report di coverage
- `make lint` - Controlla qualità del codice (ruff, prettier, markdownlint)
- `make format` - Correggi automaticamente problemi di formattazione del codice

## Incremento Versione

**Importante**: Le PR dovrebbero includere un incremento di versione in `src/gac/__version__.py` quando contengono modifiche che dovrebbero essere rilasciate.

### Come incrementare la versione

1. Modifica `src/gac/__version__.py` e incrementa il numero di versione
2. Segui [Semantic Versioning](https://semver.org/):
   - **Patch** (1.6.X): Correzioni di bug, piccoli miglioramenti
   - **Minor** (1.X.0): Nuove funzionalità, modifiche retrocompatibili (es: aggiungere un nuovo provider)
   - **Major** (X.0.0): Modifiche breaking

### Processo di Release

Le release sono attivate dal push di tag di versione:

1. Fonde PR con incrementi di versione su main
2. Crea un tag: `git tag v1.6.1`
3. Push del tag: `git push origin v1.6.1`
4. GitHub Actions pubblica automaticamente su PyPI

Esempio:

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # Incrementato da 1.6.0
```

### Usare bump-my-version (opzionale)

Se hai `bump-my-version` installato, puoi usarlo localmente:

```bash
# Per correzioni di bug:
bump-my-version bump patch

# Per nuove funzionalità:
bump-my-version bump minor

# Per modifiche breaking:
bump-my-version bump major
```

## Aggiungere un Nuovo Provider AI

Quando aggiungi un nuovo provider AI, devi aggiornare più file nel codebase. Segui questa checklist completa:

### Checklist per Aggiungere un Nuovo Provider

- [ ] **1. Crea Implementazione Provider** (`src/gac/providers/<provider_name>.py`)

  - Crea un nuovo file chiamato come il provider (es: `minimax.py`)
  - Implementa `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str`
  - Usa il formato compatibile OpenAI se il provider lo supporta
  - Gestisci chiave API da variabile d'ambiente `<PROVIDER>_API_KEY`
  - Includi gestione errori appropriata con tipi `AIError`:
    - `AIError.authentication_error()` per problemi di autenticazione
    - `AIError.rate_limit_error()` per limiti di frequenza (HTTP 429)
    - `AIError.timeout_error()` per timeout
    - `AIError.model_error()` per errori del modello e contenuto vuoto/nullo
  - Imposta URL endpoint API
  - Usa timeout di 120 secondi per richieste HTTP

- [ ] **2. Registra Provider nel Pacchetto** (`src/gac/providers/__init__.py`)

  - Aggiungi import: `from .<provider> import call_<provider>_api`
  - Aggiungi al dizionario `PROVIDER_REGISTRY`: `"provider-name": call_<provider>_api`
  - Aggiungi alla lista `__all__`: `"call_<provider>_api"`

- [ ] **3. Aggiorna Configurazione Esempio** (`.gac.env.example`)

  - Aggiungi configurazione modello esempio nel formato: `# GAC_MODEL=provider:model-name`
  - Aggiungi voce chiave API: `# <PROVIDER>_API_KEY=your_key_here`
  - Mantieni voci ordinate alfabeticamente
  - Aggiungi commenti per chiavi opzionali se applicabile

- [ ] **4. Aggiorna Documentazione** (`README.md` e tutte le traduzioni di `README.md` in `docs/`)

  - Aggiungi nome provider alla sezione "Provider Supportati" in tutte le traduzioni dei README
  - Mantieni la lista ordinata alfabeticamente nei suoi punti elenco

- [ ] **5. Aggiungi al Setup Interattivo** (`src/gac/init_cli.py`)

  - Aggiungi tupla alla lista `providers`: `("Provider Name", "default-model-name")`
  - Mantieni la lista ordinata alfabeticamente
  - **Importante**: Se il tuo provider usa un nome di chiave API non standard (non quello generato automaticamente `{PROVIDER_UPPERCASE}_API_KEY`), aggiungi gestione speciale:

    ```python
    elif provider_key == "your-provider-key":
        api_key_name = "YOUR_CUSTOM_API_KEY_NAME"
    ```

    Esempi: `kimi-for-coding` usa `KIMI_CODING_API_KEY`, `moonshot-ai` usa `MOONSHOT_API_KEY`

- [ ] **6. Crea Test Completi** (`tests/providers/test_<provider>.py`)

  - Crea file test seguendo la convenzione di nomenclatura
  - Includi queste classi di test:
    - `Test<Provider>Imports` - Test import modulo e funzione
    - `Test<Provider>APIKeyValidation` - Test errore chiave API mancante
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - Eredita da `BaseProviderTest` per 9 test standard
    - `Test<Provider>EdgeCases` - Test contenuto nullo e altri edge case
    - `Test<Provider>Integration` - Test chiamate API reali (marcati con `@pytest.mark.integration`)
  - Implementa proprietà richieste nella classe di test mock:
    - `provider_name` - Nome provider (minuscolo)
    - `provider_module` - Percorso completo modulo
    - `api_function` - Riferimento alla funzione API
    - `api_key_env_var` - Nome variabile d'ambiente per chiave API (o None per provider locali)
    - `model_name` - Nome modello predefinito per test
    - `success_response` - Risposta API mock di successo
    - `empty_content_response` - Risposta mock contenuto vuoto

- [ ] **7. Incrementa Versione** (`src/gac/__version__.py`)
  - Incrementa la versione **minor** (es: 1.10.2 → 1.11.0)
  - Aggiungere un provider è una nuova funzionalità e richiede un incremento di versione minor

### Esempio di Implementazione

Vedi l'implementazione del provider MiniMax come riferimento:

- Provider: `src/gac/providers/minimax.py`
- Test: `tests/providers/test_minimax.py`

### Punti Chiave

1. **Gestione Errori**: Usa sempre il tipo `AIError` appropriato per diversi scenari di errore
2. **Contenuto Nullo/Vuoto**: Controlla sempre sia `None` che contenuto stringa vuoto nelle risposte
3. **Testing**: La classe `BaseProviderTest` fornisce 9 test standard che ogni provider dovrebbe ereditare
4. **Ordine Alfabetico**: Mantieni le liste provider ordinate alfabeticamente per manutenibilità
5. **Nomenclatura Chiavi API**: Usa il formato `<PROVIDER>_API_KEY` (tutto maiuscolo, underscore per spazi)
6. **Registrazione Provider**: Modifica solo `src/gac/providers/__init__.py` e `src/gac/init_cli.py` – `ai.py` e `ai_utils.py` leggono automaticamente dal registro
7. **Formato Nome Provider**: Usa minuscolo con trattini per nomi multi-parola (es: "lm-studio")
8. **Incremento Versione**: Aggiungere un provider richiede un incremento di versione **minor** (nuova funzionalità)

## Standard di Codifica

- Target Python 3.10+ (3.10, 3.11, 3.12, 3.13, 3.14)
- Usa type hints per tutti i parametri di funzione e valori di ritorno
- Mantieni il codice pulito, compatto e leggibile
- Evita complessità non necessaria
- Usa logging invece di istruzioni print
- La formattazione è gestita da `ruff` (linting, formattazione e ordinamento import in uno strumento; lunghezza massima linea: 120)
- Scrivi test minimi ed efficaci con `pytest`

## Git Hooks (Lefthook)

Questo progetto usa [Lefthook](https://github.com/evilmartians/lefthook) per mantenere i controlli di qualità del codice veloci e consistenti. Gli hook configurati rispecchiano il nostro setup pre-commit precedente:

- `ruff` - Python linting e formattazione (sostituisce black, isort e flake8)
- `markdownlint-cli2` - Markdown linting
- `prettier` - Formattazione file (markdown, yaml, json)
- `check-upstream` - Hook personalizzato per controllare modifiche upstream

### Setup

**Approccio raccomandato:**

```bash
make dev
```

**Setup manuale (se preferisci passo-passo):**

1. Installa Lefthook (scegli l'opzione che corrisponde al tuo setup):

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # o
   cargo install lefthook         # Rust toolchain
   # o
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. Installa gli hook git:

   ```sh
   lefthook install
   ```

3. (Opzionale) Esegui su tutti i file:

   ```sh
   lefthook run pre-commit --all
   ```

Gli hook ora eseguiranno automaticamente a ogni commit. Se qualche controllo fallisce, dovrai correggere i problemi prima di poter fare il commit.

### Saltare Git Hooks

Se hai bisogno di saltare temporaneamente i controlli Lefthook, usa il flag `--no-verify`:

```sh
git commit --no-verify -m "Il tuo messaggio di commit"
```

Nota: Questo dovrebbe essere usato solo quando assolutamente necessario, poiché bypassa controlli importanti di qualità del codice.

## Linee Guida per i Test

Il progetto usa pytest per i test. Quando aggiungi nuove funzionalità o correggi bug, per favore includi test che coprono le tue modifiche.

Nota che la directory `scripts/` contiene script di test per funzionalità che non possono essere facilmente testate con pytest. Sentiti libero di aggiungere script qui per testare scenari complessi o test di integrazione che sarebbero difficili da implementare usando il framework pytest standard.

### Eseguire i Test

```sh
# Esegui test standard (esclude test di integrazione con chiamate API reali)
make test

# Esegui solo test di integrazione provider (richiede chiavi API)
make test-integration

# Esegui tutti i test inclusi test di integrazione provider
make test-all

# Esegui test con coverage
make test-cov

# Esegui file di test specifico
uv run -- pytest tests/test_prompt.py

# Esegui test specifico
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### Test di Integrazione Provider

I test di integrazione provider fanno chiamate API reali per verificare che le implementazioni dei provider funzionino correttamente con le API effettive. Questi test sono marcati con `@pytest.mark.integration` e sono saltati di default per:

- Evitare di consumare crediti API durante lo sviluppo regolare
- Prevenire fallimenti dei test quando le chiavi API non sono configurate
- Mantenere l'esecuzione dei test veloce per iterazione rapida

Per eseguire i test di integrazione provider:

1. **Configura le chiavi API** per i provider che vuoi testare:

   ```sh
   export ANTHROPIC_API_KEY="tua-chiave"
   export CEREBRAS_API_KEY="tua-chiave"
   export GEMINI_API_KEY="tua-chiave"
   export GROQ_API_KEY="tua-chiave"
   export OPENAI_API_KEY="tua-chiave"
   export OPENROUTER_API_KEY="tua-chiave"
   export STREAMLAKE_API_KEY="tua-chiave"
   export ZAI_API_KEY="tua-chiave"
   # LM Studio e Ollama richiedono un'istanza locale in esecuzione
   # Le chiavi API per LM Studio e Ollama sono opzionali a meno che il tuo deployment non impona autenticazione
   ```

2. **Esegui test provider**:

   ```sh
   make test-integration
   ```

I test salteranno provider dove le chiavi API non sono configurate. Questi test aiutano a rilevare cambiamenti API presto e assicurano compatibilità con le API dei provider.

## Codice di Condotta

Sii rispettoso e costruttivo. Molestie o comportamento abusivo non saranno tollerati.

## Licenza

Contribuendo, accetti che i tuoi contributi saranno licenziati sotto la stessa licenza del progetto.

---

## Dove Ottenere Aiuto

- Per risoluzione problemi, vedi [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Per utilizzo e opzioni CLI, vedi [USAGE.md](USAGE.md)
- Per dettagli licenza, vedi [../../LICENSE](../../LICENSE)

Grazie per aiutare a migliorare gac!
