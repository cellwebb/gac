# Bruke GitHub Copilot med GAC

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | **Norsk** | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC støtter autentisering via GitHub Copilot, slik at du kan bruke ditt Copilot-abonnement til å få tilgang til modeller fra OpenAI, Anthropic, Google og mer — alt inkludert i ditt GitHub Copilot-abonnement.

## Hva er GitHub Copilot OAuth?

GitHub Copilot OAuth bruker **Device Flow** — en sikker, nettleserbasert autentiseringsmetode som ikke krever en lokal callback-server. Du besøker en URL, skriver inn en engangskode og autoriserer GAC til å bruke din Copilot-tilgang. I bakgrunnen bytter GAC din langlevende GitHub OAuth-token mot en kortlevende Copilot-økttoken (~30 min) som gir tilgang til Copilot API.

Dette gir deg tilgang til modeller fra flere leverandører gjennom ett abonnement:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Fordeler

- **Multi-leverandør tilgang**: Bruk modeller fra OpenAI, Anthropic og Google gjennom ett abonnement
- **Kostnadseffektivt**: Bruk ditt eksisterende Copilot-abonnement i stedet for å betale for separate API-nøkler
- **Ingen API-nøkkeladministrasjon**: Device Flow-autentisering — ingen nøkler å rotere eller lagre
- **GitHub Enterprise-støtte**: Fungerer med GHE-instanser via `--host`-flagget

## Oppsett

### Alternativ 1: Under første gangs oppsett (Anbefalt)

Når du kjører `gac init`, velger du ganske enkelt «Copilot» som leverandøren din:

```bash
gac init
```

Veiviseren vil:

1. Be deg om å velge «Copilot» fra leverandørlisten
2. Vise en engangskode og åpne nettleseren din for Device Flow-autentisering
3. Lagre din OAuth-token i `~/.gac/oauth/copilot.json`
4. Angi standardmodellen

### Alternativ 2: Bytt til Copilot senere

Hvis du allerede har konfigurert GAC med en annen leverandør:

```bash
gac model
```

Velg deretter «Copilot» fra leverandørlisten og autentiser.

### Alternativ 3: Direkte innlogging

Autentiser direkte uten å endre din standardmodell:

```bash
gac auth copilot login
```

### Bruk GAC som normalt

Når du er autentisert, bruker du GAC som vanlig:

