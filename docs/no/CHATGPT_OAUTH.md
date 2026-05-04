# Bruke ChatGPT OAuth med GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC støtter autentisering via ChatGPT OAuth, slik at du kan bruke ditt ChatGPT-abonnement for å få tilgang til OpenAI's Codex API i stedet for å betale for OpenAI API-nøkler separat. Dette gjenspeiler den samme OAuth-flyten som brukes av OpenAI's Codex CLI.

> ⚠️ **Merk — uautorisert bruk:** Dette bruker den samme OAuth-flyten som OpenAI's Codex CLI, og selv om det fungerer for øyeblikket, kan OpenAI når som helst begrense tredjeparts tokenbruk. GAC er lite nok til at det har flydd under radaren så langt, men bruk av ChatGPT OAuth her er **ikke offisielt godkjent** for tredjepartsverktøy og kan slutte å fungere når som helst. Hvis du trenger pålitelig generering av commit-meldinger, bruk en direkte API-leverandør (`openai` osv.). Se [OpenAI's Codex-dokumentasjon](https://openai.com/codex) for gjeldende retningslinjer.

## Hva er ChatGPT OAuth?

ChatGPT OAuth lar deg dra nytte av ditt eksisterende ChatGPT Plus- eller Pro-abonnement for å få tilgang til Codex API for å generere commit-meldinger. I stedet for å administrere API-nøkler og tokenbasert fakturering, autentiserer du deg én gang via nettleseren din, og GAC håndterer tokenets livssyklus automatisk.

## Fordeler

- **Kostnadseffektivt**: Bruk ditt eksisterende ChatGPT Plus/Pro-abonnement i stedet for å betale separat for API-tilgang
- **Samme modeller**: Få tilgang til Codex-optimaliserte modeller (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **Ingen API-nøkkeladministrasjon**: Nettleserbasert OAuth betyr at det ikke er noen API-nøkler som må roteres eller lagres
- **Separat fakturering**: ChatGPT OAuth-bruk er separat fra direkte OpenAI API-fakturering

## Oppsett

GAC inkluderer innebygd OAuth-autentisering for ChatGPT. Oppsettsprosessen er helt automatisert og vil åpne nettleseren din for autentisering.

### Alternativ 1: Under første gangs oppsett (Anbefalt)

Når du kjører `gac init`, velger du ganske enkelt «ChatGPT OAuth» som leverandøren din:

```bash
gac init
```

Veiviseren vil:

1. Be deg om å velge «ChatGPT OAuth» fra leverandørlisten
2. Automatisk åpne nettleseren din for OAuth-autentisering
3. Lagre tilgangstokenet ditt i `~/.gac/oauth/chatgpt-oauth.json`
4. Angi standardmodellen

### Alternativ 2: Bytt til ChatGPT OAuth senere

Hvis du allerede har konfigurert GAC med en annen leverandør og vil bytte til ChatGPT OAuth:

```bash
gac model
```

Deretter:

1. Velg «ChatGPT OAuth» fra leverandørlisten
2. Nettleseren din åpnes automatisk for OAuth-autentisering
3. Token lagret i `~/.gac/oauth/chatgpt-oauth.json`
4. Modell konfigurert automatisk

### Bruk GAC som normalt

Når du er autentisert, bruker du GAC som vanlig:

```bash
# Scene endringene dine
git add .

# Generer og commit med ChatGPT OAuth
gac

# Eller overstyr modellen for én enkelt commit
gac -m chatgpt-oauth:gpt-5.5
```

## Tilgjengelige modeller

ChatGPT OAuth gir tilgang til Codex-optimaliserte modeller. Nåværende modeller inkluderer:

- `gpt-5.5` — Nyeste og mest kraftfulle Codex-modell
- `gpt-5.4` — Forrige generasjons Codex-modell
- `gpt-5.3-codex` — Tredje generasjons Codex-modell

Sjekk [OpenAI-dokumentasjonen](https://platform.openai.com/docs/models) for fullstendig liste over tilgjengelige modeller.

## CLI-kommandoer

GAC tilbyr dedikerte CLI-kommandoer for ChatGPT OAuth-administrasjon:

### Logg inn

Autentiser eller re-autentiser med ChatGPT OAuth:

```bash
gac auth chatgpt login
```

Nettleseren din åpnes automatisk for å fullføre OAuth-flyten. Hvis du allerede er autentisert, vil dette oppdatere tokenene dine.

### Logg ut

Fjern lagrede ChatGPT OAuth-token:

```bash
gac auth chatgpt logout
```

Dette sletter den lagrede tokenfilen på `~/.gac/oauth/chatgpt-oauth.json`.

### Status

Sjekk din nåværende ChatGPT OAuth-autentiseringsstatus:

```bash
gac auth chatgpt status
```

Eller sjekk alle leverandører på én gang:

```bash
gac auth
```

## Feilsøking

### Token utløpt

Hvis du ser autentiseringsfeil, kan tokenet ditt ha utløpt. Re-autentiser ved å kjøre:

```bash
gac auth chatgpt login
```

Nettleseren din åpnes automatisk for ny OAuth-autentisering. GAC bruker automatisk oppdateringstokens for å fornye tilgang uten re-autentisering når mulig.

### Sjekk autentiseringsstatus

For å sjekke om du for øyeblikket er autentisert:

```bash
gac auth chatgpt status
```

Eller sjekk alle leverandører på én gang:

```bash
gac auth
```

### Logg ut

For å fjerne det lagrede tokenet ditt:

```bash
gac auth chatgpt logout
```

### «ChatGPT OAuth-token ikke funnet»

Dette betyr at GAC ikke kan finne tilgangstokenet ditt. Autentiser ved å kjøre:

```bash
gac model
```

Velg deretter «ChatGPT OAuth» fra leverandørlisten. OAuth-flyten starter automatisk.

### «Autentisering mislyktes»

Hvis OAuth-autentisering mislykkes:

1. Sørg for at du har et aktivt ChatGPT Plus- eller Pro-abonnement
2. Sjekk at nettleseren din åpnes riktig
3. Prøv en annen nettleser hvis problemene vedvarer
4. Bekreft nettverkstilkobling til `auth.openai.com`
5. Sjekk at portene 1455-1465 er tilgjengelige for den lokale callback-serveren

### Port allerede i bruk

OAuth-callback-serveren prøver automatisk portene 1455-1465. Hvis alle porter er opptatt:

```bash
# På macOS/Linux:
lsof -ti:1455-1465 | xargs kill -9

# På Windows (PowerShell):
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Kjør deretter `gac auth chatgpt login` på nytt.

## Forskjeller fra OpenAI-leverandøren

| Funksjon        | OpenAI (`openai:`)            | ChatGPT OAuth (`chatgpt-oauth:`)                             |
| --------------- | ----------------------------- | ------------------------------------------------------------ |
| Autentisering   | API-nøkkel (`OPENAI_API_KEY`) | OAuth (automatisert nettleserflyt)                           |
| Fakturering     | Tokenbasert API-fakturering   | Abonnementsbasert (ChatGPT Plus/Pro)                         |
| Oppsett         | Manuell API-nøkkelinndata     | Automatisk OAuth via `gac init` eller `gac model`            |
| Tokenhåndtering | Langlevde API-nøkler          | OAuth-tokens (automatisk oppdatering med oppdateringstokens) |
| Modeller        | Alle OpenAI-modeller          | Codex-optimaliserte modeller                                 |

## Sikkerhetsmerknader

- **Aldri commit tilgangstokenet ditt** til versjonskontroll
- GAC lagrer OAuth-tokens i `~/.gac/oauth/chatgpt-oauth.json` (utenfor prosjektkatalogen din)
- OAuth-flyten bruker PKCE (Proof Key for Code Exchange) for bedre sikkerhet
- Lokal callback-server kjører kun på localhost (porter 1455-1465)
- Oppdateringstokens brukes til å automatisk fornye tilgang uten re-autentisering

## Se også

- [Hoveddokumentasjon](USAGE.md)
- [Feilsøkingsveiledning](TROUBLESHOOTING.md)
- [OpenAI's Codex-dokumentasjon](https://openai.com/codex)
