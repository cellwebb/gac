# Prompt di Sistema Personalizzati

**English** | [简体中文](../zh-CN/CUSTOM_SYSTEM_PROMPTS.md) | [繁體中文](../zh-TW/CUSTOM_SYSTEM_PROMPTS.md) | [日本語](../ja/CUSTOM_SYSTEM_PROMPTS.md) | [한국어](../ko/CUSTOM_SYSTEM_PROMPTS.md) | [हिन्दी](../hi/CUSTOM_SYSTEM_PROMPTS.md) | [Tiếng Việt](../vi/CUSTOM_SYSTEM_PROMPTS.md) | [Français](../fr/CUSTOM_SYSTEM_PROMPTS.md) | [Русский](../ru/CUSTOM_SYSTEM_PROMPTS.md) | [Español](../es/CUSTOM_SYSTEM_PROMPTS.md) | [Português](../pt/CUSTOM_SYSTEM_PROMPTS.md) | [Deutsch](../de/CUSTOM_SYSTEM_PROMPTS.md) | [Nederlands](../nl/CUSTOM_SYSTEM_PROMPTS.md) | **Italiano**

Questa guida ti aiuterà a creare prompt di sistema personalizzati per `gac` che generano messaggi di commit secondo il tuo stile preferito.

## Sommario

