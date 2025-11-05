# Bruke Claude Code med GAC

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | **Norsk** | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC støtter autentisering via Claude Code-abonnementer, slik at du kan bruke ditt Claude Code-abonnement i stedet for å betale for den dyre Anthropic API-en. Dette er perfekt for brukere som allerede har tilgang til Claude Code via sitt abonnement.

## Hva er Claude Code?

Claude Code er Anthropics abonnementstjeneste som gir OAuth-basert tilgang til Claude-modeller. I stedet for å bruke API-nøkler (som faktureres per token), bruker Claude Code OAuth-tokens fra abonnementet ditt.

## Fordeler

- **Kostnadseffektivt**: Bruk ditt eksisterende Claude Code-abonnement i stedet for å betale separat for API-tilgang
- **Samme modeller**: Tilgang til de samme Claude-modellene (f.eks. `claude-sonnet-4-5`)
- **Separat fakturering**: Claude Code-bruk er atskilt fra Anthropic API-fakturering

## Oppsett

GAC inkluderer innebygd OAuth-autentisering for Claude Code. Oppsettsprosessen er fullstendig automatisert og vil åpne nettleseren din for autentisering.

### Alternativ 1: Under innledende oppsett (Anbefalt)

Når du kjører `gac init`, velg ganske enkelt "Claude Code" som din leverandør:

```bash
gac init
```

Veiviseren vil:

1. Be deg om å velge "Claude Code" fra leverandørlisten
2. Automatisk åpne nettleseren din for OAuth-autentisering
3. Lagre tilgangstokenen din i `~/.gac.env`
4. Sette standardmodellen

### Alternativ 2: Bytt til Claude Code senere

Hvis du allerede har GAC konfigurert med en annen leverandør og vil bytte til Claude Code:

```bash
gac model
```

Deretter:

1. Velg "Claude Code" fra leverandørlisten
2. Nettleseren din vil automatisk åpne for OAuth-autentisering
3. Token lagret i `~/.gac.env`
4. Modell konfigurert automatisk

### Bruk GAC normalt

Når du er autentisert, bruk GAC som vanlig:

```bash
# Stage endringene dine
git add .

# Generer og commit med Claude Code
gac

# Eller overstyr modellen for et enkelt commit
gac -m claude-code:claude-sonnet-4-5
```

## Tilgjengelige modeller

Claude Code gir tilgang til de samme modellene som Anthropic API-en. Nåværende Claude 4.5-familiemodeller inkluderer:

- `claude-sonnet-4-5` - Nyeste og mest intelligente Sonnet-modell, best for koding
- `claude-haiku-4-5` - Rask og effektiv
- `claude-opus-4-1` - Mest kapable modell for kompleks resonnering

Se [Claude-dokumentasjonen](https://docs.claude.com/en/docs/about-claude/models/overview) for fullstendig liste over tilgjengelige modeller.

## Feilsøking

### Token utløpt

Hvis du ser autentiseringsfeil, kan tokenen din ha utløpt. Reautentiser ved å kjøre:

```bash
gac model
```

Velg deretter "Claude Code" og velg "Reautentiser (få ny token)". Nettleseren din vil åpne for ny OAuth-autentisering.

### "CLAUDE_CODE_ACCESS_TOKEN ikke funnet"

Dette betyr at GAC ikke finner tilgangstokenen din. Autentiser ved å kjøre:

```bash
gac model
```

Velg deretter "Claude Code" fra leverandørlisten. OAuth-flyten vil starte automatisk.

### "Autentisering mislyktes"

Hvis OAuth-autentisering mislykkes:

1. Sørg for at du har et aktivt Claude Code-abonnement
2. Sjekk at nettleseren din åpnes korrekt
3. Prøv en annen nettleser hvis problemer vedvarer
4. Verifiser nettverkstilkobling til `claude.ai`
5. Sjekk at porter 8765-8795 er tilgjengelige for lokal callback-server

### Forskjeller fra Anthropic-leverandør

| Funksjon         | Anthropic (`anthropic:`)         | Claude Code (`claude-code:`)                                 |
| ---------------- | -------------------------------- | ------------------------------------------------------------ |
| Autentisering    | API-nøkkel (`ANTHROPIC_API_KEY`) | OAuth (automatisk nettleserflyt)                             |
| Fakturering      | Per-token API-fakturering        | Abonnementsbasert                                            |
| Oppsett          | Manuell API-nøkkeloppføring      | Automatisk OAuth via `gac init` eller `gac model`            |
| Token-håndtering | Langvarige API-nøkler            | OAuth-tokens (kan utløpe, enkel reautentisering via `model`) |
| Modeller         | Samme modeller                   | Samme modeller                                               |

## Sikkerhetsnotater

- **Aldri committ tilgangstokenen din** til versjonskontroll
- GAC lagrer automatisk tokens i `~/.gac.env` (utenfor prosjektmappen din)
- Tokens kan utløpe og vil kreve reautentisering via `gac model`
- OAuth-flyten bruker PKCE (Proof Key for Code Exchange) for økt sikkerhet
- Lokal callback-server kjører kun på localhost (porter 8765-8795)

## Se også

- [Hoveddokumentasjon](USAGE.md)
- [Feilsøkingsguide](TROUBLESHOOTING.md)
- [Claude Code-dokumentasjon](https://claude.ai/code)