```bash
# Stage endringene dine
git add .

# Generer og commit med Copilot
gac

# Eller overstyr modellen for én enkelt commit
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Tilgjengelige modeller

Copilot gir tilgang til modeller fra flere leverandører. Nåværende modeller inkluderer:

| Leverandør | Modeller                                                                                       |
| ---------- | ---------------------------------------------------------------------------------------------- |
| OpenAI     | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic  | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google     | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Merk:** Modellerlisten som vises etter innlogging er informativ og kan bli utdatert etter hvert som GitHub legger til nye modeller. Sjekk [GitHub Copilot-dokumentasjonen](https://docs.github.com/en/copilot) for de nyeste tilgjengelige modellene.

## GitHub Enterprise

For å autentisere med en GitHub Enterprise-instans:

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC vil automatisk bruke riktig Device Flow og API-endepunkter for din GHE-instans. Økttokenet caches per vert, slik at forskjellige GHE-instanser håndteres uavhengig.

## CLI-kommandoer

GAC tilbyr dedikerte CLI-kommandoer for Copilot-autentiseringsadministrasjon:

### Logg inn

Autentiser eller re-autentiser med GitHub Copilot:

```bash
gac auth copilot login
```

Nettleseren din åpnes til en Device Flow-side der du skriver inn en engangskode. Hvis du allerede er autentisert, blir du spurt om du vil re-autentisere.

For GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Logg ut

Fjern lagrede Copilot-tokens:

```bash
gac auth copilot logout
```

Dette sletter den lagrede tokenfilen på `~/.gac/oauth/copilot.json` og øktcachen.

### Status

Sjekk din nåværende Copilot-autentiseringsstatus:

```bash
gac auth copilot status
```

Eller sjekk alle leverandører på én gang:

```bash
gac auth
```

## Hvordan det fungerer

Copilot-autentiseringsflyten skiller seg fra ChatGPT og Claude Code OAuth:

1. **Device Flow** — GAC ber GitHub om en enhetskode og viser den
2. **Nettleserautorisasjon** — Du besøker URL-en og skriver inn koden
3. **Token-polling** — GAC poller GitHub til du fullfører autorisasjon
4. **Økttoken-utveksling** — GitHub OAuth-tokenen byttes inn for en kortlevende Copilot-økttoken
5. **Automatisk fornyelse** — Økttokens (~30 min) fornyes automatisk fra den bufrede OAuth-tokenen

I motsetning til PKCE-basert OAuth (ChatGPT/Claude Code), krever ikke Device Flow en lokal callback-server eller portadministrasjon.

## Feilsøking

### «Copilot-autentisering ikke funnet»

Kjør innloggingskommandoen for å autentisere:

```bash
gac auth copilot login
```

### «Kunne ikke innhente Copilot-økttoken»

Dette betyr at GAC fikk en GitHub OAuth-token, men ikke kunne bytte den inn for en Copilot-økttoken. Vanligvis betyr dette:

1. **Ingen Copilot-abonnement** — Din GitHub-konto har ikke et aktivt Copilot-abonnement
2. **Token tilbakekalt** — OAuth-tokenen ble tilbakekalt; re-autentiser med `gac auth copilot login`

### Økttoken utløpt

Økttokens utløper etter ~30 minutter. GAC fornyer dem automatisk fra den bufrede OAuth-tokenen, så du trenger ikke å re-autentisere ofte. Hvis automatisk fornyelse mislykkes:

```bash
gac auth copilot login
```

### «Ugyldig eller usikker vertsnavn»

`--host`-flagget validerer vertsnavn strengt for å forhindre SSRF-angrep. Hvis du ser denne feilen:

- Sørg for at vertsnavnet ikke inkluderer porter (f.eks. bruk `ghe.company.com` ikke `ghe.company.com:8080`)
- Ikke inkluder protokoller eller stier (f.eks. bruk `ghe.company.com` ikke `https://ghe.company.com/api`)
- Private IP-adresser og `localhost` er blokkert av sikkerhetsgrunner

### GitHub Enterprise-problemer

Hvis GHE-autentisering mislykkes:

1. Bekreft at din GHE-instans har Copilot aktivert
2. Sjekk at ditt GHE-vertsnavn er tilgjengelig fra din maskin
3. Sørg for at din GHE-konto har en Copilot-lisens
4. Prøv med `--host`-flagget eksplisitt: `gac auth copilot login --host ghe.mycompany.com`

## Forskjeller fra andre OAuth-leverandører

| Funksjon        | ChatGPT OAuth              | Claude Code                  | Copilot                                        |
| --------------- | -------------------------- | ---------------------------- | ---------------------------------------------- |
| Auth-metode     | PKCE (nettleser-callback)  | PKCE (nettleser-callback)    | Device Flow (engangskode)                      |
| Callback-server | Porter 1455-1465           | Porter 8765-8795             | Ikke nødvendig                                 |
| Token-levetid   | Langlevende (auto-fornyet) | Utløpende (re-autentisering) | Økt ~30 min (auto-fornyet)                     |
| Modeller        | Codex-optimalisert OpenAI  | Claude-familien              | Multi-leverandør (OpenAI + Anthropic + Google) |
| GHE-støtte      | Nei                        | Nei                          | Ja (`--host`-flagg)                            |

## Sikkerhetsmerknader

- **Aldri commit din OAuth-token** til versjonskontroll
- GAC lagrer OAuth-tokens i `~/.gac/oauth/copilot.json` (utenfor prosjektkatalogen din)
- Økttokens caches i `~/.gac/oauth/copilot_session.json` med `0o600`-rettigheter
- Vertsnavn valideres strengt for å forhindre SSRF- og URL-injeksjonsangrep
- Private IP-adresser, loopback-adresser og `localhost` er blokkert som vertsnavn
- Device Flow eksponerer ingen lokale porter, noe som reduserer angrepsflaten

## Se også

- [Hoveddokumentasjon](USAGE.md)
- [Feilsøkingsveiledning](TROUBLESHOOTING.md)
- [ChatGPT OAuth-veiledning](CHATGPT_OAUTH.md)
- [Claude Code-veiledning](CLAUDE_CODE.md)
- [GitHub Copilot-dokumentasjon](https://docs.github.com/en/copilot)
