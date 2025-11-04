# gac Command-Line Gebruik

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Deutsch](../de/USAGE.md) | **Nederlands**

Dit document beschrijft alle beschikbare vlaggen en opties voor de `gac` CLI tool.

## Inhoudsopgave

- [gac Command-Line Gebruik](#gac-command-line-gebruik)
  - [Inhoudsopgave](#inhoudsopgave)
  - [Basisgebruik](#basisgebruik)
  - [Kern Workflow Vlaggen](#kern-workflow-vlaggen)
  - [Bericht Aanpassing](#bericht-aanpassing)
  - [Output en Verbose](#output-en-verbose)
  - [Help en Versie](#help-en-versie)
  - [Voorbeeld Workflows](#voorbeeld-workflows)
  - [Geavanceerd](#geavanceerd)
    - [Pre-commit en Lefthook Hooks Overslaan](#pre-commit-en-lefthook-hooks-overslaan)
  - [Configuratie Notities](#configuratie-notities)
    - [Geavanceerde Configuratie Opties](#geavanceerde-configuratie-opties)
    - [Configuratie Subcommando's](#configuratie-subcommandos)
  - [Hulp Krijgen](#hulp-krijgen)

## Basisgebruik

```sh
gac init
# Volg daarna de prompts om uw provider, model en API sleutels interactief te configureren
gac
```

Genereert een LLM-aangedreven commitbericht voor staged wijzigingen en vraagt om bevestiging. De bevestigingsprompt accepteert:

- `y` of `yes` - Ga door met de commit
- `n` of `no` - Annuleer de commit
- `r` of `reroll` - Genereer het commitbericht opnieuw met dezelfde context
- `e` of `edit` - Bewerk het commitbericht ter plaatse met rijke terminalbewerking (vi/emacs keybindings)
- Alle andere tekst - Genereer opnieuw met die tekst als feedback (bv., `maak het korter`, `focus op prestaties`)
- Lege input (alleen Enter) - Toon de prompt opnieuw

---

## Kern Workflow Vlaggen

| Vlag / Optie         | Kort | Beschrijving                                               |
| -------------------- | ---- | ---------------------------------------------------------- |
| `--add-all`          | `-a` | Stage alle wijzigingen voordat u commit                    |
| `--group`            | `-g` | Groepeer staged wijzigingen in meerdere logische commits   |
| `--push`             | `-p` | Push wijzigingen naar remote na commit                     |
| `--yes`              | `-y` | Bevestig commit automatisch zonder prompting               |
| `--dry-run`          |      | Toon wat er zou gebeuren zonder wijzigingen te maken       |
| `--no-verify`        |      | Sla pre-commit en lefthook hooks over bij commit           |
| `--skip-secret-scan` |      | Sla security scan over voor geheimen in staged wijzigingen |

**Let op:** Combineer `-a` en `-g` (d.w.z. `-ag`) om eerst ALLE wijzigingen te stage, en ze daarna te groeperen in commits.

**Let op:** Bij gebruik van `--group`, wordt het maximale output tokens limiet automatisch geschaald op basis van het aantal bestanden dat wordt gecommit (2x voor 1-9 bestanden, 3x voor 10-19 bestanden, 4x voor 20-29 bestanden, 5x voor 30+ bestanden). Dit zorgt ervoor dat de LLM genoeg tokens heeft om alle gegroepeerde commits te genereren zonder truncatie, zelfs voor grote changesets.

## Bericht Aanpassing

| Vlag / Optie        | Kort | Beschrijving                                                                  |
| ------------------- | ---- | ----------------------------------------------------------------------------- |
| `--one-liner`       | `-o` | Genereer een eenregelig commitbericht                                         |
| `--verbose`         | `-v` | Genereer gedetailleerde commitberichten met motivatie, architectuur, & impact |
| `--hint <tekst>`    | `-h` | Voeg een hint toe om de LLM te begeleiden                                     |
| `--model <model>`   | `-m` | Specificeer het model dat voor deze commit moet worden gebruikt               |
| `--language <taal>` | `-l` | Overschrijf de taal (naam of code: 'Spanish', 'es', 'zh-CN', 'ja')            |
| `--scope`           | `-s` | Stel een passende scope voor de commit vast                                   |

**Let op:** U kunt interactief feedback geven door het gewoon op de bevestigingsprompt te typen - geen prefix met 'r' nodig. Typ `r` voor een simple reroll, `e` om ter plaatse te bewerken met vi/emacs keybindings, of typ uw feedback direct zoals `maak het korter`.

## Output en Verbose

| Vlag / Optie          | Kort | Beschrijving                                             |
| --------------------- | ---- | -------------------------------------------------------- |
| `--quiet`             | `-q` | Onderdruk alle output behalve fouten                     |
| `--log-level <level>` |      | Stel log niveau in (debug, info, warning, error)         |
| `--show-prompt`       |      | Print de LLM prompt gebruikt voor commitberichtgeneratie |

## Help en Versie

| Vlag / Optie | Kort | Beschrijving                 |
| ------------ | ---- | ---------------------------- |
| `--version`  |      | Toon gac versie en sluit af  |
| `--help`     |      | Toon helpbericht en sluit af |

---

## Voorbeeld Workflows

- **Stage alle wijzigingen en commit:**

  ```sh
  gac -a
  ```

- **Commit en push in één stap:**

  ```sh
  gac -ap
  ```

- **Genereer een eenregelig commitbericht:**

  ```sh
  gac -o
  ```

- **Genereer een gedetailleerd commitbericht met gestructureerde secties:**

  ```sh
  gac -v
  ```

- **Voeg een hint toe voor de LLM:**

  ```sh
  gac -h "Refactor authenticatielogica"
  ```

- **Stel een scope voor de commit vast:**

  ```sh
  gac -s
  ```

- **Groepeer staged wijzigingen in logische commits:**

  ```sh
  gac -g
  # Groepeert alleen de bestanden die u al gestaged heeft
  ```

- **Groepeer alle wijzigingen (staged + unstaged) en auto-bevestig:**

  ```sh
  gac -agy
  # Staged alles, groepeert het, en bevestigt automatisch
  ```

- **Gebruik een specifiek model alleen voor deze commit:**

  ```sh
  gac -m anthropic:claude-3-5-haiku-latest
  ```

- **Genereer commitbericht in een specifieke taal:**

  ```sh
  # Gebruik taalcodes (korter)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # Gebruik volledige namen
  gac -l "Simplified Chinese"
  gac -l Japanese
  gac -l Spanish
  ```

- **Dry run (zie wat er zou gebeuren):**

  ```sh
  gac --dry-run
  ```

## Geavanceerd

- Combineer vlaggen voor krachtigere workflows (bv., `gac -ayp` om te stage, auto-bevestigen en pushen)
- Gebruik `--show-prompt` om te debuggen of de prompt die naar de LLM wordt gestuurd te bekijken
- Pas verbose aan met `--log-level` of `--quiet`

### Pre-commit en Lefthook Hooks Overslaan

De `--no-verify` vlag staat u toe om pre-commit of lefthook hooks te overslaan die in uw project geconfigureerd zijn:

```sh
gac --no-verify  # Sla alle pre-commit en lefthook hooks over
```

**Gebruik `--no-verify` wanneer:**

- Pre-commit of lefthook hooks tijdelijk falen
- Werken met tijdrovende hooks
- Committen van work-in-progress code die nog niet alle controles doorstaat

**Let op:** Gebruik met voorzichtigheid omdat deze hooks codekwaliteitsstandaarden handhaven.

### Security Scanning

gac inclusief ingebouwde security scanning die automatisch potentiële geheimen en API sleutels detecteert in uw staged wijzigingen voordat u commit. Dit helpt voorkomen dat u per ongeluk gevoelige informatie commit.

**Security scans overslaan:**

```sh
gac --skip-secret-scan  # Sla security scan over voor deze commit
```

**Om permanent uit te schakelen:** Stel `GAC_SKIP_SECRET_SCAN=true` in uw `.gac.env` bestand.

**Wanneer overslaan:**

- Committen van voorbeeldcode met placeholder sleutels
- Werken met test fixtures die dummy credentials bevatten
- Wanneer u heeft geverifieerd dat de wijzigingen veilig zijn

**Let op:** De scanner gebruikt patroone matching om algemene geheime formaten te detecteren. Bekijk altijd uw staged wijzigingen voordat u commit.

## Configuratie Notities

- De aanbevolen manier om gac in te stellen is `gac init` uit te voeren en de interactieve prompts te volgen.
- Al geconfigureerde taal en alleen providers of modellen moeten wisselen? Voer `gac model` uit om de setup te herhalen zonder taalvragen.
- gac laadt configuratie in de volgende volgorde van prioriteit:
  1. CLI vlaggen
  2. Omgevingsvariabelen
  3. Project-niveau `.gac.env`
  4. Gebruiker-niveau `~/.gac.env`

### Geavanceerde Configuratie Opties

U kunt het gedrag van gac aanpassen met deze optionele omgevingsvariabelen:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Stel automatisch een scope en voeg deze toe aan commitberichten (bv., `feat(auth):` vs `feat:`)
- `GAC_VERBOSE=true` - Genereer gedetailleerde commitberichten met motivatie, architectuur en impact secties
- `GAC_TEMPERATURE=0.7` - Controleer LLM creativiteit (0.0-1.0, lager = meer gefocust)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Maximale tokens voor gegenereerde berichten (automatisch geschaald 2-5x bij gebruik van `--group` op basis van bestandsaantal; overschrijf om hoger of lager te gaan)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Waarschuw wanneer prompts dit tokenaantal overschrijden
- `GAC_SYSTEM_PROMPT_PATH=/pad/naar/custom_prompt.txt` - Gebruik een custom system prompt voor commitberichtgeneratie
- `GAC_LANGUAGE=Spanish` - Genereer commitberichten in een specifieke taal (bv., Spanish, French, Japanese, German). Ondersteunt volledige namen of ISO codes (es, fr, ja, de, zh-CN). Gebruik `gac language` voor interactieve selectie
- `GAC_TRANSLATE_PREFIXES=true` - Vertaal conventionele commit prefixen (feat, fix, etc.) naar de doeltaal (standaard: false, houdt prefixen in Engels)
- `GAC_SKIP_SECRET_SCAN=true` - Schakel automatische security scanning voor geheimen in staged wijzigingen uit (gebruik met voorzichtigheid)

Zie `.gac.env.example` voor een complete configuratiesjabloon.

Voor gedetailleerde begeleiding bij het maken van custom system prompts, zie [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md).

### Configuratie Subcommando's

De volgende subcommando's zijn beschikbaar:

- `gac init` — Interactieve setup wizard voor provider, model en taalconfiguratie
- `gac model` — Provider/model/API sleutel setup zonder taalprompts (ideaal voor snelle wissels)
- `gac config show` — Toon huidige configuratie
- `gac config set KEY VALUE` — Stel een config sleutel in in `$HOME/.gac.env`
- `gac config get KEY` — Krijg een config waarde
- `gac config unset KEY` — Verwijder een config sleutel van `$HOME/.gac.env`
- `gac language` (of `gac lang`) — Interactieve taalkeuzemenu voor commitberichten (stelt GAC_LANGUAGE in)
- `gac diff` — Toon gefilterde git diff met opties voor staged/unstaged wijzigingen, kleur en truncatie

## Hulp Krijgen

- Voor custom system prompts, zie [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- Voor probleemoplossing en geavanceerde tips, zie [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Voor installatie en configuratie, zie [README.md#installation-and-configuration](README.md#installation-and-configuration)
- Om bij te dragen, zie [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Licentie informatie: [LICENSE](LICENSE)
