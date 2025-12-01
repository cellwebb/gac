<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

# 🚀 Git Auto Commit (gac)

[![PyPI version](https://img.shields.io/pypi/v/gac.svg)](https://pypi.org/project/gac/)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/sv/CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[**English**](../../README.md) | [简体中文](docs/zh-CN/README.md) | [繁體中文](docs/zh-TW/README.md) | [日本語](docs/ja/README.md) | [한국어](docs/ko/README.md) | [हिन्दी](docs/hi/README.md) | [Tiếng Việt](docs/vi/README.md) | [Français](docs/fr/README.md) | [Русский](docs/ru/README.md) | [Español](docs/es/README.md) | [Português](docs/pt/README.md) | [Norsk](docs/no/README.md) | **Svenska** | [Deutsch](docs/de/README.md) | [Nederlands](docs/nl/README.md) | [Italiano](docs/it/README.md)

**LLM-drivna commit-meddelanden som förstår din kod!**

**Automatisera dina commits!** Ersätt `git commit -m "..."` med `gac` för kontekstuell, velformaterade commit-meddelanden genererade av stora språkmodeller!

---

## Vad Du Får

Intelligenta, kontextuella meddelanden som förklarar **varför** bakom dina ändringar:

![GAC generating a contextual commit message](assets/gac-simple-usage.sv.png)

---

</div>

<!-- markdownlint-enable MD033 MD036 -->

## Snabbstart

### Använd gac utan installation

```bash
uvx gac init   # Konfigurera din leverantör, modell och språk
uvx gac        # Generera och commit med LLM
```

Det är allt! Granska det genererade meddelandet och bekräfta med `y`.

### Installera och använd gac

```bash
uv tool install gac
gac init
gac
```

### Uppgradera installerad gac

```bash
uv tool upgrade gac
```

---

## Nyckelfunktioner

### 🌐 **25+ Stödda Leverantörer**

- **Anthropic** • **Azure OpenAI** • **Cerebras** • **Chutes.ai** • **Claude Code (OAuth)**
- **DeepSeek** • **Fireworks** • **Gemini** • **Groq** • **Kimi for Coding** • **LM Studio**
- **MiniMax.io** • **Mistral AI** • **Moonshot AI** • **Ollama** • **OpenAI** • **OpenRouter**
- **Replicate** • **Streamlake** • **Synthetic.new** • **Together AI** • **Z.AI** • **Z.AI Coding**
- **Custom Endpoints (Anthropic/OpenAI)**

### 🧠 **Smart LLM-analys**

- **Förstår avsikt**: Analyserar kodstruktur, logik och mönster för att förstå "varför" bakom dina ändringar, inte bara vad som ändrades
- **Semantisk medvetenhet**: Känner igen refactoring, bug-fixer, funktioner och breaking changes för att generera kontextuellt lämpliga meddelanden
- **Intelligent filtrering**: Prioriterar meningsfulla ändringar medan den ignorerar genererade filer, beroenden och artefakter
- **Intelligent commit-gruppering** - Gruppera automatiskt relaterade ändringar i flera logiska commits med `--group`

### 📝 **Flera Meddelandeformat**

- **En-rads** (-o flagga): Enkel-rads commit-meddelande som följer conventional commit-format
- **Standard** (standard): Sammanfattning med punktlista som förklarar implementeringsdetaljer
- **Utförlig** (-v flagga): Omfattande förklaringar inklusive motivation, teknisk ansats och påverkananalys

### 🌍 **Flerspråkigt Stöd**

- **25+ språk**: Generera commit-meddelanden på engelska, kinesiska, japanska, koreanska, spanska, franska, tyska och 20+ fler språk
- **Flexibel översättning**: Välj att behålla conventional commit-prefix på engelska för verktygskompatibilitet, eller översätt dem helt
- **Flera arbetsflöden**: Ställ in ett standardspråk med `gac language`, eller använd `-l <språk>` flagget för engångsöverstyrning
- **Stöd för originalskript**: Fullt stöd för icke-latinska skript inklusive CJK, kyrilliska, thai och mer

### 💻 **Utvecklarupplevelse**

- **Interaktiv feedback**: Skriv `r` för att köra om, `e` för att redigera på plats med vi/emacs-tangentbindningar, eller skriv din feedback direkt som `gör den kortare` eller `fokusera på bug-fixen`
- **Interaktiv frågning**: Använd `--interactive` (`-i`) för att svara på riktade frågor om dina ändringar för mer kontextuella commit-meddelanden
- **Ett-kommandos arbetsflöden**: Kompletta arbetsflöden med flaggor som `gac -ayp` (stage alla, auto-bekräfta, push)
- **Git-integration**: Respekterar pre-commit och lefthook hooks, kör dem innan dyra LLM-operationer

### 🛡️ **Inbyggd Säkerhet**

- **Automatisk hemlighetsdetektering**: Skannar efter API-nycklar, lösenord och tokens innan commit
- **Interaktivt skydd**: Frågar innan commit av potentiellt känslig data med tydliga åtgärdsalternativ
- **Smart filtrering**: Ignorerar exempelfiler, mallfiler och platshållar-text för att minska falska positiva

---

## Användningsexempel

### Grundläggande Arbetsflöde

```bash
# Stage dina ändringar
git add .

# Generera och commit med LLM
gac

# Granska → y (commit) | n (avbryt) | r (köra om) | e (redigera) | eller skriv feedback
```

### Vanliga Kommandon

| Kommando        | Beskrivning                                                        |
| --------------- | ------------------------------------------------------------------ |
| `gac`           | Generera commit-meddelande                                         |
| `gac -y`        | Auto-bekräfta (ingen granskning behövs)                            |
| `gac -a`        | Stage alla innan generering av commit-meddelande                   |
| `gac -o`        | En-rads meddelande för triviala ändringar                          |
| `gac -v`        | Utförligt format med Motivation, Teknisk Ansats och Påverkananalys |
| `gac -h "hint"` | Lägg till kontext för LLM (t.ex., `gac -h "bug fix"`)              |
| `gac -s`        | Inkludera scope (t.ex., feat(auth):)                               |
| `gac -i`        | Ställ frågor om ändringar för bättre kontext                       |
| `gac -p`        | Commit och push                                                    |

### Exempel för Avancerade Användare

```bash
# Komplett arbetsflöde i ett kommando
gac -ayp -h "release preparation"

# Detaljerad förklaring med scope
gac -v -s

# Snabb en-rads för små ändringar
gac -o

# Gruppera ändringar i logiskt relaterade commits
gac -ag

# Interaktivt läge med utförlig output för detaljerade förklaringar
gac -iv

# Debug vad LLM ser
gac --show-prompt

# Hoppa över säkerhetsskanning (använd med försiktighet)
gac --skip-secret-scan
```

### Interaktivt Feedbacksystem

Inte nöjd med resultatet? Du har flera alternativ:

```bash
# Enkel omspelning (ingen feedback)
r

# Redigera på plats med rik terminalredigering
e
# Använder prompt_toolkit för flerradersredigering med vi/emacs-tangentbindningar
# Tryck Esc+Enter eller Ctrl+S för att skicka, Ctrl+C för att avbryta

# Eller skriv bara din feedback direkt!
gör den kortare och fokusera på prestandaförbättringen
använd conventional commit-format med scope
förklara säkerhetsimplicationerna

# Tryck Enter på tom input för att se prompten igen
```

Redigeringsfunktionen (`e`) ger rik på-plats-terminalredigering som låter dig:

- **Redigera naturligt**: Flerradersredigering med bekanta vi/emacs-tangentbindningar
- **Göra snabba fixar**: Korrigera stavfel, justera formuleringar eller finslipa formatering
- **Lägga till detaljer**: Inkludera information LLM kan ha missat
- **Omstrukturera**: Omorganisera punktlister eller ändra meddelandestrukturen

---

## Konfiguration

Kör `gac init` för att konfigurera din leverantör interaktivt, eller sätt miljövariabler:

Behöver du ändra leverantörer eller modeller senare utan att röra språkinställningar? Använd `gac model` för ett strömlinjeformat flöde som hoppar över språkfrågorna.

```bash
# Exempelkonfiguration
GAC_MODEL=anthropic:your-model-name
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Se `.gac.env.example` för alla tillgängliga alternativ.

**Vill du ha commit-meddelanden på ett annat språk?** Kör `gac language` för att välja från 25+ språk inklusive Español, Français, 日本語 och mer.

**Vill du anpassa commit-meddelandestil?** Se [docs/CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md) för vägledning om att skriva anpassade system-prompts.

---

## Projektanalys

📊 **[Visa live användningsanalys och statistik →](https://clickpy.clickhouse.com/dashboard/gac)**

Följ realtids installationsmätningar och pakkenedladdningsstatistik.

---

## Få Hjälp

- **Full dokumentation**: [USAGE.md](USAGE.md) - Komplett CLI-referens
- **Anpassade prompts**: [CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md) - Anpassa commit-meddelandestil
- **Felsökning**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Vanliga problem och lösningar
- **Bidra**: [CONTRIBUTING.md](CONTRIBUTING.md) - Utvecklings-setup och riktlinjer

---

<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

Skapat med ❤️ för utvecklare som vill ha bättre commit-meddelanden

[⭐ Stjärna oss på GitHub](https://github.com/cellwebb/gac) • [🐛 Rapportera problem](https://github.com/cellwebb/gac/issues) • [📖 Full dokumentation](USAGE.md)

</div>

<!-- markdownlint-enable MD033 MD036 -->
