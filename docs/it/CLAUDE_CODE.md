# Usare Claude Code con GAC

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | **Italiano**

GAC supporta l'autenticazione tramite abbonamenti Claude Code, permettendoti di usare il tuo abbonamento Claude Code invece di pagare per l'API Anthropic costosa. Questo è perfetto per utenti che hanno già accesso a Claude Code tramite il loro abbonamento.

## Cos'è Claude Code?

Claude Code è il servizio di abbonamento di Anthropic che fornisce accesso ai modelli Claude basato su OAuth. Invece di usare chiavi API (che vengono fatturate per token), Claude Code usa token OAuth dal tuo abbonamento.

## Vantaggi

- **Conveniente**: Usa il tuo abbonamento Claude Code esistente invece di pagare separatamente per l'accesso API
- **Stessi modelli**: Accedi agli stessi modelli Claude (es. `claude-sonnet-4-5`)
- **Fatturazione separata**: L'uso di Claude Code è separato dalla fatturazione API Anthropic

## Configurazione

GAC include autenticazione OAuth integrata per Claude Code. Il processo di configurazione è completamente automatizzato e aprirà il tuo browser per l'autenticazione.

### Opzione 1: Durante la configurazione iniziale (Raccomandato)

Quando esegui `gac init`, seleziona semplicemente "Claude Code" come tuo provider:

```bash
gac init
```

La procedura guidata:

1. Ti chiederà di selezionare "Claude Code" dall'elenco dei provider
2. Aprirà automaticamente il tuo browser per l'autenticazione OAuth
3. Salverà il tuo token di accesso in `~/.gac.env`
4. Imposterà il modello predefinito

### Opzione 2: Passare a Claude Code in seguito

Se hai già configurato GAC con un altro provider e vuoi passare a Claude Code:

```bash
gac model
```

Quindi:

1. Seleziona "Claude Code" dall'elenco dei provider
2. Il tuo browser si aprirà automaticamente per l'autenticazione OAuth
3. Token salvato in `~/.gac.env`
4. Modello configurato automaticamente

### Usare GAC normalmente

Una volta autenticato, usa GAC come al solito:

```bash
# Metti in stage le tue modifiche
git add .

# Genera e fai il commit con Claude Code
gac

# O sovrascrivi il modello per un singolo commit
gac -m claude-code:claude-sonnet-4-5
```

## Modelli disponibili

Claude Code fornisce accesso agli stessi modelli dell'API Anthropic. I modelli attuali della famiglia Claude 4.5 includono:

- `claude-sonnet-4-5` - Modello Sonnet più recente e intelligente, migliore per la codifica
- `claude-haiku-4-5` - Veloce ed efficiente
- `claude-opus-4-1` - Modello più capace per ragionamento complesso

Consulta la [documentazione di Claude](https://docs.claude.com/en/docs/about-claude/models/overview) per l'elenco completo dei modelli disponibili.

## Risoluzione dei problemi

### Token scaduto

Se vedi errori di autenticazione, il tuo token potrebbe essere scaduto. Ri-autenticati eseguendo:

```bash
gac model
```

Quindi seleziona "Claude Code" e scegli "Ri-autenticazione (ottenere nuovo token)". Il tuo browser si aprirà per nuova autenticazione OAuth.

### "CLAUDE_CODE_ACCESS_TOKEN non trovato"

Questo significa che GAC non può trovare il tuo token di accesso. Autenticati eseguendo:

```bash
gac model
```

Quindi seleziona "Claude Code" dall'elenco dei provider. Il flusso OAuth inizierà automaticamente.

### "Autenticazione fallita"

Se l'autenticazione OAuth fallisce:

1. Assicurati di avere un abbonamento Claude Code attivo
2. Verifica che il tuo browser si apra correttamente
3. Prova un browser diverso se i problemi persistono
4. Verifica la connettività di rete a `claude.ai`
5. Verifica che le porte 8765-8795 siano disponibili per il server di callback locale

## Differenze dal provider Anthropic

| Funzionalità   | Anthropic (`anthropic:`)         | Claude Code (`claude-code:`)                                            |
| -------------- | -------------------------------- | ----------------------------------------------------------------------- |
| Autenticazione | Chiave API (`ANTHROPIC_API_KEY`) | OAuth (flusso browser automatico)                                       |
| Fatturazione   | Fatturazione API per token       | Basata su abbonamento                                                   |
| Configurazione | Inserimento manuale chiave API   | OAuth automatico tramite `gac init` o `gac model`                       |
| Gestione token | Chiavi API a lungo termine       | Token OAuth (possono scadere, facile ri-autenticazione tramite `model`) |
| Modelli        | Stessi modelli                   | Stessi modelli                                                          |

## Note sulla sicurezza

- **Non fare mai commit del tuo token di accesso** nel controllo versione
- GAC memorizza automaticamente i token in `~/.gac.env` (fuori dalla tua directory di progetto)
- I token possono scadere e richiederanno ri-autenticazione tramite `gac model`
- Il flusso OAuth usa PKCE (Proof Key for Code Exchange) per sicurezza migliorata
- Il server di callback locale viene eseguito solo su localhost (porte 8765-8795)

## Vedi anche

- [Documentazione principale](USAGE.md)
- [Guida alla risoluzione dei problemi](TROUBLESHOOTING.md)
- [Documentazione Claude Code](https://claude.ai/code)
