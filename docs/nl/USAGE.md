# gac Command-Line Gebruik

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Рус../](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | **Nederlands** | [Italiano](../it/USAGE.md)

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
    - [Security Scanning](#security-scanning)
    - [SSL-certificaatverificatie](#ssl-certificaatverificatie)
  - [Configuratie Notities](#configuratie-notities)
    - [Geavanceerde Configuratie Opties](#geavanceerde-configuratie-opties)
    - [Configuratie Subcommando's](#configuratie-subcommandos)
  - [Interactieve Modus](#interactieve-modus)
    - [Hoe het werkt](#hoe-het-werkt)
    - [Wanneer interactieve modus te gebruiken](#wanneer-interactieve-modus-te-gebruiken)
    - [Gebruiksvoorbeelden](#gebruiksvoorbeelden)
    - [Vraag-Antwoord Workflow](#vraag-antwoord-workflow)
    - [Combinatie met andere vlaggen](#combinatie-met-andere-vlaggen)
    - [Beste Praktijken](#beste-praktijken)
  - [Gebruiksstatistieken](#gebruiksstatistieken)
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
- `e` of `edit` - Bewerk het commitbericht. Standaard wordt een in-place TUI geopend met vi/emacs-keybindings. Stel `GAC_EDITOR` in om in plaats daarvan uw voorkeurseditor te openen (bijv. `GAC_EDITOR=code gac` voor VS Code, `GAC_EDITOR=vim gac` voor vim)
- Alle andere tekst - Genereer opnieuw met die tekst als feedback (bv., `maak het korter`, `focus op prestaties`)
- Lege input (alleen Enter) - Toon de prompt opnieuw

---

## Kern Workflow Vlaggen

| Vlag / Optie         | Kort | Beschrijving                                                                 |
| -------------------- | ---- | ---------------------------------------------------------------------------- |
| `--add-all`          | `-a` | Stage alle wijzigingen voordat u commit                                      |
| `--group`            | `-g` | Groepeer staged wijzigingen in meerdere logische commits                     |
| `--push`             | `-p` | Push wijzigingen naar remote na commit                                       |
| `--yes`              | `-y` | Bevestig commit automatisch zonder prompting                                 |
| `--dry-run`          |      | Toon wat er zou gebeuren zonder wijzigingen te maken                         |
| `--message-only`     |      | Toon alleen het gegenereerde commitbericht zonder daadwerkelijk te committen |
| `--no-verify`        |      | Sla pre-commit en lefthook hooks over bij commit                             |
| `--skip-secret-scan` |      | Sla security scan over voor geheimen in staged wijzigingen                   |
| `--no-verify-ssl`    |      | Sla SSL-certificaatverificatie over (nuttig voor bedrijfsproxies)            |
| `--signoff`          |      | Voeg Signed-off-by regel toe aan commitbericht (DCO-naleving)                |
| `--interactive`      | `-i` | Stel vragen over wijzigingen voor betere commits                             |

**Let op:** Combineer `-a` en `-g` (d.w.z. `-ag`) om eerst ALLE wijzigingen te stage, en ze daarna te groeperen in commits.

**Let op:** Bij gebruik van `--group`, wordt het maximale output tokens limiet automatisch geschaald op basis van het aantal bestanden dat wordt gecommit (2x voor 1-9 bestanden, 3x voor 10-19 bestanden, 4x voor 20-29 bestanden, 5x voor 30+ bestanden). Dit zorgt ervoor dat de LLM genoeg tokens heeft om alle gegroepeerde commits te genereren zonder truncatie, zelfs voor grote changesets.

**Let op:** `--message-only` en `--group` sluiten elkaar uit. Gebruik `--message-only` wanneer u het commitbericht voor externe verwerking nodig heeft, en `--group` wanneer u meerdere commits binnen de huidige git-workflow wilt organiseren.

**Let op:** De `--interactive` vlag verstrekt extra context aan de LLM door vragen te stellen over uw wijzigingen, wat leidt tot nauwkeurigere en gedetailleerdere commitberichten. Dit is vooral handig voor complexe wijzigingen of wanneer u ervoor wilt zorgen dat het commitbericht de volledige context van uw werk vastlegt.

## Bericht Aanpassing

| Vlag / Optie        | Kort | Beschrijving                                                                  |
| ------------------- | ---- | ----------------------------------------------------------------------------- |
| `--one-liner`       | `-o` | Genereer een eenregelig commitbericht                                         |
| `--verbose`         | `-v` | Genereer gedetailleerde commitberichten met motivatie, architectuur, & impact |
| `--hint <tekst>`    | `-h` | Voeg een hint toe om de LLM te begeleiden                                     |
| `--model <model>`   | `-m` | Specificeer het model dat voor deze commit moet worden gebruikt               |
| `--language <taal>` | `-l` | Overschrijf de taal (naam of code: 'Spanish', 'es', 'zh-CN', 'ja')            |
| `--scope`           | `-s` | Stel een passende scope voor de commit vast                                   |
| `--50-72`           |      | De 50/72-regel toepassen voor commitberichtopmaak                             |

**Let op:** De `--50-72` vlag past de [50/72-regel](https://www.conventionalcommits.org/en/v1.0.0/#summary) toe waarbij:

- Onderwerpregel: maximaal 50 tekens
- Body-regels: maximaal 72 tekens per regel
- Dit houdt commitberichten leesbaar in `git log --oneline` en GitHub's UI

U kunt ook `GAC_USE_50_72_RULE=true` instellen in uw `.gac.env` bestand om deze regel altijd toe te passen.

**Let op:** U kunt interactief feedback geven door het gewoon op de bevestigingsprompt te typen - geen prefix met 'r' nodig. Typ `r` voor een eenvoudige reroll, `e` om het bericht te bewerken (standaard in-place TUI, of uw `$GAC_EDITOR` indien ingesteld), of typ uw feedback direct zoals `maak het korter`.

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
  gac -m anthropic:claude-haiku-4-5
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

- **Alleen het commitbericht ophalen (voor script-integratie):**

  ```sh
  gac --message-only
  # Voorbeeldoutput: feat: add user authentication system
  ```

- **Commitbericht in eenregel-formaat ophalen:**

  ```sh
  gac --message-only --one-liner
  # Voorbeeldoutput: feat: add user authentication system
  ```

- **Gebruik interactieve modus voor context:**

  ```sh
  gac -i
  # Wat is het hoofddoel van deze wijzigingen?
  # Welk probleem lost u op?
  # Zijn er implementatiedetails om te vermelden?
  ```

- **Interactieve modus met gedetailleerde output:**

  ```sh
  gac -i -v
  # Stel vragen en genereer gedetailleerde commitberichten
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

### SSL-certificaatverificatie

De `--no-verify-ssl` vlag staat u toe om SSL-certificaatverificatie voor API-aanroepen over te slaan:

```sh
gac --no-verify-ssl  # Sla SSL-verificatie over voor deze commit
```

**Om permanent in te stellen:** Stel `GAC_NO_VERIFY_SSL=true` in uw `.gac.env` bestand.

**Gebruik `--no-verify-ssl` wanneer:**

- Bedrijfsproxies SSL-verkeer onderscheppen (MITM-proxies)
- Ontwikkelomgevingen zelfondertekende certificaten gebruiken
- U SSL-certificaatfouten tegenkomt door netwerk beveiligingsinstellingen

**Let op:** Gebruik deze optie alleen in vertrouwde netwerkomgevingen. Het uitschakelen van SSL-verificatie vermindert de beveiliging en kan uw API-verzoeken kwetsbaar maken voor man-in-the-middle aanvallen.

### Signed-off-by Regel (DCO-naleving)

gac ondersteunt het toevoegen van een `Signed-off-by` regel aan commitberichten, wat vereist is voor naleving van de [Developer Certificate of Origin (DCO)](https://developercertificate.org/) in veel open-source projecten.

**Signoff toevoegen :**

```sh
gac --signoff  # Voeg Signed-off-by regel toe aan commitbericht (DCO-naleving)
```

**Om permanent in te stellen :** Stel `GAC_SIGNOFF=true` in je `.gac.env` bestand, of voeg `signoff=true` toe aan je configuratie.

**Wat het doet :**

- Voegt `Signed-off-by: Jouw Naam <jouw.email@example.com>` toe aan het commitbericht
- Gebruikt je git configuratie (`user.name` en `user.email`) voor de regel
- Vereist voor projecten zoals Cherry Studio, Linux kernel en andere die DCO gebruiken

**Git identiteit instellen :**

Zorg ervoor dat je git configuratie de juiste naam en email heeft :

```sh
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"
```

**Let op :** De Signed-off-by regel wordt toegevoegd door git tijdens de commit, niet door de AI tijdens berichtgeneratie. Je ziet het niet in de preview, maar het zal in de uiteindelijke commit zitten (controleer met `git log -1`).

## Configuratie Notities

- De aanbevolen manier om gac in te stellen is `gac init` uit te voeren en de interactieve prompts te volgen.
- Al geconfigureerde taal en alleen providers of modellen moeten wisselen? Voer `gac model` uit om de setup te herhalen zonder taalvragen.
- **Gebruikt u Claude Code?** Zie de [Claude Code installatiehandleiding](CLAUDE_CODE.md) voor OAuth-authenticatie-instructies.
- **Gebruikt u ChatGPT OAuth?** Zie de [ChatGPT OAuth installatiehandleiding](CHATGPT_OAUTH.md) voor browsergebaseerde authenticatie-instructies.
- **GitHub Copilot gebruiken?** Zie de [GitHub Copilot installatiehandleiding](GITHUB_COPILOT.md) voor Device Flow-authenticatie-instructies.
- gac laadt configuratie in de volgende volgorde van prioriteit:
  1. CLI vlaggen
  2. Omgevingsvariabelen
  3. Project-niveau `.gac.env`
  4. Gebruiker-niveau `~/.gac.env`

### Geavanceerde Configuratie Opties

U kunt het gedrag van gac aanpassen met deze optionele omgevingsvariabelen:

- `GAC_EDITOR=code --wait` - Overschrijf de editor die wordt gebruikt wanneer u `e` indrukt bij de bevestigingsprompt. Standaard opent `e` een in-place TUI; door `GAC_EDITOR` in te stellen schakelt u over naar een externe editor. Ondersteunt elke editoropdracht met argumenten. Wait-flags (`--wait`/`-w`) worden automatisch ingevoegd voor bekende GUI-editors (VS Code, Cursor, Zed, Sublime Text) zodat het proces blokkeert tot u het bestand sluit
- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Stel automatisch een scope en voeg deze toe aan commitberichten (bv., `feat(auth):` vs `feat:)
- `GAC_VERBOSE=true` - Genereer gedetailleerde commitberichten met motivatie, architectuur en impact secties
- `GAC_USE_50_72_RULE=true` - De 50/72-regel altijd toepassen voor commitberichten (onderwerp ≤50 tekens, body-regels ≤72 tekens)
- `GAC_SIGNOFF=true` - Altijd Signed-off-by regel toevoegen aan commits (voor DCO-naleving)
- `GAC_TEMPERATURE=0.7` - Controleer LLM creativiteit (0.0-1.0, lager = meer gefocust)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Maximale tokens voor gegenereerde berichten (automatisch geschaald 2-5x bij gebruik van `--group` op basis van bestandsaantal; overschrijf om hoger of lager te gaan)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Waarschuw wanneer prompts dit tokenaantal overschrijden
- `GAC_SYSTEM_PROMPT_PATH=/pad/naar/custom_prompt.txt` - Gebruik een custom system prompt voor commitberichtgeneratie
- `GAC_LANGUAGE=Spanish` - Genereer commitberichten in een specifieke taal (bv., Spanish, French, Japanese, German). Ondersteunt volledige namen of ISO codes (es, fr, ja, de, zh-CN). Gebruik `gac language` voor interactieve selectie
- `GAC_TRANSLATE_PREFIXES=true` - Vertaal conventionele commit prefixen (feat, fix, etc.) naar de doeltaal (standaard: false, houdt prefixen in Engels)
- `GAC_SKIP_SECRET_SCAN=true` - Schakel automatische security scanning voor geheimen in staged wijzigingen uit (gebruik met voorzichtigheid)
- `GAC_NO_VERIFY_SSL=true` - Sla SSL-certificaatverificatie over voor API-aanroepen (nuttig voor bedrijfsproxies die SSL-verkeer onderscheppen)
- `GAC_DISABLE_STATS=true` - Schakel tracking van gebruikstatistieken uit (geen lees- of schrijfbewerkingen naar het statistiekbestand; bestaande gegevens worden behouden). Alleen truthy-waarden schakelen statistieken uit; instellen op `false`/`0`/`no`/`off` houdt statistieken ingeschakeld, net als het weglaten van de variabele

Zie `.gac.env.example` voor een complete configuratiesjabloon.

Voor gedetailleerde begeleiding bij het maken van custom system prompts, zie [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md).

### Configuratie Subcommando's

De volgende subcommando's zijn beschikbaar:

- `gac init` — Interactieve setup wizard voor provider, model en taalconfiguratie
- `gac model` — Provider/model/API key setup zonder taalprompts (ideaal voor snelle wissels)
- `gac auth` — Toon OAuth-authenticatiestatus voor alle providers
- `gac auth claude-code login` — Inloggen op Claude Code met OAuth (opent browser)
- `gac auth claude-code logout` — Uitloggen uit Claude Code en opgeslagen token verwijderen
- `gac auth claude-code status` — Claude Code-authenticatiestatus controleren
- `gac auth chatgpt login` — Inloggen op ChatGPT met OAuth (opent browser)
- `gac auth chatgpt logout` — Uitloggen uit ChatGPT en opgeslagen token verwijderen
- `gac auth chatgpt status` — ChatGPT-authenticatiestatus controleren
- `gac auth copilot login` — Inloggen op GitHub Copilot via Device Flow
- `gac auth copilot login --host ghe.mycompany.com` — Inloggen op Copilot op een GitHub Enterprise-instantie
- `gac auth copilot logout` — Uitloggen bij Copilot en opgeslagen tokens verwijderen
- `gac auth copilot status` — Copilot-authenticatiestatus controleren
- `gac config show` — Huidige configuratie tonen
- `gac config set KEY VALUE` — Configuratiesleutel instellen in `$HOME/.gac.env`
- `gac config get KEY` — Configuratiewaarde krijgen
- `gac config unset KEY` — Configuratiesleutel verwijderen uit `$HOME/.gac.env`
- `gac language` (of `gac lang`) — Interactieve taalselector voor commitberichten (stelt GAC_LANGUAGE in)
- `gac editor` (of `gac edit`) — Interactieve editor-selector voor de `e`-knop bij de bevestigingsprompt (zet GAC_EDITOR)
- `gac diff` — Gefilterde git diff tonen met opties voor gestagede/ongestagede wijzigingen, kleur en truncatie
- `gac serve` — Start GAC als [MCP-server](MCP.md) voor AI-agent integratie (stdio transport)
- `gac stats show` — Bekijk uw gac-gebruiksstatistieken (totalen, streaks, dagelijkse & wekelijkse activiteit, tokengebruik, topprojecten, topmodellen)
- `gac stats models` — Bekijk gedetailleerde statistieken van alle modellen met token-uitsplitsing en snelheidsvergelijkingsgrafiek
- `gac stats project` — Bekijk statistieken alleen voor het huidige git-project
- `gac stats reset` — Reset alle statistieken naar nul (vraagt om bevestiging)

## Interactieve Modus

De `--interactive` (`-i`) vlag verbetert de commitberichtgeneratie van gac door gerichte vragen te stellen over uw wijzigingen. Deze extra context helpt de LLM om nauwkeurigere, gedetailleerdere en context-gepaste commitberichten te maken.

### Hoe het werkt

Wanneer u `--interactive` gebruikt, zal gac vragen stellen zoals:

- **Wat is het hoofddoel van deze wijzigingen?** - Helpt bij het begrijpen van het hoog-niveau doel
- **Welk probleem lost u op?** - Biedt context over de motivatie
- **Zijn er implementatiedetails om te vermelden?** - Vangt technische specificaties
- **Zijn er breaking changes?** - Identificeert potentiële impactproblemen
- **Is dit gerelateerd aan een issue of ticket?** - Koppelt aan projectmanagement

### Wanneer interactieve modus te gebruiken

Interactieve modus is vooral handig voor:

- **Complexe wijzigingen** waar de context niet duidelijk is uit de diff alleen
- **Refactoring werk** dat zich uitstrekt over meerdere bestanden en concepten
- **Nieuwe functies** die uitleg van het overall doel vereisen
- **Bug fixes** waar de oorzaak niet direct zichtbaar is
- **Prestatieoptimalisatie** waar de logica niet voor de hand ligt
- **Code review voorbereiding** - vragen helpen u om na te denken over uw wijzigingen

### Gebruiksvoorbeelden

**Basis interactieve modus:**

```sh
gac -i
```

Dit zal:

1. Een samenvatting tonen van gestagede wijzigingen
2. Vragen stellen over de wijzigingen
3. Een commitbericht genereren met uw antwoorden
4. Om bevestiging vragen (of automatisch bevestigen wanneer gecombineerd met `-y`)

**Interactieve modus met gestagede wijzigingen:**

```sh
gac -ai
# Stage alle wijzigingen, stel dan vragen voor betere context
```

**Interactieve modus met specifieke hints:**

```sh
gac -i -h "Databasemigratie voor gebruikersprofielen"
# Stel vragen terwijl u een specifieke hint geeft om de LLM te focussen
```

**Interactieve modus met gedetailleerde output:**

```sh
gac -i -v
# Stel vragen en genereer een gedetailleerd, gestructureerd commitbericht
```

**Automatisch bevestigde interactieve modus:**

```sh
gac -i -y
# Stel vragen maar bevestig de resulterende commit automatisch
```

### Vraag-Antwoord Workflow

De interactieve workflow volgt dit patroon:

1. **Wijzigingen review** - gac toont een samenvatting van wat u commit
2. **Beantwoord vragen** - geef antwoord op elke prompt met relevante details
3. **Context verbetering** - uw antwoorden worden toegevoegd aan de LLM prompt
4. **Berichtgeneratie** - de LLM maakt een commitbericht met volledige context
5. **Bevestiging** - review en bevestig de commit (of automatisch met `-y`)

**Tips voor nuttige antwoorden:**

- **Beknopt maar compleet** - geef belangrijke details zonder overdreven verbose te zijn
- **Focus op "waarom"** - leg de redenering achter uw wijzigingen uit
- **Vermeld beperkingen** - noteer beperkingen of speciale overwegingen
- **Link naar externe context** - verwijs naar issues, documentatie, of ontwerpdocumenten
- **Lege antwoorden zijn ok** - als een vraag niet van toepassing is, druk gewoon op Enter

### Combinatie met andere vlaggen

Interactieve modus werkt goed met de meeste andere vlaggen:

```sh
# Stage alle wijzigingen en stel vragen
gac -ai

# Stel vragen met gedetailleerde output
gac -i -v
```

### Beste Praktijken

- **Gebruik voor complexe PR's** - vooral handig voor pull requests die gedetailleerde uitleg nodig hebben
- **Team samenwerking** - vragen helpen u om na te denken over wijzigingen die anderen zullen reviewen
- **Documentatie voorbereiding** - uw antwoorden kunnen helpen bij het vormen van de basis voor release notes
- **Leerhulpmiddel** - vragen versterken goede praktijken voor commitberichten
- **Overslaan voor simpele wijzigingen** - voor triviale fixes kan de basismodus sneller zijn

## Gebruiksstatistieken

gac houdt lichtgewicht gebruikstatistieken bij, zodat u uw commitactiviteit, streaks, tokengebruik en meest actieve projecten en modellen kunt bekijken. Statistieken worden lokaal opgeslagen in `~/.gac_stats.json` en worden nergens naartoe gestuurd — er is geen telemetrie.

**Wat wordt bijgehouden:** totaal aantal gac-uitvoeringen, totaal aantal commits, totaal aantal prompt- en completion-tokens, eerste/laatste gebruiksdata, dagelijkse en wekelijkse tellingen (gacs, commits, tokens), huidige en langste streak, activiteit per project (gacs, commits, prompt + completion-tokens) en activiteit per model (gacs, prompt + completion-tokens).

**Wat NIET wordt bijgehouden:** commitberichten, code-inhoud, bestandspaden, persoonlijke informatie of iets anders dan tellingen, data, projectnamen (afgeleid van git remote of mapnaam) en modelnamen.

### Opt-in of Opt-out

`gac init` vraagt of u statistieken wilt inschakelen en legt uit wat er wordt opgeslagen. U kunt op elk moment van gedachten veranderen:

- **Statistieken inschakelen:** verwijder `GAC_DISABLE_STATS` of stel in op `false`/`0`/`no`/`off`/leeg.
- **Statistieken uitschakelen:** stel `GAC_DISABLE_STATS` in op een truthy-waarde (`true`, `1`, `yes`, `on`).

Wanneer u statistieken afwijst tijdens `gac init` en een bestaand `~/.gac_stats.json` wordt gedetecteerd, wordt u de optie geboden om het te verwijderen.

### Statistiek-subcommando's

| Commando            | Beschrijving                                                                                                                |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `gac stats`         | Uw statistieken bekijken (hetzelfde als `gac stats show`)                                                                   |
| `gac stats show`    | Volledige statistieken tonen: totalen, streaks, dagelijkse & wekelijkse activiteit, tokengebruik, topprojecten, topmodellen |
| `gac stats models`  | Gedetailleerde statistieken tonen van **alle** gebruikte modellen, met token-uitsplitsing en snelheidsvergelijkingsgrafiek  |
| `gac stats project` | Statistieken alleen voor het huidige git-project tonen                                                                      |
| `gac stats reset`   | Alle statistieken naar nul resetten (vraagt om bevestiging)                                                                 |

### Voorbeelden

```sh
# Uw algemene statistieken bekijken
gac stats

# Gedetailleerde uitsplitsing van alle gebruikte modellen
gac stats models

# Statistieken alleen voor het huidige project
gac stats project

# Alle statistieken resetten (met bevestigingsprompt)
gac stats reset
```

### Wat u zult zien

Het uitvoeren van `gac stats` toont:

- **Totaal aantal gacs en commits** — hoe vaak u gac heeft gebruikt en hoeveel commits het heeft gemaakt
- **Huidige en langste streak** — opeenvolgende dagen met gac-activiteit (🔥 bij 5+ dagen)
- **Activiteitssamenvatting** — gacs, commits en tokens van vandaag en deze week vergeleken met uw piekdag en piekweek
- **Topprojecten** — uw 5 meest actieve repos op basis van gac- + commit-aantal, met tokengebruik per project
- **Topmodellen** — uw 5 meest gebruikte modellen met verbruikte prompt-, completion- en totale tokens

Running `gac stats models` toont **alle** modellen (niet alleen de top 5) met:

- **Alle modellen-tabel** — elk gebruikt model gesorteerd op activiteit, met gac-aantal, snelheid (tokens/sec), prompt-tokens, completion-tokens, reasoning-tokens en totale tokens
- **Snelheidsvergelijking** — een horizontaal staafdiagram van alle modellen met bekende snelheden, gesorteerd van snelst naar traagst, kleurgecodeerd op snelheidspercentiel (🟡 bliksemsnel, 🟢 snel, 🔵 matig, 🔘 traag)
- **Highscore-vieringen** — 🏆 trofeeën wanneer u nieuwe dagelijkse, wekelijkse, token- of streak-records vestigt; 🥈 voor het evenaren ervan
- **Aanmoedigingsberichten** — contextuele aanmoedigingen op basis van uw activiteit

### Statistieken uitschakelen

Stel de omgevingsvariabele `GAC_DISABLE_STATS` in op een truthy-waarde:

```sh
# Statistiektracking uitschakelen
export GAC_DISABLE_STATS=true

# Of in .gac.env
GAC_DISABLE_STATS=true
```

Falsy-waarden (`false`, `0`, `no`, `off`, leeg) houden statistieken ingeschakeld — hetzelfde als het weglaten van de variabele.

Bij uitschakeling slaat gac alle statistiekregistratie over — er vinden geen bestandslees- of schrijfbewerkingen plaats. Bestaande gegevens worden behouden maar niet bijgewerkt totdat u ze weer inschakelt.

---

## Hulp Krijgen

- Voor MCP-server setup (AI-agent integratie), zie [docs/MCP.md](MCP.md)
- Voor custom system prompts, zie [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- Voor Claude Code OAuth-installatie, zie [CLAUDE_CODE.md](CLAUDE_CODE.md)
- Voor ChatGPT OAuth-installatie, zie [CHATGPT_OAUTH.md](CHATGPT_OAUTH.md)
- Voor GitHub Copilot-installatie, zie [GITHUB_COPILOT.md](GITHUB_COPILOT.md)
- Voor probleemoplossing en geavanceerde tips, zie [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Voor installatie en configuratie, zie [README.md#installation-and-configuration](README.md#installation-and-configuration)
- Om bij te dragen, zie [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Licentie informatie: [LICENSE](LICENSE)
