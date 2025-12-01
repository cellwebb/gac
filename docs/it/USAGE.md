# Utilizzo della Linea di Comando di gac

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | **Italiano**

Questo documento descrive tutte le flag e opzioni disponibili per lo strumento CLI `gac`.

## Indice

- [Utilizzo della Linea di Comando di gac](#utilizzo-della-linea-di-comando-di-gac)
  - [Indice](#indice)
  - [Utilizzo Base](#utilizzo-base)
  - [Flag del Workflow Principale](#flag-del-workflow-principale)
  - [Personalizzazione Messaggio](#personalizzazione-messaggio)
  - [Output e Verbosità](#output-e-verbosità)
  - [Aiuto e Versione](#aiuto-e-versione)
  - [Workflow di Esempio](#workflow-di-esempio)
  - [Avanzate](#avanzate)
    - [Integrazione Script e Elaborazione Esterna](#integrazione-script-e-elaborazione-esterna)
    - [Saltare Hook Pre-commit e Lefthook](#saltare-hook-pre-commit-e-lefthook)
    - [Scansione Sicurezza](#scansione-sicurezza)
  - [Note di Configurazione](#note-di-configurazione)
    - [Opzioni di Configurazione Avanzate](#opzioni-di-configurazione-avanzate)
    - [Sottocomandi di Configurazione](#sottocomandi-di-configurazione)
  - [Modalità Interattiva](#modalità-interattiva)
    - [Come Funziona](#come-funziona)
    - [Quando Usare la Modalità Interattiva](#quando-usare-la-modalità-interattiva)
    - [Esempi di Utilizzo](#esempi-di-utilizzo)
    - [Workflow Domanda-Risposta](#workflow-domanda-risposta)
    - [Combinazione con Altre Flag](#combinazione-con-altre-flag)
    - [Best Practice](#best-practice)
  - [Ottenere Aiuto](#ottenere-aiuto)

## Utilizzo Base

```sh
gac init
# Segui le istruzioni per configurare il tuo provider, modello e chiavi API in modo interattivo
gac
```

Genera un messaggio di commit basato su LLM per le modifiche in staging e richiede conferma. Il prompt di conferma accetta:

- `y` o `yes` - Procedi con il commit
- `n` o `no` - Annulla il commit
- `r` o `reroll` - Rigenera il messaggio di commit con lo stesso contesto
- `e` o `edit` - Modifica il messaggio di commit sul posto con editing ricco del terminale (binding vi/emacs)
- Qualsiasi altro testo - Rigenera con quel testo come feedback (es. `rendilo più breve`, `concentrati sulle performance`)
- Input vuoto (solo Enter) - Mostra di nuovo il prompt

---

## Flag del Workflow Principale

| Flag / Opzione       | Breve | Descrizione                                               |
| -------------------- | ----- | --------------------------------------------------------- |
| `--add-all`          | `-a`  | Metti in staging tutte le modifiche prima del commit      |
| `--group`            | `-g`  | Raggruppa le modifiche in staging in più commit logici    |
| `--push`             | `-p`  | Push delle modifiche al remote dopo il commit             |
| `--yes`              | `-y`  | Conferma automaticamente il commit senza richiedere       |
| `--dry-run`          |       | Mostra cosa accadrebbe senza fare modifiche               |
| `--message-only`     |       | Output solo del messaggio di commit generato senza commit |
| `--no-verify`        |       | Salta hook pre-commit e lefthook durante il commit        |
| `--skip-secret-scan` |       | Salta scansione sicurezza per segreti nelle modifiche     |
| `--interactive`      | `-i`  | Fai domande sulle modifiche per generare commit migliori  |

**Nota:** Combina `-a` e `-g` (cioè `-ag`) per mettere in staging TUTTE le modifiche prima, poi raggrupparle in commit.

**Nota:** Quando usi `--group`, il limite massimo di token di output viene scalato automaticamente in base al numero di file in commit (2x per 1-9 file, 3x per 10-19 file, 4x per 20-29 file, 5x per 30+ file). Questo assicura che l'LLM abbia abbastanza token per generare tutti i commit raggruppati senza troncamento, anche per changeset grandi.

**Nota:** `--message-only` e `--group` si escludono a vicenda. Usa `--message-only` quando vuoi ottenere il messaggio di commit per elaborazione esterna, e `--group` quando vuoi organizzare più commit nel workflow git corrente.

**Nota:** La flag `--interactive` fa domande sulle tue modifiche per fornire contesto aggiuntivo all'LLM, risultando in messaggi di commit più accurati e dettagliati. Questo è particolarmente utile per modifiche complesse o quando vuoi assicurarti che il messaggio di commit catturi il contesto completo del tuo lavoro.

## Personalizzazione Messaggio

| Flag / Opzione      | Breve | Descrizione                                                                   |
| ------------------- | ----- | ----------------------------------------------------------------------------- |
| `--one-liner`       | `-o`  | Genera un messaggio di commit su una riga                                     |
| `--verbose`         | `-v`  | Genera messaggi di commit dettagliati con motivazione, architettura e impatto |
| `--hint <text>`     | `-h`  | Aggiungi un suggerimento per guidare l'LLM                                    |
| `--model <model>`   | `-m`  | Specifica il modello da usare per questo commit                               |
| `--language <lang>` | `-l`  | Sovrascrivi la lingua (nome o codice: 'Italian', 'it', 'zh-CN', 'ja')         |
| `--scope`           | `-s`  | Deduci uno scope appropriato per il commit                                    |

**Nota:** Puoi fornire feedback in modo interattivo digitandolo semplicemente al prompt di conferma - non è necessario prefissare con 'r'. Digita `r` per un semplice reroll, `e` per modificare sul posto con binding vi/emacs, o digita il tuo feedback direttamente come `rendilo più breve`.

## Output e Verbosità

| Flag / Opzione        | Breve | Descrizione                                                 |
| --------------------- | ----- | ----------------------------------------------------------- |
| `--quiet`             | `-q`  | Sopprimi tutto l'output tranne gli errori                   |
| `--log-level <level>` |       | Imposta livello di log (debug, info, warning, error)        |
| `--show-prompt`       |       | Stampa il prompt LLM usato per la generazione del messaggio |

## Aiuto e Versione

| Flag / Opzione | Breve | Descrizione                       |
| -------------- | ----- | --------------------------------- |
| `--version`    |       | Mostra versione gac ed esce       |
| `--help`       |       | Mostra messaggio di aiuto ed esce |

---

## Workflow di Esempio

- **Metti in staging tutte le modifiche e fai commit:**

  ```sh
  gac -a
  ```

- **Fai commit e push in un passo:**

  ```sh
  gac -ap
  ```

- **Genera un messaggio di commit su una riga:**

  ```sh
  gac -o
  ```

- **Genera un messaggio di commit dettagliato con sezioni strutturate:**

  ```sh
  gac -v
  ```

- **Aggiungi un suggerimento per l'LLM:**

  ```sh
  gac -h "Rifattorizza logica di autenticazione"
  ```

- **Deduci scope per il commit:**

  ```sh
  gac -s
  ```

- **Raggruppa modifiche in staging in commit logici:**

  ```sh
  gac -g
  # Raggruppa solo i file che hai già messo in staging
  ```

- **Raggruppa tutte le modifiche (staging + non-staging) e conferma automaticamente:**

  ```sh
  gac -agy
  # Mette in staging tutto, raggruppa e conferma automaticamente
  ```

- **Usa un modello specifico solo per questo commit:**

  ```sh
  gac -m anthropic:claude-haiku-4-5
  ```

- **Genera messaggio di commit in una lingua specifica:**

  ```sh
  # Usando codici lingua (più brevi)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # Usando nomi completi
  gac -l "Cinese Semplificato"
  gac -l Giapponese
  gac -l Spagnolo
  ```

- **Dry run (vedi cosa accadrebbe):**

  ```sh
  gac --dry-run
  ```

- **Ottieni solo il messaggio di commit (per integrazione script):**

  ```sh
  gac --message-only
  # Output: feat: aggiungi sistema di autenticazione utente
  ```

- **Ottieni messaggio di commit in formato una riga:**

  ```sh
  gac --message-only --one-liner
  # Output: feat: aggiungi sistema di autenticazione utente
  ```

- **Usa modalità interattiva per fornire contesto:**

  ```sh
  gac -i
  # Qual è lo scopo principale di queste modifiche?
  # Quale problema stai risolvendo?
  # Ci sono dettagli implementativi da menzionare?
  ```

- **Modalità interattiva con output dettagliato:**

  ```sh
  gac -i -v
  # Fai domande e genera messaggio di commit dettagliato
  ```

## Avanzate

- Combina flag per workflow più potenti (es. `gac -ayp` per mettere in staging, confermare automaticamente e pushare)
- Usa `--show-prompt` per debuggare o rivedere il prompt inviato all'LLM
- Regola verbosità con `--log-level` o `--quiet`
- Usa `--message-only` per integrazione script e workflow automatizzati

### Integrazione Script e Elaborazione Esterna

La flag `--message-only` è progettata per integrazione script e workflow strumenti esterni. Output solo il messaggio di commit grezzo senza formattazione, spinner o elementi UI aggiuntivi.

**Casi d'uso:**

- **Integrazione agenti:** Permetti agli agenti AI di ottenere messaggi di commit e gestire i commit stessi
- **VCS alternativi:** Usa messaggi generati con altri sistemi di controllo versione (Mercurial, Jujutsu, ecc.)
- **Workflow commit personalizzati:** Elabora o modifica il messaggio prima del commit
- **Pipeline CI/CD:** Estrai messaggi di commit per processi automatizzati

**Esempio uso script:**

```sh
#!/bin/bash
# Ottieni messaggio di commit e usa con funzione commit personalizzata
MESSAGE=$(gac --message-only --add-all --yes)
git commit -m "$MESSAGE"
```

```python
# Esempio integrazione Python
import subprocess

def get_commit_message():
    result = subprocess.run(
        ["gac", "--message-only", "--yes"],
        capture_output=True, text=True
    )
    return result.stdout.strip()

message = get_commit_message()
print(f"Messaggio generato: {message}")
```

**Caratteristiche chiave per uso script:**

- Output pulito senza formattazione Rich o spinner
- Bypassa automaticamente i prompt di conferma
- Nessun commit effettivo viene fatto su git
- Funziona con `--one-liner` per output semplificato
- Può essere combinato con altre flag come `--hint`, `--model`, ecc.

### Saltare Hook Pre-commit e Lefthook

La flag `--no-verify` ti permette di saltare qualsiasi hook pre-commit o lefthook configurato nel tuo progetto:

```sh
gac --no-verify  # Salta tutti gli hook pre-commit e lefthook
```

**Usa `--no-verify` quando:**

- Gli hook pre-commit o lefthook falliscono temporaneamente
- Stai lavorando con hook che richiedono molto tempo
- Stai facendo commit di codice work-in-progress che non passa ancora tutti i controlli

**Nota:** Usa con cautela poiché questi hook mantengono standard di qualità del codice.

### Scansione Sicurezza

gac include scansione sicurezza integrata che rileva automaticamente potenziali segreti e chiavi API nelle tue modifiche in staging prima del commit. Questo aiuta a prevenire il commit accidentale di informazioni sensibili.

**Saltare scansioni sicurezza:**

```sh
gac --skip-secret-scan  # Salta scansione sicurezza per questo commit
```

**Per disabilitare permanentemente:** Imposta `GAC_SKIP_SECRET_SCAN=true` nel tuo file `.gac.env`.

**Quando saltare:**

- Commit di codice esempio con chiavi segnaposto
- Lavoro con test fixture che contengono credenziali fittizie
- Quando hai verificato che le modifiche sono sicure

**Nota:** Lo scanner usa pattern matching per rilevare formati segreti comuni. Rivedi sempre le tue modifiche in staging prima del commit.

## Note di Configurazione

- Il modo raccomandato per configurare gac è eseguire `gac init` e seguire i prompt interattivi.
- Già configurata la lingua e devi solo cambiare provider o modelli? Esegui `gac model` per ripetere la configurazione senza domande sulla lingua.
- **Usi Claude Code?** Vedi la [guida setup Claude Code](CLAUDE_CODE.md) per istruzioni autenticazione OAuth.
- gac carica la configurazione nel seguente ordine di precedenza:
  1. Flag CLI
  2. Variabili ambiente
  3. `.gac.env` a livello di progetto
  4. `~/.gac.env` a livello utente

### Opzioni di Configurazione Avanzate

Puoi personalizzare il comportamento di gac con queste variabili ambiente opzionali:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Deduci automaticamente e includi scope nei messaggi di commit (es. `feat(auth):` vs `feat:`)
- `GAC_VERBOSE=true` - Genera messaggi di commit dettagliati con sezioni motivazione, architettura e impatto
- `GAC_TEMPERATURE=0.7` - Controlla creatività LLM (0.0-1.0, più basso = più focalizzato)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Token massimi per messaggi generati (scalato automaticamente 2-5x quando usi `--group` in base al numero di file; sovrascrivi per andare più alto o più basso)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Avvisa quando i prompt superano questo numero di token
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Usa un prompt di sistema personalizzato per la generazione messaggi di commit
- `GAC_LANGUAGE=Italian` - Genera messaggi di commit in una lingua specifica (es. Italian, French, Japanese, German). Supporta nomi completi o codici ISO (it, fr, ja, de, zh-CN). Usa `gac language` per selezione interattiva
- `GAC_TRANSLATE_PREFIXES=true` - Traduci prefissi commit convenzionali (feat, fix, ecc.) nella lingua target (default: false, mantiene prefissi in inglese)
- `GAC_SKIP_SECRET_SCAN=true` - Disabilita scansione sicurezza automatica per segreti nelle modifiche in staging (usa con cautela)
- `GAC_NO_TIKTOKEN=true` - Rimani completamente offline bypassando il passo download `tiktoken` e usando lo stimatore token approssimato integrato

Vedi `.gac.env.example` per un template di configurazione completo.

Per guida dettagliata sulla creazione di prompt di sistema personalizzati, vedi [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md).

### Sottocomandi di Configurazione

I seguenti sottocomandi sono disponibili:

- `gac init` — Setup guidato interattivo per configurazione provider, modello e lingua
- `gac model` — Setup provider/modello/chiave API senza prompt lingua (ideale per cambi rapidi)
- `gac auth` — Autentica o ri-autentica token OAuth Claude Code (utile quando il token scade)
- `gac config show` — Mostra configurazione corrente
- `gac config set KEY VALUE` — Imposta una chiave di configurazione in `$HOME/.gac.env`
- `gac config get KEY` — Ottieni un valore di configurazione
- `gac config unset KEY` — Rimuovi una chiave di configurazione da `$HOME/.gac.env`
- `gac language` (o `gac lang`) — Selettore lingua interattivo per messaggi di commit (imposta GAC_LANGUAGE)
- `gac diff` — Mostra git diff filtrato con opzioni per modifiche staging/non-staging, colore e troncamento

## Modalità Interattiva

La flag `--interactive` (`-i`) migliora la generazione messaggi di commit di gac facendoti domande mirate sulle tue modifiche. Questo contesto aggiuntivo aiuta l'LLM a creare messaggi di commit più accurati, dettagliati e contestualmente appropriati.

### Come Funziona

Quando usi `--interactive`, gac ti farà domande come:

- **Qual è lo scopo principale di queste modifiche?** - Aiuta a capire l'obiettivo di alto livello
- **Quale problema stai risolvendo?** - Fornisce contesto sulla motivazione
- **Ci sono dettagli implementativi da menzionare?** - Cattura specifiche tecniche
- **Ci sono breaking changes?** - Identifica potenziali problemi di impatto
- **Questo è correlato a qualche issue o ticket?** - Collega al project management

### Quando Usare la Modalità Interattiva

La modalità interattiva è particolarmente utile per:

- **Modifiche complesse** dove il contesto non è ovvio solo dal diff
- **Lavoro di refactoring** che si estende su più file e concetti
- **Nuove funzionalità** che richiedono spiegazione dello scopo generale
- **Bug fix** dove la causa radice non è immediatamente visibile
- **Ottimizzazioni performance** dove il ragionamento non è ovvio
- **Preparazione code review** - le domande aiutano a pensare alle tue modifiche

### Esempi di Utilizzo

**Modalità interattiva base:**

```sh
gac -i
```

Questo:

1. Mostra un riepilogo delle modifiche in staging
2. Fa domande sulle modifiche
3. Genera un messaggio di commit incorporando le tue risposte
4. Richiede conferma (o conferma automatica se combinato con `-y`)

**Modalità interattiva con modifiche in staging:**

```sh
gac -ai
# Metti in staging tutte le modifiche, poi fai domande per migliore contesto
```

**Modalità interattiva con suggerimenti specifici:**

```sh
gac -i -h "Migrazione database per profili utente"
# Fai domande fornendo un suggerimento specifico per focalizzare l'LLM
```

**Modalità interattiva con output dettagliato:**

```sh
gac -i -v
# Fai domande e genera un messaggio di commit dettagliato e strutturato
```

**Modalità interattiva con conferma automatica:**

```sh
gac -i -y
# Fai domande ma conferma automaticamente il commit risultante
```

### Workflow Domanda-Risposta

Il workflow interattivo segue questo schema:

1. **Rivedi modifiche** - gac mostra un riepilogo di ciò che stai committando
2. **Rispondi alle domande** - rispondi a ogni prompt con dettagli rilevanti
3. **Miglioramento contesto** - le tue risposte vengono aggiunte al prompt LLM
4. **Generazione messaggio** - l'LLM crea un messaggio di commit con contesto completo
5. **Conferma** - rivedi e conferma il commit (o conferma automatica con `-y`)

**Suggerimenti per fornire risposte utili:**

- **Sii conciso ma completo** - fornisci dettagli chiave senza essere eccessivamente verboso
- **Concentrati sul "perché"** - spiega il ragionamento dietro le tue modifiche
- **Menziona vincoli** - nota limitazioni o considerazioni speciali
- **Collega a contesto esterno** - riferisci a issues, documentazione o documenti di design
- **Risposte vuote vanno bene** - se una domanda non si applica, premi solo Enter

### Combinazione con Altre Flag

La modalità interattiva funziona bene con la maggior parte delle altre flag:

```sh
# Metti in staging tutte le modifiche e fai domande
gac -ai

# Fai domande con output dettagliato
gac -i -v
```

### Best Practice

- **Usa per PR complessi** - particolarmente utile per pull request che necessitano descrizioni dettagliate
- **Collaborazione team** - le domande aiutano a pensare a modifiche che altri revisioneranno
- **Preparazione documentazione** - le tue risposte possono aiutare a formare la base per le release notes
- **Strumento di apprendimento** - le domande rafforzano buone pratiche di messaggi di commit
- **Salta per modifiche semplici** - per fix banali, la modalità base potrebbe essere più veloce

## Ottenere Aiuto

- Per prompt di sistema personalizzati, vedi [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- Per troubleshooting e suggerimenti avanzati, vedi [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Per installazione e configurazione, vedi [README.md#installation-and-configuration](README.md#installation-and-configuration)
- Per contribuire, vedi [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Informazioni licenza: [LICENSE](LICENSE)
