# Usare ChatGPT OAuth con GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC supporta l'autenticazione tramite ChatGPT OAuth, consentendoti di utilizzare il tuo abbonamento ChatGPT per accedere all'API Codex di OpenAI invece di pagare separatamente le chiavi API di OpenAI. Questo riflette lo stesso flusso OAuth utilizzato dal CLI Codex di OpenAI.

> ⚠️ **Attenzione — uso non autorizzato:** Questo utilizza lo stesso flusso OAuth del CLI Codex di OpenAI e, sebbene attualmente funzioni, OpenAI potrebbe limitare l'uso dei token di terze parti in qualsiasi momento. GAC è abbastanza piccolo da essere passato inosservato finora, ma l'uso di ChatGPT OAuth qui **non è ufficialmente approvato** per strumenti di terze parti e potrebbe smettere di funzionare in qualsiasi momento. Se hai bisogno di una generazione affidabile di messaggi di commit, usa un provider API diretto (`openai`, ecc.). Consulta la [documentazione Codex di OpenAI](https://openai.com/codex) per la politica attuale.

## Cos'è ChatGPT OAuth?

ChatGPT OAuth ti consente di sfruttare il tuo abbonamento esistente ChatGPT Plus o Pro per accedere all'API Codex per generare messaggi di commit. Invece di gestire chiavi API e fatturazione per token, ti autentichi una volta tramite il tuo browser e GAC gestisce automaticamente il ciclo di vita del token.

## Vantaggi

- **Conveniente**: Utilizza il tuo abbonamento esistente ChatGPT Plus/Pro invece di pagare separatamente per l'accesso API
- **Stessi modelli**: Accedi ai modelli ottimizzati per Codex (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **Nessuna gestione di chiavi API**: OAuth basato su browser significa che non ci sono chiavi API da ruotare o archiviare
- **Fatturazione separata**: L'uso di ChatGPT OAuth è separato dalla fatturazione API diretta di OpenAI

## Configurazione

GAC include l'autenticazione OAuth integrata per ChatGPT. Il processo di configurazione è completamente automatizzato e aprirà il tuo browser per l'autenticazione.

### Opzione 1: Durante la configurazione iniziale (Consigliato)

Quando esegui `gac init`, seleziona semplicemente «ChatGPT OAuth» come tuo provider:

```bash
gac init
```

La procedura guidata:

1. Ti chiederà di selezionare «ChatGPT OAuth» dall'elenco dei provider
2. Aprirà automaticamente il tuo browser per l'autenticazione OAuth
3. Salverà il tuo token di accesso in `~/.gac/oauth/chatgpt-oauth.json`
4. Imposterà il modello predefinito

### Opzione 2: Passa a ChatGPT OAuth in seguito

Se hai già configurato GAC con un altro provider e vuoi passare a ChatGPT OAuth:

```bash
gac model
```

Poi:

1. Seleziona «ChatGPT OAuth» dall'elenco dei provider
2. Il tuo browser si aprirà automaticamente per l'autenticazione OAuth
3. Token salvato in `~/.gac/oauth/chatgpt-oauth.json`
4. Modello configurato automaticamente

### Usa GAC normalmente

Una volta autenticato, usa GAC come al solito:

```bash
# Prepara le tue modifiche
git add .

# Genera ed esegui il commit con ChatGPT OAuth
gac

# Oppure sovrascrivi il modello per un singolo commit
gac -m chatgpt-oauth:gpt-5.5
```

## Modelli disponibili

ChatGPT OAuth fornisce accesso a modelli ottimizzati per Codex. I modelli attuali includono:

- `gpt-5.5` — Modello Codex più recente e potente
- `gpt-5.4` — Modello Codex di generazione precedente
- `gpt-5.3-codex` — Modello Codex di terza generazione

Consulta la [documentazione OpenAI](https://platform.openai.com/docs/models) per l'elenco completo dei modelli disponibili.

## Comandi CLI

GAC fornisce comandi CLI dedicati per la gestione di ChatGPT OAuth:

### Accedi

Autenticati o riautenticati con ChatGPT OAuth:

```bash
gac auth chatgpt login
```

Il tuo browser si aprirà automaticamente per completare il flusso OAuth. Se sei già autenticato, questo aggiornerà i tuoi token.

### Disconnettiti

Rimuovi i token ChatGPT OAuth archiviati:

```bash
gac auth chatgpt logout
```

Questo elimina il file token archiviato in `~/.gac/oauth/chatgpt-oauth.json`.

### Stato

Controlla il tuo stato di autenticazione ChatGPT OAuth corrente:

```bash
gac auth chatgpt status
```

Oppure controlla tutti i provider in una volta:

```bash
gac auth
```

## Risoluzione dei problemi

### Token scaduto

Se vedi errori di autenticazione, il tuo token potrebbe essere scaduto. Riautenticati eseguendo:

```bash
gac auth chatgpt login
```

Il tuo browser si aprirà automaticamente per una nuova autenticazione OAuth. GAC utilizza automaticamente i token di aggiornamento per rinnovare l'accesso senza riautenticazione quando possibile.

### Controlla lo stato di autenticazione

Per verificare se sei attualmente autenticato:

```bash
gac auth chatgpt status
```

Oppure controlla tutti i provider in una volta:

```bash
gac auth
```

### Disconnettiti

Per rimuovere il tuo token archiviato:

```bash
gac auth chatgpt logout
```

### «Token ChatGPT OAuth non trovato»

Ciò significa che GAC non riesce a trovare il tuo token di accesso. Autenticati eseguendo:

```bash
gac model
```

Poi seleziona «ChatGPT OAuth» dall'elenco dei provider. Il flusso OAuth si avvierà automaticamente.

### «Autenticazione fallita»

Se l'autenticazione OAuth fallisce:

1. Assicurati di avere un abbonamento ChatGPT Plus o Pro attivo
2. Controlla che il tuo browser si apra correttamente
3. Prova un browser diverso se i problemi persistono
4. Verifica la connettività di rete a `auth.openai.com`
5. Controlla che le porte 1455-1465 siano disponibili per il server di callback locale

### Porta già in uso

Il server di callback OAuth prova automaticamente le porte 1455-1465. Se tutte le porte sono occupate:

```bash
# Su macOS/Linux:
lsof -ti:1455-1465 | xargs kill -9

# Su Windows (PowerShell):
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Poi esegui di nuovo `gac auth chatgpt login`.

## Differenze rispetto al provider OpenAI

| Funzionalità   | OpenAI (`openai:`)                   | ChatGPT OAuth (`chatgpt-oauth:`)                                  |
| -------------- | ------------------------------------ | ----------------------------------------------------------------- |
| Autenticazione | Chiave API (`OPENAI_API_KEY`)        | OAuth (flusso browser automatizzato)                              |
| Fatturazione   | Fatturazione API per token           | Basata su abbonamento (ChatGPT Plus/Pro)                          |
| Configurazione | Inserimento manuale della chiave API | OAuth automatico tramite `gac init` o `gac model`                 |
| Gestione token | Chiavi API di lunga durata           | Token OAuth (aggiornamento automatico con token di aggiornamento) |
| Modelli        | Tutti i modelli OpenAI               | Modelli ottimizzati per Codex                                     |

## Note sulla sicurezza

- **Non eseguire mai il commit del tuo token di accesso** nel controllo versione
- GAC archivia i token OAuth in `~/.gac/oauth/chatgpt-oauth.json` (al di fuori della directory del progetto)
- Il flusso OAuth utilizza PKCE (Proof Key for Code Exchange) per una maggiore sicurezza
- Il server di callback locale viene eseguito solo su localhost (porte 1455-1465)
- I token di aggiornamento vengono utilizzati per rinnovare automaticamente l'accesso senza riautenticazione

## Vedi anche

- [Documentazione principale](USAGE.md)
- [Guida alla risoluzione dei problemi](TROUBLESHOOTING.md)
- [Documentazione Codex di OpenAI](https://openai.com/codex)