- [Prompt di Sistema Personalizzati](#prompt-di-sistema-personalizzati)
  - [Sommario](#sommario)
  - [Cos'è un Prompt di Sistema?](#cosè-un-prompt-di-sistema)
  - [Come Funziona](#come-funziona)
  - [Creare un Prompt Personalizzato](#creare-un-prompt-personalizzato)
    - [Struttura di Base](#struttura-di-base)
    - [Variabili Disponibili](#variabili-disponibili)
    - [Esempi di Prompt Personalizzati](#esempi-di-prompt-personalizzati)
  - [Template di Prompt Popolari](#template-di-prompt-popolari)
    - [1. Stile Minimalista](#1-stile-minimalista)
    - [2. Stile Tecnico Dettagliato](#2-stile-tecnico-dettagliato)
    - [3. Stile Agile/Scrum](#stile-agilescrum) <!-- markdownlint-disable-line MD051 -->
    - [4. Stile Convenzionale con Scope](#4-stile-convenzionale-con-scope)
    - [5. Stile Descrittivo](#5-stile-descrittivo)
  - [Best Practices](#best-practices)
  - [Risoluzione Problemi](#risoluzione-problemi)
    - [Prompt Non Funziona](#prompt-non-funziona)
    - [Output Troppo Lungo/Corto](#output-troppo-lungocorto)
    - [Lingua Non Corretta](#lingua-non-corretta)
  - [Esempi Reali dalla Comunità](#esempi-reali-dalla-comunità)

## Cos'è un Prompt di Sistema?

Un prompt di sistema è un'istruzione che dice al modello linguistico come comportarsi quando genera messaggi di commit. `gac` usa prompt di sistema per guidare l'AI a produrre messaggi di commit che seguono stili specifici, formati o convenzioni.

## Come Funziona

1. `gac` analizza le tue modifiche git (diff)
2. Costruisce un contesto che include il diff e altre informazioni rilevanti
3. Usa il prompt di sistema per istruire l'AI su come formattare il messaggio di commit
4. L'AI genera un messaggio di commit seguendo le tue linee guida

## Creare un Prompt Personalizzato

### Struttura di Base

Un prompt di sistema personalizzato dovrebbe includere:

1. **Istruzioni chiare** su come formattare i messaggi di commit
2. **Esempi** del formato desiderato
3. **Regole specifiche** per il tuo stile preferito
4. **Considerazioni sulla lingua** (se necessario)

### Variabili Disponibili

Il prompt può usare queste variabili che saranno sostituite con valori reali:

- `{{diff}}` - Il diff git effettivo delle modifiche
- `{{context}}` - Informazioni contestuali sul repository
- `{{language}}` - La lingua di output desiderata
- `{{format}}` - Il formato di output (one-liner, standard, verbose)

### Esempi di Prompt Personalizzati

#### Esempio Base

```text
Genera un messaggio di commit per le seguenti modifiche git in {{language}}.

Diff:
{{diff}}

Segui queste linee guida:
- Usa il formato conventional commit
- Sii conciso ma chiaro
- Spiega il "perché" dietro le modifiche
- Mantieni la prima riga sotto 72 caratteri

Esempio:
feat(auth): aggiungi supporto OAuth2

Implementa l'autenticazione OAuth2 per permettere l'accesso tramite provider terzi.
```

#### Esempio Avanzato

```text
Sei un esperto sviluppatore che scrive messaggi di commit professionali in {{language}}.

Analizza le seguenti modifiche:
{{diff}}

Requisiti:
1. Formato conventional commit con scope appropriato
2. Prima riga: tipo(scope): descrizione (massimo 72 caratteri)
3. Corpo: spiega cosa è cambiato e perché
4. Usa forma imperativa ("aggiungi" non "aggiunto")
5. Priorità: chiarezza > brevità

Tipi consentiti:
- feat: nuove funzionalità
- fix: correzioni di bug
- docs: documentazione
- style: formattazione (senza logica)
- refactor: refactoring
- test: test
- chore: manutenzione

{{#if verbose}}
Includi anche:
- Motivazione della modifica
- Impatto su altre parti del codebase
{{/if}}
```

## Template di Prompt Popolari

### 1. Stile Minimalista

```text
Crea un messaggio di commit conciso in {{language}} per questo diff:
{{diff}}

Requisiti:
- Massimo 50 caratteri nella prima riga
- Usa formato conventional commit
- Nessun corpo del messaggio
```

### 2. Stile Tecnico Dettagliato

````text
Genera un messaggio di commit tecnico dettagliato in {{language}}.

Contesto del repository:
{{context}}

Modifiche:
{{diff}}

Formato richiesto:
```text

tipo(scope): descrizione breve

Dettagli tecnici:

- Spiega l'approccio tecnico usato
- Menziona algoritmi o pattern importanti
- Nota implicazioni di performance
- Elenca file chiave modificati

````

Sii specifico sui dettagli di implementazione.

````text

### 3. Stile Agile/Scrum

```text
Crea un messaggio di commit in stile agile in {{language}}.

Analizza questo diff:
{{diff}}

Focus su:
- Valore per l'utente finale
- Funzionalità completata
- User story correlata (se applicabile)

Formato:
feat(story-ID): descrizione valore utente

Spiega come questa modifica contribuisce agli obiettivi sprint.
````

### 4. Stile Convenzionale con Scope

```text
Genera un conventional commit in {{language}} con scope automatico.

Diff:
{{diff}}

Regole:
1. Determina lo scope basato sui file modificati
2. Usa tipi standard: feat, fix, docs, style, refactor, test, chore
3. Formato: tipo(scope): descrizione
4. Scope comuni: auth, ui, api, db, config, utils

Esempi:
- auth: file di autenticazione
- ui: componenti interfaccia
- api: endpoint API
- db: schema database
- config: configurazione
- utils: funzioni utility
```

### 5. Stile Descrittivo

```text
Scrivi un messaggio di commit descrittivo in {{language}} che racconti una storia.

Modifiche:
{{diff}}

Crea una narrazione che:
1. Spiega il problema risolto
2. Descrive la soluzione implementata
3. Menziona il beneficio ottenuto

Usa linguaggio naturale ma professionale.
```

## Best Practices

### ✅ Fai Così

- **Sii specifico**: Istruzioni chiare producono risultati migliori
- **Fornisci esempi**: Mostra il formato desiderato
- **Considera il contesto**: Adatta il prompt al tuo tipo di progetto
- **Testa e itera**: Prova diversi prompt per trovare quello migliore
- **Mantieni semplice**: Prompt troppo complessi possono confondere l'AI

### ❌ Evita Questo

- **Istruzioni contraddittorie**: Non dare direttive opposte
- **Prompt troppo lunghi**: Mantieni sotto 2000 caratteri
- **Formato ambiguo**: Sii chiaro sulla struttura desiderata
- **Ignorare la lingua**: Specifica sempre la lingua di output

## Risoluzione Problemi

### Prompt Non Funziona

1. **Controlla la sintassi**: Assicurati che le variabili `{{...}}` siano corrette
2. **Verifica il percorso**: Il file deve essere nel percorso corretto
3. **Testa con un prompt semplice**: Inizia con qualcosa di base e complessifica gradualmente

### Output Troppo Lungo/Corto

1. **Aggiungi limiti di caratteri**: Specifica "massimo X caratteri"
2. **Sii più specifico**: Dettaglia meglio il formato desiderato
3. **Usa esempi**: Mostra esempi della lunghezza desiderata

### Lingua Non Corretta

1. **Verifica la variabile language**: Assicurati che `{{language}}` sia inclusa
2. **Specifica la lingua**: Aggiungi "scrivi in italiano" o simile
3. **Testa con diverse lingue**: Prova con lingue diverse per isolare il problema

## Esempi Reali dalla Comunità

### Esempio 1: Progetto React

```text
Genera un commit per un progetto React in {{language}}.

{{diff}}

Focus su:
- Componenti React modificati
- Cambiamenti di stato o props
- Hook personalizzati
- Modifiche al routing

Formato:
feat(component): descrizione

Usa scope specifici come:
- component: componenti React
- hook: hook personalizzati
- state: gestione stato
- routing: configurazione routing
```

### Esempio 2: API Backend

```text
Crea un commit per API backend in {{language}}.

{{diff}}

Enfasi su:
- Endpoint API modificati
- Schema database
- Logica di business
- Validazione dati

Formato:
tipo(api): descrizione endpoint

Scope consigliati:
- api: endpoint API
- db: schema/migrazioni database
- auth: autenticazione/autorizzazione
- validation: validazione dati
```

### Esempio 3: Progetto Python

```text
Genera commit per progetto Python in {{language}}.

{{diff}}

Considera:
- Moduli Python modificati
- Dipendenze (requirements.txt, pyproject.toml)
- Test unitari
- Configurazione

Formato standard PEP 8 con scope.

Scope comuni:
- core: logica principale
- utils: funzioni utility
- tests: test
- deps: dipendenze
- config: configurazione
```

---

## Prossimi Passi

1. **Scegli un template** di base da questa guida
2. **Personalizzalo** per le tue esigenze specifiche
3. **Testalo** su alcuni commit reali
4. **Affinalo** basandoti sui risultati
5. **Condividilo** con il team se funziona bene

Per più esempi e ispirazione, controlla la directory `examples/` nel repository gac.
