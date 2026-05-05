# Usare GitHub Copilot con GAC

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | **Italiano**

GAC supporta l'autenticazione tramite GitHub Copilot, consentendoti di utilizzare il tuo abbonamento Copilot per accedere a modelli di OpenAI, Anthropic, Google e altro — tutto incluso nel tuo piano GitHub Copilot.

## Cos'è GitHub Copilot OAuth?

GitHub Copilot OAuth utilizza il **Device Flow** — un metodo di autenticazione sicuro basato su browser che non richiede un server di callback locale. Visiti un URL, inserisci un codice monouso e autorizzi GAC a usare il tuo accesso Copilot. Dietro le quinte, GAC scambia il tuo token OAuth GitHub di lunga durata con token di sessione Copilot di breve durata (~30 min) che concedono l'accesso all'API Copilot.

Questo ti dà accesso a modelli di più provider tramite un singolo abbonamento:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Vantaggi

- **Accesso multi-provider**: Usa modelli di OpenAI, Anthropic e Google tramite un singolo abbonamento
- **Conveniente**: Usa il tuo abbonamento Copilot esistente invece di pagare chiavi API separate
- **Nessuna gestione di chiavi API**: Autenticazione Device Flow — nessuna chiave da ruotare o archiviare
- **Supporto GitHub Enterprise**: Funziona con istanze GHE tramite il flag `--host`

## Configurazione

### Opzione 1: Durante la configurazione iniziale (Consigliato)

Quando esegui `gac init`, seleziona semplicemente «Copilot» come tuo provider:

```bash
gac init
```

La procedura guidata:

1. Ti chiederà di selezionare «Copilot» dall'elenco dei provider
2. Mostrerà un codice monouso e aprirà il tuo browser per l'autenticazione Device Flow
3. Salverà il tuo token OAuth in `~/.gac/oauth/copilot.json`
4. Imposterà il modello predefinito

### Opzione 2: Passa a Copilot in seguito

Se hai già configurato GAC con un altro provider:

```bash
gac model
```

Poi seleziona «Copilot» dall'elenco dei provider e autenticati.

### Opzione 3: Login diretto

Autenticati direttamente senza cambiare il tuo modello predefinito:

```bash
gac auth copilot login
```

### Usa GAC normalmente

Una volta autenticato, usa GAC come al solito:

