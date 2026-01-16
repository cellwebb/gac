<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

# 🚀 Git Auto Commit (gac)

[![PyPI version](https://img.shields.io/pypi/v/gac.svg)](https://pypi.org/project/gac/)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/no/CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[**English**](../../README.md) | [简体中文](docs/zh-CN/README.md) | [繁體中文](docs/zh-TW/README.md) | [日本語](docs/ja/README.md) | [한국어](docs/ko/README.md) | [हिन्दी](docs/hi/README.md) | [Tiếng Việt](docs/vi/README.md) | [Français](docs/fr/README.md) | [Русский](docs/ru/README.md) | [Español](docs/es/README.md) | [Português](docs/pt/README.md) | **Norsk** | [Svenska](docs/sv/README.md) | [Deutsch](docs/de/README.md) | [Nederlands](docs/nl/README.md) | [Italiano](docs/it/README.md)

**LLM-drevne commit-meldinger som forstår koden din!**

**Automatiser dine commits!** Erstatt `git commit -m "..."` med `gac` for kontekstuelle, velformaterte commit-meldinger generert av store språkmodeller!

---

## Hva Du Får

Intelligente, kontekstuelle meldinger som forklarer **hvorfor** bak endringene dine:

![GAC generating a contextual commit message](assets/gac-simple-usage.no.png)

---

</div>

<!-- markdownlint-enable MD033 MD036 -->

## Hurtigstart

### Bruk gac uten installasjon

```bash
uvx gac init   # Konfigurer din leverandør, modell og språk
uvx gac        # Generer og commit med LLM
```

Det er alt! Gjennomgå den genererte meldingen og bekreft med `y`.

### Installer og bruk gac

```bash
uv tool install gac
gac init
gac
```

### Oppgrader installert gac

```bash
uv tool upgrade gac
```

---

## Nøkkelegenskaper

### 🌐 **25+ Støttede Leverandører**

- **Anthropic** • **Azure OpenAI** • **Cerebras** • **Chutes.ai** • **Claude Code (OAuth)**
- **DeepSeek** • **Fireworks** • **Gemini** • **Groq** • **Kimi for Coding** • **LM Studio**
- **MiniMax.io** • **Mistral AI** • **Moonshot AI** • **Ollama** • **OpenAI** • **OpenRouter**
- **Qwen.ai (OAuth)** • **Replicate** • **Streamlake** • **Synthetic.new** • **Together AI**
- **Z.AI** • **Z.AI Coding** • **Custom Endpoints (Anthropic/OpenAI)**

### 🧠 **Smart LLM-analyse**

- **Forstår intensjon**: Analyserer kode-struktur, logikk og mønstre for å forstå "hvorfor" bak endringene dine, ikke bare hva som ble endret
- **Semantisk bevissthet**: Gjenkjenner refactoring, bug-fikser, funksjoner og breaking changes for å generere kontekstuelt passende meldinger
- **Intelligent filtrering**: Prioriterer meningsfulle endringer mens den ignorerer genererte filer, avhengigheter og artefakter
- **Intelligent commit-gruppering** - Grupper automatisk relaterte endringer i flere logiske commits med `--group`

### 📝 **Flere Meldingsformater**

- **En-linjers** (-o flagg): Enkel-linjers commit-melding som følger conventional commit-format
- **Standard** (standard): Oppsummering med punktliste som forklarer implementeringsdetaljer
- **Utførlig** (-v flagg): Oversiktlige forklaringer inkludert motivasjon, teknisk tilnærming og påvirkningsanalyse

### 🌍 **Flerspråklig Støtte**

- **25+ språk**: Generer commit-meldinger på engelsk, kinesisk, japansk, koreansk, spansk, fransk, tysk og 20+ flere språk
- **Fleksibel oversettelse**: Velg å beholde conventional commit-prefikser på engelsk for verktøykompatibilitet, eller oversett dem fullstendig
- **Flere arbeidsflyter**: Sett et standardspråk med `gac language`, eller bruk `-l <språk>` flagget for engangs-overstyring
- **Støtte for det opprinnelige skriptet**: Full støtte for ikke-latinske skript inkludert CJK, kyrillisk, thai og mer

### 💻 **Utvikleropplevelse**

- **Interaktiv tilbakemelding**: Skriv `r` for å kjøre på nytt, `e` for å redigere på stedet med vi/emacs-tastebindinger, eller skriv direkte tilbakemeldingen din som `gjør den kortere` eller `fokuser på bug-fiksen`
- **Interaktiv spørsmålsstilling**: Bruk `--interactive` (`-i`) for å svare på målrettede spørsmål om endringene dine for mer kontekstuelle commit-meldinger
- **Én-kommandos arbeidsflyter**: Komplette arbeidsflyter med flagg som `gac -ayp` (stage alle, auto-bekreft, push)
- **Git-integrasjon**: Respekterer pre-commit og lefthook hooks, og kjører dem før dyre LLM-operasjoner

### 🛡️ **Innebygd Sikkerhet**

- **Automatisk hemmelighetsoppdagelse**: Skanner etter API-nøkler, passord og tokens før commit
- **Interaktiv beskyttelse**: Spør før commit av potensielt sensitive data med klare løsningsalternativer
- **Smart filtrering**: Ignorerer eksempelfiler, mal-filer og plassholdertekst for å redusere falske positive

---

## Brukseksempler

### Enkel Arbeidsflyt

```bash
# Stage endringene dine
git add .

# Generer og commit med LLM
gac

# Gjennomgå → y (commit) | n (avbryt) | r (kjør på nytt) | e (rediger) | eller skriv tilbakemelding
```

### Vanlige Kommandoer

| Kommando        | Beskrivelse                                                              |
| --------------- | ------------------------------------------------------------------------ |
| `gac`           | Generer commit-melding                                                   |
| `gac -y`        | Auto-bekreft (ingen gjennomgang nødvendig)                               |
| `gac -a`        | Stage alle før generering av commit-melding                              |
| `gac -o`        | En-linjers melding for trivielle endringer                               |
| `gac -v`        | Utførlig format med Motivasjon, Teknisk Tilnærming og Påvirkningsanalyse |
| `gac -h "hint"` | Legg til kontekst for LLM (f.eks., `gac -h "bug fix"`)                   |
| `gac -s`        | Inkluder scope (f.eks., feat(auth):)                                     |
| `gac -i`        | Stil spørsmål om endringer for bedre kontekst                            |
| `gac -g`        | Gruppere endringer i flere logiske commits                               |
| `gac -p`        | Commit og push                                                           |

### Eksempler for Avanserte Brukere

```bash
# Komplett arbeidsflyt i én kommando
gac -ayp -h "release preparation"

# Detaljert forklaring med scope
gac -v -s

# Rask en-linjers for små endringer
gac -o

# Grupper endringer i logisk relaterte commits
gac -ag

# Interaktiv modus med utførlig output for detaljerte forklaringer
gac -iv

# Debug hva LLM ser
gac --show-prompt

# Hopp over sikkerhetsskanning (bruk med forsiktighet)
gac --skip-secret-scan
```

### Interaktivt Tilbakemeldingssystem

Ikke fornøyd med resultatet? Du har flere alternativer:

```bash
# Enkel ny gjennomsyning (ingen tilbakemelding)
r

# Rediger på stedet med rik terminalredigering
e
# Bruker prompt_toolkit for flerreduers redigering med vi/emacs-tastebindinger
# Trykk Esc+Enter eller Ctrl+S for å sende inn, Ctrl+C for å avbryte

# Eller skriv bare tilbakemeldingen din direkte!
gjør den kortere og fokuser på ytelsesforbedringen
bruk conventional commit-format med scope
forklar sikkerhetsimplikasjonene

# Trykk Enter på tom input for å se prompten på nytt
```

Redigeringsfunksjonen (`e`) gir rik på-plass-terminalredigering, som lar deg:

- **Redigere naturlig**: Flerreduers redigering med kjente vi/emacs-tastebindinger
- **Gjøre raske rettelser**: Korrigere skrivefeil, justere ordlyd eller forbedre formatering
- **Legge til detaljer**: Inkludere informasjon LLM kan ha gått glipp av
- **Omstrukturere**: Reorganisere punktlister eller endre meldingsstrukturen

---

## Konfigurasjon

Kjør `gac init` for å konfigurere din leverandør interaktivt, eller sett miljøvariabler:

Trenger du å endre leverandører eller modeller senere uten å røre språkinnstillinger? Bruk `gac model` for en strømlinjeformet flyt som hopper over språk-spørsmålene.

```bash
# Eksempelkonfigurasjon
GAC_MODEL=anthropic:your-model-name
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Se `.gac.env.example` for alle tilgjengelige alternativer.

**Vil du ha commit-meldinger på et annet språk?** Kjør `gac language` for å velge fra 25+ språk inkludert Español, Français, 日本語 og mer.

**Vil du tilpasse commit-meldingsstil?** Se [docs/CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md) for veiledning om å skrive egendefinerte system-prompts.

---

## Prosjektanalyse

📊 **[Vis live bruksanalyse og statistikk →](https://clickpy.clickhouse.com/dashboard/gac)**

Følg sanntids installasjonsmålinger og pakkenedlastningsstatistikk.

---

## Få Hjelp

- **Full dokumentasjon**: [USAGE.md](USAGE.md) - Komplett CLI-referanse
- **Claude Code OAuth**: [docs/CLAUDE_CODE.md](docs/no/CLAUDE_CODE.md) - Claude Code oppsett og autentisering
- **Qwen.ai OAuth**: [docs/QWEN.md](docs/no/QWEN.md) - Qwen.ai oppsett og autentisering
- **Egendefinerte prompts**: [CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md) - Tilpass commit-meldingsstil
- **Feilsøking**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Vanlige problemer og løsninger
- **Bidra**: [CONTRIBUTING.md](CONTRIBUTING.md) - Utviklingsoppsett og retningslinjer

---

<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

Laget med ❤️ for utviklere som vil ha bedre commit-meldinger

[⭐ Star oss på GitHub](https://github.com/cellwebb/gac) • [🐛 Rapporter problemer](https://github.com/cellwebb/gac/issues) • [📖 Full dokumentasjon](USAGE.md)

</div>

<!-- markdownlint-enable MD033 MD036 -->
