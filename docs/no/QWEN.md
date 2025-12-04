[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | **Norsk** | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# Bruke Qwen.ai med GAC

GAC støtter autentisering via Qwen.ai OAuth, slik at du kan bruke din Qwen.ai-konto for generering av commit-meldinger. Dette bruker OAuth-enhetsflytautentisering for en sømløs påloggingsopplevelse.

## Hva er Qwen.ai?

Qwen.ai er Alibaba Clouds AI-plattform som gir tilgang til Qwen-familien av store språkmodeller. GAC støtter OAuth-basert autentisering, slik at du kan bruke din Qwen.ai-konto uten å måtte administrere API-nøkler manuelt.

## Fordeler

- **Enkel autentisering**: OAuth-enhetsflyt - bare logg inn med nettleseren din
- **Ingen API-nøkkelhåndtering**: Autentisering håndteres automatisk
- **Tilgang til Qwen-modeller**: Bruk kraftige Qwen-modeller for generering av commit-meldinger

## Oppsett

GAC inkluderer innebygd OAuth-autentisering for Qwen.ai ved bruk av enhetsflyten. Oppsettprosessen vil vise en kode og åpne nettleseren din for autentisering.

### Alternativ 1: Under første oppsett (Anbefalt)

Når du kjører `gac init`, velg ganske enkelt "Qwen.ai (OAuth)" som din leverandør:

```bash
gac init
```

Veiviseren vil:

1. Be deg velge "Qwen.ai (OAuth)" fra leverandørlisten
2. Vise en enhetskode og åpne nettleseren din
3. Du vil autentisere på Qwen.ai og skrive inn koden
4. Lagre tilgangstokenet ditt sikkert
5. Angi standardmodellen

### Alternativ 2: Bytt til Qwen.ai senere

Hvis du allerede har konfigurert GAC med en annen leverandør og ønsker å bytte til Qwen.ai:

```bash
gac model
```

Deretter:

1. Velg "Qwen.ai (OAuth)" fra leverandørlisten
2. Følg autentiseringsflyten for enhetskode
3. Token lagret sikkert til `~/.gac/oauth/qwen.json`
4. Modell konfigurert automatisk

### Alternativ 3: Direkte pålogging

Du kan også autentisere direkte ved å bruke:

```bash
gac auth qwen login
```

Dette vil:

1. Vise en enhetskode
2. Åpne nettleseren din til Qwen.ai-autentiseringssiden
3. Etter at du har autentisert, lagres tokenet automatisk

### Bruk GAC normalt

Når du er autentisert, bruk GAC som vanlig:

```bash
# Stage endringene dine
git add .

# Generer og commit med Qwen.ai
gac

# Eller overstyr modellen for en enkelt commit
gac -m qwen:qwen3-coder-plus
```

## Tilgjengelige modeller

Qwen.ai OAuth-integrasjonen bruker:

- `qwen3-coder-plus` - Optimalisert for kodingsoppgaver (standard)

Dette er modellen som er tilgjengelig via portal.qwen.ai OAuth-endepunktet. For andre Qwen-modeller, vurder å bruke OpenRouter-leverandøren som tilbyr flere Qwen-modellalternativer.

## Autentiseringskommandoer

GAC tilbyr flere kommandoer for å administrere Qwen.ai-autentisering:

```bash
# Logg inn på Qwen.ai
gac auth qwen login

# Sjekk autentiseringsstatus
gac auth qwen status

# Logg ut og fjern lagret token
gac auth qwen logout

# Sjekk status for alle OAuth-leverandører
gac auth
```

### Påloggingsalternativer

```bash
# Standard pålogging (åpner nettleser automatisk)
gac auth qwen login

# Pålogging uten å åpne nettleser (viser URL for å besøke manuelt)
gac auth qwen login --no-browser

# Stille modus (minimal utdata)
gac auth qwen login --quiet
```

## Feilsøking

### Token utløpt

Hvis du ser autentiseringsfeil, kan tokenet ditt ha utløpt. Re-autentiser ved å kjøre:

```bash
gac auth qwen login
```

Enhetskodeflyten vil starte, og nettleseren din vil åpnes for re-autentisering.

### Sjekk autentiseringsstatus

For å sjekke om du for øyeblikket er autentisert:

```bash
gac auth qwen status
```

Eller sjekk alle leverandører samtidig:

```bash
gac auth
```

### Logg ut

For å fjerne det lagrede tokenet ditt:

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (Qwen-autentisering ikke funnet)

Dette betyr at GAC ikke finner tilgangstokenet ditt. Autentiser ved å kjøre:

```bash
gac auth qwen login
```

Eller kjør `gac model` og velg "Qwen.ai (OAuth)" fra leverandørlisten.

### "Authentication failed" (Autentisering mislyktes)

Hvis OAuth-autentisering mislykkes:

1. Sørg for at du har en Qwen.ai-konto
2. Sjekk at nettleseren din åpnes riktig
3. Bekreft at du skrev inn enhetskoden riktig
4. Prøv en annen nettleser hvis problemene vedvarer
5. Bekreft nettverkstilkobling til `qwen.ai`

### Enhetskode fungerer ikke

Hvis autentisering med enhetskode ikke fungerer:

1. Sørg for at koden ikke har utløpt (koder er gyldige i en begrenset periode)
2. Prøv å kjøre `gac auth qwen login` igjen for en ny kode
3. Bruk `--no-browser`-flagget og besøk URL-en manuelt hvis åpning av nettleser mislykkes

## Sikkerhetsmerknader

- **Aldri commit tilgangstokenet ditt** til versjonskontroll
- GAC lagrer automatisk tokens i `~/.gac/oauth/qwen.json` (utenfor prosjektkatalogen din)
- Tokenfiler har begrensede tillatelser (kun lesbare av eier)
- Tokens kan utløpe og vil kreve re-autentisering
- OAuth-enhetsflyten er designet for sikker autentisering på hodeløse systemer

## Se også

- [Hoveddokumentasjon](USAGE.md)
- [Claude Code-oppsett](CLAUDE_CODE.md)
- [Feilsøkingsguide](TROUBLESHOOTING.md)
- [Qwen.ai-dokumentasjon](https://qwen.ai)