```bash
# Prepara le tue modifiche
git add .

# Genera ed esegui il commit con Copilot
gac

# Oppure sovrascrivi il modello per un singolo commit
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Modelli disponibili

Copilot fornisce accesso a modelli di più provider. I modelli attuali includono:

| Provider  | Modelli                                                                                        |
| --------- | ---------------------------------------------------------------------------------------------- |
| OpenAI    | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google    | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Nota:** L'elenco dei modelli mostrato dopo il login è informativo e potrebbe diventare obsoleto man mano che GitHub aggiunge nuovi modelli. Consulta la [documentazione GitHub Copilot](https://docs.github.com/en/copilot) per i modelli disponibili più recenti.

## GitHub Enterprise

Per autenticarti con un'istanza GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC utilizzerà automaticamente gli endpoint Device Flow e API corretti per la tua istanza GHE. Il token di sessione viene memorizzato nella cache per host, quindi diverse istanze GHE vengono gestite indipendentemente.

## Comandi CLI

GAC fornisce comandi CLI dedicati per la gestione dell'autenticazione Copilot:

### Accedi

Autenticati o riautenticati con GitHub Copilot:

```bash
gac auth copilot login
```

Il tuo browser si aprirà su una pagina Device Flow dove inserisci un codice monouso. Se sei già autenticato, ti verrà chiesto se desideri riautenticarti.

Per GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Disconnettiti

Rimuovi i token Copilot memorizzati:

```bash
gac auth copilot logout
```

Questo elimina il file token memorizzato in `~/.gac/oauth/copilot.json` e la cache di sessione.

### Stato

Controlla il tuo stato di autenticazione Copilot corrente:

```bash
gac auth copilot status
```

Oppure controlla tutti i provider in una volta:

```bash
gac auth
```

## Come Funziona

Il flusso di autenticazione Copilot differisce dall'OAuth di ChatGPT e Claude Code:

1. **Device Flow** — GAC richiede un codice dispositivo a GitHub e lo mostra
2. **Autorizzazione browser** — Visiti l'URL e inserisci il codice
3. **Polling del token** — GAC esegue il polling di GitHub finché non completi l'autorizzazione
4. **Scambio token di sessione** — Il token OAuth GitHub viene scambiato con un token di sessione Copilot di breve durata
5. **Aggiornamento automatico** — I token di sessione (~30 min) vengono rinnovati automaticamente dal token OAuth memorizzato nella cache

A differenza dell'OAuth basato su PKCE (ChatGPT/Claude Code), il Device Flow non richiede un server di callback locale né la gestione delle porte.

## Risoluzione dei problemi

### «Autenticazione Copilot non trovata»

Esegui il comando di login per autenticarti:

```bash
gac auth copilot login
```

### «Impossibile ottenere il token di sessione Copilot»

Questo significa che GAC ha ottenuto un token OAuth GitHub ma non ha potuto scambiarlo con un token di sessione Copilot. Di solito significa:

1. **Nessun abbonamento Copilot** — Il tuo account GitHub non ha un abbonamento Copilot attivo
2. **Token revocato** — Il token OAuth è stato revocato; riautenticati con `gac auth copilot login`

### Token di sessione scaduto

I token di sessione scadono dopo ~30 minuti. GAC li rinnova automaticamente dal token OAuth memorizzato nella cache, quindi non dovresti aver bisogno di riautenticarti frequentemente. Se l'aggiornamento automatico fallisce:

```bash
gac auth copilot login
```

### «Hostname non valido o non sicuro»

Il flag `--host` valida rigorosamente gli hostname per prevenire attacchi SSRF. Se vedi questo errore:

- Assicurati che l'hostname non includa porte (es. usa `ghe.company.com` non `ghe.company.com:8080`)
- Non includere protocolli o percorsi (es. usa `ghe.company.com` non `https://ghe.company.com/api`)
- Gli indirizzi IP privati e `localhost` sono bloccati per motivi di sicurezza

### Problemi con GitHub Enterprise

Se l'autenticazione GHE fallisce:

1. Verifica che la tua istanza GHE abbia Copilot abilitato
2. Controlla che l'hostname del tuo GHE sia accessibile dalla tua macchina
3. Assicurati che il tuo account GHE abbia una licenza Copilot
4. Prova con il flag `--host` esplicitamente: `gac auth copilot login --host ghe.mycompany.com`

## Differenze rispetto ad altri provider OAuth

| Funzionalità    | ChatGPT OAuth               | Claude Code             | Copilot                                      |
| --------------- | --------------------------- | ----------------------- | -------------------------------------------- |
| Metodo di auth  | PKCE (callback browser)     | PKCE (callback browser) | Device Flow (codice monouso)                 |
| Server callback | Porte 1455-1465             | Porte 8765-8795         | Non necessario                               |
| Durata token    | Lunga durata (auto-refresh) | In scadenza (ri-auth)   | Sessione ~30 min (auto-refresh)              |
| Modelli         | OpenAI ottimizzato Codex    | Famiglia Claude         | Multi-provider (OpenAI + Anthropic + Google) |
| Supporto GHE    | No                          | No                      | Sì (flag `--host`)                           |

## Note sulla sicurezza

- **Non eseguire mai il commit del tuo token OAuth** nel controllo versione
- GAC archivia i token OAuth in `~/.gac/oauth/copilot.json` (al di fuori della directory del progetto)
- I token di sessione vengono memorizzati nella cache in `~/.gac/oauth/copilot_session.json` con permessi `0o600`
- Gli hostname sono convalidati rigorosamente per prevenire attacchi SSRF e URL injection
- Gli indirizzi IP privati, gli indirizzi di loopback e `localhost` sono bloccati come hostname
- Il Device Flow non espone alcuna porta locale, riducendo la superficie di attacco

## Vedi anche

- [Documentazione principale](USAGE.md)
- [Guida alla risoluzione dei problemi](TROUBLESHOOTING.md)
- [Guida ChatGPT OAuth](CHATGPT_OAUTH.md)
- [Guida Claude Code](CLAUDE_CODE.md)
- [Documentazione GitHub Copilot](https://docs.github.com/en/copilot)
