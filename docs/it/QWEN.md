[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | **Italiano**

# Utilizzare Qwen.ai con GAC

GAC supporta l'autenticazione tramite Qwen.ai OAuth, consentendoti di utilizzare il tuo account Qwen.ai per la generazione di messaggi di commit. Questo utilizza l'autenticazione del flusso del dispositivo OAuth per un'esperienza di accesso senza interruzioni.

## Cos'è Qwen.ai?

Qwen.ai è la piattaforma AI di Alibaba Cloud che fornisce accesso alla famiglia Qwen di modelli linguistici di grandi dimensioni. GAC supporta l'autenticazione basata su OAuth, consentendoti di utilizzare il tuo account Qwen.ai senza dover gestire manualmente le chiavi API.

## Vantaggi

- **Autenticazione semplice**: Flusso del dispositivo OAuth - accedi semplicemente con il tuo browser
- **Nessuna gestione delle chiavi API**: L'autenticazione è gestita automaticamente
- **Accesso ai modelli Qwen**: Utilizza potenti modelli Qwen per la generazione di messaggi di commit

## Configurazione

GAC include l'autenticazione OAuth integrata per Qwen.ai utilizzando il flusso del dispositivo. Il processo di configurazione visualizzerà un codice e aprirà il browser per l'autenticazione.

### Opzione 1: Durante la configurazione iniziale (Consigliato)

Quando esegui `gac init`, seleziona semplicemente "Qwen.ai (OAuth)" come provider:

```bash
gac init
```

La procedura guidata:

1. Ti chiederà di selezionare "Qwen.ai (OAuth)" dall'elenco dei provider
2. Visualizzerà un codice dispositivo e aprirà il browser
3. Ti autenticherai su Qwen.ai e inserirai il codice
4. Salverà il tuo token di accesso in modo sicuro
5. Imposterà il modello predefinito

### Opzione 2: Passare a Qwen.ai in seguito

Se hai già configurato GAC con un altro provider e desideri passare a Qwen.ai:

```bash
gac model
```

Quindi:

1. Seleziona "Qwen.ai (OAuth)" dall'elenco dei provider
2. Segui il flusso di autenticazione del codice dispositivo
3. Token salvato in modo sicuro in `~/.gac/oauth/qwen.json`
4. Modello configurato automaticamente

### Opzione 3: Accesso diretto

Puoi anche autenticarti direttamente utilizzando:

```bash
gac auth qwen login
```

Questo:

1. Visualizzerà un codice dispositivo
2. Aprirà il browser alla pagina di autenticazione di Qwen.ai
3. Dopo l'autenticazione, il token viene salvato automaticamente

### Utilizzare GAC normalmente

Una volta autenticato, utilizza GAC come di consueto:

```bash
# Metti in stage le tue modifiche
git add .

# Genera e committa con Qwen.ai
gac

# O sovrascrivi il modello per un singolo commit
gac -m qwen:qwen3-coder-plus
```

## Modelli disponibili

L'integrazione Qwen.ai OAuth utilizza:

- `qwen3-coder-plus` - Ottimizzato per attività di codifica (predefinito)

Questo è il modello disponibile tramite l'endpoint OAuth portal.qwen.ai. Per altri modelli Qwen, considera l'utilizzo del provider OpenRouter che offre opzioni aggiuntive per i modelli Qwen.

## Comandi di autenticazione

GAC fornisce diversi comandi per gestire l'autenticazione Qwen.ai:

```bash
# Accedi a Qwen.ai
gac auth qwen login

# Controlla lo stato dell'autenticazione
gac auth qwen status

# Disconnettiti e rimuovi il token memorizzato
gac auth qwen logout

# Controlla lo stato di tutti i provider OAuth
gac auth
```

### Opzioni di accesso

```bash
# Accesso standard (apre il browser automaticamente)
gac auth qwen login

# Accesso senza aprire il browser (visualizza l'URL da visitare manualmente)
gac auth qwen login --no-browser

# Modalità silenziosa (output minimo)
gac auth qwen login --quiet
```

## Risoluzione dei problemi

### Token scaduto

Se visualizzi errori di autenticazione, il tuo token potrebbe essere scaduto. Autenticati nuovamente eseguendo:

```bash
gac auth qwen login
```

Il flusso del codice dispositivo verrà avviato e il browser si aprirà per la riautenticazione.

### Controlla lo stato dell'autenticazione

Per verificare se sei attualmente autenticato:

```bash
gac auth qwen status
```

O controlla tutti i provider contemporaneamente:

```bash
gac auth
```

### Disconnessione

Per rimuovere il token memorizzato:

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (Autenticazione Qwen non trovata)

Ciò significa che GAC non riesce a trovare il tuo token di accesso. Autenticati eseguendo:

```bash
gac auth qwen login
```

O esegui `gac model` e seleziona "Qwen.ai (OAuth)" dall'elenco dei provider.

### "Authentication failed" (Autenticazione fallita)

Se l'autenticazione OAuth fallisce:

1. Assicurati di avere un account Qwen.ai
2. Verifica che il browser si apra correttamente
3. Verifica di aver inserito correttamente il codice dispositivo
4. Prova un browser diverso se i problemi persistono
5. Verifica la connettività di rete a `qwen.ai`

### Il codice dispositivo non funziona

Se l'autenticazione del codice dispositivo non funziona:

1. Assicurati che il codice non sia scaduto (i codici sono validi per un tempo limitato)
2. Prova a eseguire nuovamente `gac auth qwen login` per ottenere un nuovo codice
3. Utilizza il flag `--no-browser` e visita manualmente l'URL se l'apertura del browser fallisce

## Note di sicurezza

- **Non committare mai il tuo token di accesso** nel controllo versione
- GAC memorizza automaticamente i token in `~/.gac/oauth/qwen.json` (fuori dalla directory del progetto)
- I file dei token hanno autorizzazioni limitate (leggibili solo dal proprietario)
- I token possono scadere e richiederanno la riautenticazione
- Il flusso del dispositivo OAuth è progettato per l'autenticazione sicura su sistemi headless

## Vedi anche

- [Documentazione principale](USAGE.md)
- [Configurazione di Claude Code](CLAUDE_CODE.md)
- [Guida alla risoluzione dei problemi](TROUBLESHOOTING.md)
- [Documentazione Qwen.ai](https://qwen.ai)
