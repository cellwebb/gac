# Usare GAC come Server MCP

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | **Italiano**

GAC può funzionare come un server del [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), permettendo ad agenti IA ed editor di generare commit attraverso chiamate di strumenti strutturate invece di comandi shell.

## Indice

- [Usare GAC come Server MCP](#usare-gac-come-server-mcp)
  - [Indice](#indice)
  - [Cos'è MCP?](#cosè-mcp)
  - [Benefici](#benefici)
  - [Installazione](#installazione)
    - [Claude Code](#claude-code)
    - [Cursor](#cursor)
    - [Altri Client MCP](#altri-client-mcp)
  - [Strumenti Disponibili](#strumenti-disponibili)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Flussi di Lavoro](#flussi-di-lavoro)
    - [Commit Base](#commit-base)
    - [Anteprima Prima del Commit](#anteprima-prima-del-commit)
    - [Commit Raggruppati](#commit-raggruppati)
    - [Commit con Contesto](#commit-con-contesto)
  - [Configurazione](#configurazione)
  - [Risoluzione Problemi](#risoluzione-problemi)
  - [Vedi Anche](#vedi-anche)

## Cos'è MCP?

Il Model Context Protocol è uno standard aperto che permette alle applicazioni IA di chiamare strumenti esterni attraverso un'interfaccia strutturata. Eseguendo GAC come server MCP, qualsiasi client compatibile con MCP può ispezionare lo stato del repository e creare commit alimentati dall'IA senza invocare direttamente comandi shell.

## Benefici

- **Interazione strutturata**: Gli agenti chiamano strumenti tipizzati con parametri validati invece di analizzare l'output della shell
- **Flusso di lavoro a due strumenti**: `gac_status` per ispezionare, `gac_commit` per agire — un adattamento naturale per il ragionamento degli agenti
- **Capacità complete di GAC**: Messaggi di commit IA, commit raggruppati, scansione di segreti e push — tutto disponibile tramite MCP
- **Nessuna configurazione aggiuntiva**: Il server utilizza la tua configurazione GAC esistente (`~/.gac.env`, impostazioni provider, ecc.)

## Installazione

Il server MCP viene avviato con `gac serve` e comunica tramite stdio, il trasporto standard MCP.

### Claude Code

Aggiungi al `.mcp.json` del tuo progetto o al `~/.claude/claude_code_config.json` globale:

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

O se hai GAC installato globalmente:

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

### Cursor

Aggiungi alle impostazioni MCP di Cursor (`.cursor/mcp.json`):

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

### Altri Client MCP

Qualsiasi client compatibile con MCP può usare GAC. Il punto di ingresso del server è:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

Se hai GAC installato (tramite `uv tool install gac`), puoi usare `gac` direttamente invece di `uvx gac`.

## Strumenti Disponibili

Il server espone due strumenti:

### gac_status

Ispeziona lo stato del repository. Usalo prima del commit per capire cosa verrà committato.

**Parametri:**

| Parameter           | Type                                    | Default     | Descrizione                                      |
| ------------------- | --------------------------------------- | ----------- | ------------------------------------------------ |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Formato di output                                |
| `include_diff`      | bool                                    | `false`     | Includere il contenuto completo del diff         |
| `include_stats`     | bool                                    | `true`      | Includere statistiche sulle modifiche alle righe |
| `include_history`   | int                                     | `0`         | Numero di commit recenti da includere            |
| `staged_only`       | bool                                    | `false`     | Mostrare solo le modifiche nello staging         |
| `include_untracked` | bool                                    | `true`      | Includere file non tracciati                     |
| `max_diff_lines`    | int                                     | `500`       | Limitare la dimensione del diff (0 = illimitato) |

**Restituisce:** Nome del branch, stato dei file (staging/non staging/non tracciati/conflitti), contenuto opzionale del diff, statistiche opzionali e cronologia opzionale dei commit.

### gac_commit

Genera un messaggio di commit alimentato dall'IA e opzionalmente esegue il commit.

**Parametri:**

| Parameter          | Type           | Default | Descrizione                                                           |
| ------------------ | -------------- | ------- | --------------------------------------------------------------------- |
| `stage_all`        | bool           | `false` | Mettere in staging tutte le modifiche prima del commit (`git add -A`) |
| `files`            | list[str]      | `[]`    | File specifici da mettere in staging                                  |
| `dry_run`          | bool           | `false` | Anteprima senza eseguire                                              |
| `message_only`     | bool           | `false` | Generare il messaggio senza fare commit                               |
| `push`             | bool           | `false` | Push al remoto dopo il commit                                         |
| `group`            | bool           | `false` | Dividere le modifiche in più commit logici                            |
| `one_liner`        | bool           | `false` | Messaggio di commit su una singola riga                               |
| `scope`            | string \| null | `null`  | Scope di commit convenzionale (auto-rilevato se non fornito)          |
| `hint`             | string         | `""`    | Contesto aggiuntivo per messaggi migliori                             |
| `model`            | string \| null | `null`  | Sovrascrivere il modello IA (`provider:model_name`)                   |
| `language`         | string \| null | `null`  | Sovrascrivere la lingua del messaggio di commit                       |
| `skip_secret_scan` | bool           | `false` | Saltare la scansione di sicurezza                                     |
| `no_verify`        | bool           | `false` | Saltare gli hook di pre-commit                                        |
| `auto_confirm`     | bool           | `false` | Saltare le conferme (richiesto per gli agenti)                        |

**Restituisce:** Stato di successo, messaggio di commit generato, hash del commit (se committato), lista dei file modificati e eventuali avvisi.

## Flussi di Lavoro

### Commit Base

```text
1. gac_status()                              → Vedere cosa è cambiato
2. gac_commit(stage_all=true, auto_confirm=true)  → Staging, generazione messaggio e commit
```

### Anteprima Prima del Commit

```text
1. gac_status(include_diff=true, include_stats=true)  → Esaminare le modifiche in dettaglio
2. gac_commit(stage_all=true, dry_run=true)            → Anteprima del messaggio di commit
3. gac_commit(stage_all=true, auto_confirm=true)       → Eseguire il commit
```

### Commit Raggruppati

```text
1. gac_status()                                           → Vedere tutte le modifiche
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Anteprima dei raggruppamenti logici
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Eseguire i commit raggruppati
```

### Commit con Contesto

```text
1. gac_status(include_history=5)  → Vedere i commit recenti come riferimento di stile
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Configurazione

Il server MCP utilizza la tua configurazione GAC esistente. Non è necessaria alcuna configurazione aggiuntiva oltre a:

1. **Provider e modello**: Esegui `gac init` o `gac model` per configurare il tuo provider IA
2. **Chiavi API**: Memorizzate in `~/.gac.env` (configurate durante `gac init`)
3. **Impostazioni opzionali**: Tutte le variabili d'ambiente GAC si applicano (`GAC_LANGUAGE`, `GAC_VERBOSE`, ecc.)

Consulta la [documentazione principale](USAGE.md#note-di-configurazione) per tutte le opzioni di configurazione.

## Risoluzione Problemi

### "No model configured"

Esegui `gac init` per configurare il tuo provider IA e il modello prima di usare il server MCP.

### "No staged changes found"

Metti in staging i file manualmente (`git add`) o usa `stage_all=true` nella chiamata a `gac_commit`.

### Il server non si avvia

Verifica che GAC sia installato e accessibile:

```bash
uvx gac --version
# o
gac --version
```

Se usi `uvx`, assicurati che `uv` sia installato e nel tuo PATH.

### L'agente non trova il server

Assicurati che il file di configurazione MCP sia nella posizione corretta per il tuo client e che il percorso del `command` sia accessibile dal tuo ambiente shell.

### Corruzione dell'output Rich

Il server MCP reindirizza automaticamente tutto l'output della console Rich su stderr per prevenire la corruzione del protocollo stdio. Se vedi output illeggibile, assicurati di eseguire `gac serve` (non `gac` direttamente) quando usi MCP.

## Vedi Anche

- [Documentazione Principale](USAGE.md)
- [Configurazione OAuth Claude Code](CLAUDE_CODE.md)
- [Guida alla Risoluzione Problemi](TROUBLESHOOTING.md)
- [Specifica MCP](https://modelcontextprotocol.io/)
