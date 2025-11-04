# Bidra till gac

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Norsk](../no/CONTRIBUTING.md) | **Svenska** | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md) | [Italiano](../it/CONTRIBUTING.md)

Tack för ditt intresse att bidra till detta projekt! Din hjälp uppskattas. Följ dessa riktlinjer för att göra processen smidig för alla.

## Innehållsförteckning

- [Bidra till gac](#bidra-till-gac)
  - [Innehållsförteckning](#innehållsförteckning)
  - [Installation av utvecklingsmiljö](#installation-av-utvecklingsmiljö)
    - [Snabb installation](#snabb-installation)
    - [Alternativ installation (om du föredrar steg-för-steg)](#alternativ-installation-om-du-föredrar-steg-för-steg)
    - [Tillgängliga kommandon](#tillgängliga-kommandon)
  - [Versionshantering](#versionshantering)
    - [Hur man uppdaterar versionen](#hur-man-uppdaterar-versionen)
    - [Releaseprocess](#releaseprocess)
    - [Använda bump-my-version (valfritt)](#använda-bump-my-version-valfritt)
  - [Lägga till en ny AI-leverantör](#att-lägga-till-en-ny-ai-leverantör)
    - [Checklista för att lägga till en ny leverantör](#checklista-för-att-lägga-till-en-ny-leverantör)
    - [Exempelimplementation](#exempelimplementation)
    - [Viktiga punkter](#viktiga-punkter)
  - [Kodstandarder](#kodstandarder)
  - [Git Hooks (Lefthook)](#git-hooks-lefthook)
    - [Installation](#installation)
    - [Hoppa över Git Hooks](#hoppa-över-git-hooks)
  - [Testeriktlinjer](#testriktlinjer)
    - [Köra tester](#köra-tester)
      - [Integrationstester](#integrationstester)
  - [Uppförandekod](#uppförandekod)
  - [Licens](#licens)
  - [Var får man hjälp](#var-får-man-hjälp)

## Installation av utvecklingsmiljö

Detta projekt använder `uv` för hantering av beroenden och tillhandahåller en Makefile för vanliga utvecklingsuppgifter:

### Snabb installation

```bash
# Ett kommando för att installera allt inklusive Lefthook hooks
make dev
```

Detta kommando kommer att:

- Installera utvecklingsberoenden
- Installera git hooks
- Köra Lefthook hooks genom alla filer för att åtgärda eventuella existerande problem

### Alternativ installation (om du föredrar steg-för-steg)

```bash
# Skapa virtuell miljö och installera beroenden
make setup

# Installera utvecklingsberoenden
make dev

# Installera Lefthook hooks
brew install lefthook  # eller se dokumentation nedan för alternativ
lefthook install
lefthook run pre-commit --all
```

### Tillgängliga kommandon

- `make setup` - Skapa virtuell miljö och installera alla beroenden
- `make dev` - **Fullständig installation för utveckling** - inkluderar Lefthook hooks
- `make test` - Kör standardtester (exkluderar integrationstester)
- `make test-integration` - Kör endast integrationstester (kräver API-nycklar)
- `make test-all` - Kör alla tester
- `make test-cov` - Kör test med täckningsrapport
- `make lint` - Kontrollera kodkvalitet (ruff, prettier, markdownlint)
- `make format` - Automatisk korrigering av kodformat

## Versionshantering

**Viktigt**: PRs bör inkludera en versionsuppdatering i `src/gac/__version__.py` när de innehåller ändringar som bör släppas.

### Hur man uppdaterar versionen

1. Redigera `src/gac/__version__.py` och öka versionsnumret
2. Följ [Semantisk Versionshantering](https://semver.org/):
   - **Patch** (1.6.X): Buggfixar, små förbättringar
   - **Minor** (1.X.0): Nya funktioner, bakåtkompatibla ändringar (t.ex. lägga till en ny leverantör)
   - **Major** (X.0.0): Brytande ändringar

### Releaseprocess

Releases triggreras genom att pusha versionstaggar:

1. Merge:a PR(s) med versionsuppdateringar till main
2. Skapa en tagg: `git tag v1.6.1`
3. Pusha taggen: `git push origin v1.6.1`
4. GitHub Actions publicerar automatiskt till PyPI

Exempel:

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # Uppdaterad från 1.6.0
```

### Använda bump-my-version (valfritt)

Om du har `bump-my-version` installerat kan du använda det lokalt:

```bash
# För buggfixar:
bump-my-version bump patch

# För nya funktioner:
bump-my-version bump minor

# För brytande ändringar:
bump-my-version bump major
```

## Att lägga till en ny AI-leverantör

När du lägger till en ny AI-leverantör behöver du uppdatera flera filer i kodbasen. Följ denna omfattande checklista:

### Checklista för att lägga till en ny leverantör

- [ ] **1. Skapa leverantörsimplementation** (`src/gac/providers/<provider_name>.py`)

  - Skapa en ny fil med namn efter leverantören (t.ex. `minimax.py`)
  - Implementera `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str`
  - Använd OpenAI-kompatibelt format om leverantören stöder det
  - Hantera API-nyckel från miljövariabel `<PROVIDER>_API_KEY`
  - Inkludera korrekt felhantering med `AIError` typer:
    - `AIError.authentication_error()` för autentiseringsproblem
    - `AIError.rate_limit_error()` för hastighetsgränser (HTTP 429)
    - `AIError.timeout_error()` för timeout
    - `AIError.model_error()` för modellfel och tomt/innehåll
  - Ange API endpoint URL
  - Använd 120 sekunders timeout för HTTP-begäranden

- [ ] **2. Registrera leverantör i paketet** (`src/gac/providers/__init__.py`)

  - Lägg till import: `from .<provider> import call_<provider>_api`
  - Lägg till i `__all__` listan: `"call_<provider>_api"`

- [ ] **3. Registrera leverantör i AI-modulen** (`src/gac/ai.py`)

  - Lägg till import i sektionen `from gac.providers import (...)`
  - Lägg till i `provider_funcs` ordbok: `"provider-name": call_<provider>_api`

- [ ] **4. Lägg till i listan med stödda leverantörer** (`src/gac/ai_utils.py`)

  - Lägg till `"provider-name"` till listan `supported_providers` i `generate_with_retries()`
  - Håll listan sorterad alfabetiskt

- [ ] **5. Lägg till interaktiv installation** (`src/gac/init_cli.py`)

  - Lägg till tuple till listan `providers`: `("Provider Name", "standard-modell-namn")`
  - Håll listan sorterad alfabetiskt
  - Lägg till specialhantering om nödvändigt (som Ollama/LM Studio för lokala leverantörer)

- [ ] **6. Uppdatera exempelkonfiguration** (`.gac.env.example`)

  - Lägg till exempelmodellkonfiguration i formatet: `# GAC_MODEL=provider:modell-namn`
  - Lägg till API-nyckel: `# <PROVIDER>_API_KEY=din_nyckel_här`
  - Håll poster sorterade alfabetiskt
  - Lägg till kommentarer för valfria nycklar om tillämpligt

- [ ] **7. Uppdatera dokumentation** (`README.md` och `docs/sv/README.md`)

  - Lägg till leverantörens namn till "Supported Providers" i både engelska och svenska READMEs
  - Håll listan sorterade alfabetiskt i sina punkter

- [ ] **8. Skapa omfattande tester** (`tests/providers/test_<provider>.py`)

  - Skapa testfil med namnkonventionen
  - Inkludera dessa testklasser:
    - `Test<Provider>Imports` - Testa modul- och funktionsimporter
    - `Test<Provider>APIKeyValidation` - Testa saknad API-nyckel fel
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - Ärv från `BaseProviderTest` för 9 standardtester
    - `Test<Provider>EdgeCases` - Testa tomt innehåll och andra edge-cases
    - `Test<Provider>Integration` - Riktiga API-anropstester (markerade med `@pytest.mark.integration`)
  - Implementera nödvändiga egenskaper i den mockade testklassen:
    - `provider_name` - Leverantörens namn (gemener)
    - `provider_module` - Fullständig modulsökväg
    - `api_function` - API-funktionens referens
    - `api_key_env_var` - Miljövariabelens namn för API-nyckel (eller None för lokala leverantörer)
    - `model_name` - Standardmodellnamn för testning
    - `success_response` - Mocka lyckat API-svar
    - `empty_content_response` - Mocka tomt innehåll svar

- [ ] **9. Uppdatera version** (`src/gac/__version__.py`)
  - Öka **minor** versionen (t.ex. 1.10.2 → 1.11.0)
  - Att lägga till en leverantör kräver en mindre versionsuppdatering (ny funktion)

### Exempelimplementation

Se MiniMax leverantörsimplementation som referens:

- Leverantör: `src/gac/providers/minimax.py`
- Tester: `tests/providers/test_minimax.py`

### Viktiga punkter

1. **Felhantering**: Använd alltid lämplig `AIError` typ för olika felscenarier
2. **Null/Tomt innehåll**: Kontrollera alltid både `None` och tomma strängar i svar
3. **Testning**: `BaseProviderTest` klassen tillhandahåller 9 standardtester som varje leverantör bör ärva
4. **Alfabetisk ordning**: Håll listan med leverantörer sorterad alfabetiskt för underhållbarhet
5. **API-nyckel namngivning**: Använd formatet `<PROVIDER>_API_KEY` (alla versaler, understreck för mellanslag)
6. **Leverantörens namnformat**: Använd gemener med bindestreck för flerord namn (t.ex. "lm-studio")
7. **Versionsuppdatering**: Att lägga till en leverantör kräver en **mindre** versionsuppdatering (ny funktion)

## Kodstandarder

- Mål Python 3.10+ (3.10, 3.11, 3.12, 3.13, 3.14)
- Använd typ hints för alla funktionsparametrar och returvärden
- Håll koden ren, kompakt och läsbar
- Undvik onödig komplexitet
- Använd loggning istället för print-satser
- Formatering hanteras av `ruff` (linting, formatering och importsortering i ett verktyg; max radlängd: 120)
- Skriv minimala, effektiva tester med `pytest`

## Git Hooks (Lefthook)

Detta projekt använder [Lefthook](https://github.com/evilmartians/lefthook) för att hålla kontroller av kodkvalitet snabba och konsekventa. De konfigurerade hookarna speglar våra tidigare pre-commit konfigurationer:

- `ruff` - Python lintern och formateraren (ersätter black, isort och flake8)
- `markdownlint-cli2` - Markdown lintern
- `prettier` - Filformatering (markdown, yaml, json)
- `check-upstream` - Anpassad hook för att kontrollera upströmsändringar

### Installation

**Rekommenderat tillvägagångssätt:**

```bash
make dev
```

**Manuell installation (om du föredrar steg-för-steg):**

1. Installera Lefthook (välj alternativet som matchar din installation):

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # eller
   cargo install lefthook         # Rust toolchain
   # eller
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. Installera git hooks:

   ```sh
   lefthook install
   ```

3. (Valfritt) Kör genom alla filer:

   ```sh
   lefthook run pre-commit --all
   ```

Hooks kommer nu köras automatiskt vid varje commit. Om några kontroller misslyckas måste du åtgärda problemen innan du kan committa.

### Hoppa över Git Hooks

Om du behöver hoppa över Lefthook kontroller temporärt, använd flaggan `--no-verify`:

```sh
git commit --no-verify -m "Ditt commit-meddelande"
```

Observera: Detta bör endast användas när det är absolut nödvändigt eftersom det förbigår viktiga kontroller av kodkvalitet.

## Testriktlinjer

Projektet använder pytest för testning. När du lägger till nya funktioner eller fixar buggar, vänligen inkludera tester som täcker dina ändringar.

Observera att katalogen `scripts/` innehåller testskript för funktionalitet som inte lätt kan testas med pytest. Lägg gärna till skript här för att testa komplexa scenarier eller integrationstester som skulle vara svåra att implementera med standard pytest-ramverket.

### Köra tester

```sh
# Kör standardtester (exkluderar integrationstester med riktiga API-anrop)
make test

# Kör endast provider-integrationstester (kräver API-nycklar)
make test-integration

# Kör alla tester inklusive provider-integrationstester
make test-all

# Kör tester med täckning
make test-cov

# Kör specifik testfil
uv run -- pytest tests/test_prompt.py

# Kör specifikt test
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### Integrationstester

Integrationstester för leverantörer gör riktiga API-anrop för att verifiera att leverantörsimplementationer fungerar korrekt med riktiga API:er. Dessa tester är markerade med `@pytest.mark.integration` och hoppas över som standard för att:

- Undvika att konsumera API-krediter under vanlig utveckling
- Förhindra testfel när API-nycklar inte är konfigurerade
- Hålla testexekvering snabb för snabb iteration

För att köra integrationstester för leverantörer:

1. **Ställ in API-nycklar** för de leverantörer du vill testa:

   ```sh
   export ANTHROPIC_API_KEY="din-nyckel"
   export CEREBRAS_API_KEY="din-nyckel"
   export GEMINI_API_KEY="din-nyckel"
   export GROQ_API_KEY="din-nyckel"
   export OPENAI_API_KEY="din-nyckel"
   export OPENROUTER_API_KEY="din-nyckel"
   export STREAMLAKE_API_KEY="din-nyckel"
   export ZAI_API_KEY="din-nyckel"
   # LM Studio och Ollama kräver en lokal instans som körs
   # API-nycklar för LM Studio och Ollama är valfria om inte din deployment kräver autentisering
   ```

2. **Kör providerstester**:

   ```sh
   make test-integration
   ```

Tester kommer hoppa över leverantörer där API-nycklar inte är konfigurerade. Dessa tester hjälper till att upptäcka API-ändringar tidigt och säkerställa kompatibilitet med leverantörens API:er.

## Uppförandekod

Var respektfull och konstruktiv. Trakasserier eller missbrukande beteende kommer inte tolereras.

## Licens

Genom att bidra samtycker du till att dina bidrag kommer licensieras under samma licens som projektet.

---

## Var får man hjälp

- För felsökning, se [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- För användning och CLI-alternativ, se [USAGE.md](USAGE.md)
- För licensinformation, se [../../LICENSE](../../LICENSE)

Tack för att du hjälper till att förbättra gac!
