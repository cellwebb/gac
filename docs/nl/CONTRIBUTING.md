# Bijdragen aan gac

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | **Nederlands**

Bedankt voor uw interesse in bijdragen aan dit project! Uw hulp wordt gewaardeerd. Volg deze richtlijnen om het proces voor iedereen soepel te laten verlopen.

## Inhoudsopgave

- [Bijdragen aan gac](#bijdragen-aan-gac)
  - [Inhoudsopgave](#inhoudsopgave)
  - [Ontwikkelomgeving Instellen](#ontwikkelomgeving-instellen)
    - [Snelle Installatie](#snelle-installatie)
    - [Alternatieve Installatie (als u stapsgewijs prefereert)](#alternatieve-installatie-als-u-stapsgewijs-prefereert)
    - [Beschikbare Commando's](#beschikbare-commandos)
  - [Versie Bumping](#versie-bumping)
    - [Hoe de versie te bumpen](#hoe-de-versie-te-bumpen)
    - [Release Proces](#release-proces)
    - [Gebruik van bump-my-version (optioneel)](#gebruik-van-bump-my-version-optioneel)
  - [Een Nieuwe AI Provider Toevoegen](#een-nieuwe-ai-provider-toevoegen)
    - [Checklist voor het Toevoegen van een Nieuwe Provider](#checklist-voor-het-toevoegen-van-een-nieuwe-provider)
    - [Voorbeeld Implementatie](#voorbeeld-implementatie)
    - [Belangrijke Punten](#belangrijke-punten)
  - [Coderingsstandaarden](#coderingsstandaarden)
  - [Git Hooks (Lefthook)](#git-hooks-lefthook)
    - [Installatie](#installatie)
    - [Git Hooks Overslaan](#git-hooks-overslaan)
  - [Test Richtlijnen](#test-richtlijnen)
    - [Tests Uitvoeren](#tests-uitvoeren)
      - [Provider Integratietests](#provider-integratietests)
  - [Gedragscode](#gedragscode)
  - [Licentie](#licentie)
  - [Waar Hulp Krijgen](#waar-hulp-krijgen)

## Ontwikkelomgeving Instellen

Dit project gebruikt `uv` voor dependency management en biedt een Makefile voor veelvoorkomende ontwikkeltaken:

### Snelle Installatie

```bash
# Eén commando om alles in te stellen inclusief Lefthook hooks
make dev
```

Dit commando zal:

- Ontwikkeldependencies installeren
- Git hooks installeren
- Lefthook hooks uitvoeren op alle bestanden om bestaande problemen op te lossen

### Alternatieve Installatie (als u stapsgewijs prefereert)

```bash
# Creëer virtuele omgeving en installeer dependencies
make setup

# Installeer ontwikkeldependencies
make dev

# Installeer Lefthook hooks
brew install lefthook  # of zie docs hieronder voor alternatieven
lefthook install
lefthook run pre-commit --all
```

### Beschikbare Commando's

- `make setup` - Creëer virtuele omgeving en installeer alle dependencies
- `make dev` - **Volledige ontwikkelinstallatie** - inclusief Lefthook hooks
- `make test` - Voer standaard tests uit (exclusief integratietests)
- `make test-integration` - Voer alleen integratietests uit (vereist API sleutels)
- `make test-all` - Voer alle tests uit
- `make test-cov` - Voer tests uit met dekkingsrapport
- `make lint` - Controleer codekwaliteit (ruff, prettier, markdownlint)
- `make format` - Corrigeer code formatteringsproblemen automatisch

## Versie Bumping

**Belangrijk**: PR's moeten een versie bump bevatten in `src/gac/__version__.py` wanneer ze wijzigingen bevatten die moeten worden uitgebracht.

### Hoe de versie te bumpen

1. Bewerk `src/gac/__version__.py` en verhoog het versienummer
2. Volg [Semantic Versioning](https://semver.org/):
   - **Patch** (1.6.X): Bug fixes, kleine verbeteringen
   - **Minor** (1.X.0): Nieuwe features, backwards-compatibele wijzigingen (bv., een nieuwe provider toevoegen)
   - **Major** (X.0.0): Breaking changes

### Release Proces

Releases worden getriggerd door het pushen van versietags:

1. Merge PR(s) met versie bumps naar main
2. Creëer een tag: `git tag v1.6.1`
3. Push de tag: `git push origin v1.6.1`
4. GitHub Actions publiceert automatisch naar PyPI

Voorbeeld:

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # Bumped van 1.6.0
```

### Gebruik van bump-my-version (optioneel)

Als u `bump-my-version` geïnstalleerd heeft, kunt u het lokaal gebruiken:

```bash
# Voor bug fixes:
bump-my-version bump patch

# Voor nieuwe features:
bump-my-version bump minor

# Voor breaking changes:
bump-my-version bump major
```

## Een Nieuwe AI Provider Toevoegen

Bij het toevoegen van een nieuwe AI provider moet u meerdere bestanden in de codebase bijwerken. Volg deze uitgebreide checklist:

### Checklist voor het Toevoegen van een Nieuwe Provider

- [ ] **1. Creëer Provider Implementatie** (`src/gac/providers/<provider_name>.py`)

  - Creëer een nieuw bestand genaamd naar de provider (bv., `minimax.py`)
  - Implementeer `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str`
  - Gebruik het OpenAI-compatibele formaat als de provider dit ondersteunt
  - Handel API sleutel van omgevingsvariabele `<PROVIDER>_API_KEY` af
  - Inclusief juiste foutafhandeling met `AIError` types:
    - `AIError.authentication_error()` voor auth problemen
    - `AIError.rate_limit_error()` voor rate limits (HTTP 429)
    - `AIError.timeout_error()` voor timeouts
    - `AIError.model_error()` voor model fouten en lege/null content
  - Stel API endpoint URL in
  - Gebruik 120-seconden timeout voor HTTP verzoeken

- [ ] **2. Registreer Provider in Package** (`src/gac/providers/__init__.py`)

  - Voeg import toe: `from .<provider> import call_<provider>_api`
  - Voeg toe aan `__all__` lijst: `"call_<provider>_api"`

- [ ] **3. Registreer Provider in AI Module** (`src/gac/ai.py`)

  - Voeg import toe in het `from gac.providers import (...)` gedeelte
  - Voeg toe aan `provider_funcs` dictionary: `"provider-name": call_<provider>_api`

- [ ] **4. Voeg toe aan Ondersteunde Providers Lijst** (`src/gac/ai_utils.py`)

  - Voeg `"provider-name"` toe aan de `supported_providers` lijst in `generate_with_retries()`
  - Houd de lijst alfabetisch gesorteerd

- [ ] **5. Voeg toe aan Interactieve Setup** (`src/gac/init_cli.py`)

  - Voeg tuple toe aan `providers` lijst: `("Provider Name", "default-model-name")`
  - Houd de lijst alfabetisch gesorteerd
  - Voeg speciale handling toe indien nodig (zoals Ollama/LM Studio voor lokale providers)

- [ ] **6. Update Voorbeeldconfiguratie** (`.gac.env.example`)

  - Voeg voorbeeld modelconfiguratie toe in het formaat: `# GAC_MODEL=provider:model-name`
  - Voeg API sleutel entry toe: `# <PROVIDER>_API_KEY=your_key_here`
  - Houd entries alfabetisch gesorteerd
  - Voeg commentaren toe voor optionele sleutels indien van toepassing

- [ ] **7. Update Documentatie** (`README.md` en `docs/zh-CN/README.md`)

  - Voeg providernaam toe aan de "Supported Providers" sectie in zowel Engelse als Chinese README's
  - Houd de lijst alfabetisch gesorteerd binnen de bullet points

- [ ] **8. Creëer Uitgebreide Tests** (`tests/providers/test_<provider>.py`)

  - Creëer testbestand volgens de naamconventie
  - Inclusief deze testklassen:
    - `Test<Provider>Imports` - Test module en functie imports
    - `Test<Provider>APIKeyValidation` - Test missende API sleutel fout
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - Erf van `BaseProviderTest` voor 9 standaard tests
    - `Test<Provider>EdgeCases` - Test null content en andere edge cases
    - `Test<Provider>Integration` - Echte API aanroep tests (gemarkeerd met `@pytest.mark.integration`)
  - Implementeer vereiste properties in de mocked testklasse:
    - `provider_name` - Provider naam (kleine letters)
    - `provider_module` - Volledige modulepad
    - `api_function` - De API functie referentie
    - `api_key_env_var` - Omgevingsvariabele naam voor API sleutel (of None voor lokale providers)
    - `model_name` - Standaard modelnaam voor testen
    - `success_response` - Mock succesvolle API response
    - `empty_content_response` - Mock lege content response

- [ ] **9. Bump Versie** (`src/gac/__version__.py`)
  - Verhoog de **minor** versie (bv., 1.10.2 → 1.11.0)
  - Een provider toevoegen is een nieuw feature en vereist een minor versie bump

### Voorbeeld Implementatie

Zie de MiniMax provider implementatie als referentie:

- Provider: `src/gac/providers/minimax.py`
- Tests: `tests/providers/test_minimax.py`

### Belangrijke Punten

1. **Foutafhandeling**: Gebruik altijd het juiste `AIError` type voor verschillende foutscenario's
2. **Null/Lege Content**: Controleer altijd op zowel `None` als lege string content in responses
3. **Testing**: De `BaseProviderTest` klasse biedt 9 standaard tests die elke provider moet erven
4. **Alfabetische Volgorde**: Houd providerlijsten alfabetisch gesorteerd voor onderhoudbaarheid
5. **API Sleutel Naamgeving**: Gebruik het formaat `<PROVIDER>_API_KEY` (allemaal hoofdletters, underscores voor spaties)
6. **Provider Naam Formaat**: Gebruik kleine letters met streepjes voor meerwoordnamen (bv., "lm-studio")
7. **Versie Bump**: Een provider toevoegen vereist een **minor** versie bump (nieuw feature)

## Coderingsstandaarden

- Target Python 3.10+ (3.10, 3.11, 3.12, 3.13, 3.14)
- Gebruik type hints voor alle functieparameters en returnwaarden
- Houd code schoon, compact en leesbaar
- Vermijd onnodige complexiteit
- Gebruik logging in plaats van print statements
- Formattering wordt afgehandeld door `ruff` (linting, formattering en import sortering in één tool; maximale lijnlengte: 120)
- Schrijf minimale, effectieve tests met `pytest`

## Git Hooks (Lefthook)

Dit project gebruikt [Lefthook](https://github.com/evilmartians/lefthook) om codekwaliteitscontroles snel en consistent te houden. De geconfigureerde hooks spiegelen onze vorige pre-commit setup:

- `ruff` - Python linting en formattering (vervangt black, isort en flake8)
- `markdownlint-cli2` - Markdown linting
- `prettier` - Bestandsformattering (markdown, yaml, json)
- `check-upstream` - Custom hook om upstream wijzigingen te controleren

### Installatie

**Aanbevolen aanpak:**

```bash
make dev
```

**Handmatige installatie (als u stapsgewijs prefereert):**

1. Installeer Lefthook (kies de optie die bij uw setup past):

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # of
   cargo install lefthook         # Rust toolchain
   # of
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. Installeer de git hooks:

   ```sh
   lefthook install
   ```

3. (Optioneel) Voer uit op alle bestanden:

   ```sh
   lefthook run pre-commit --all
   ```

De hooks worden nu automatisch uitgevoerd bij elke commit. Als controles mislukken, moet u de problemen oplossen voordat u commit.

### Git Hooks Overslaan

Als u de Lefthook controles tijdelijk moet overslaan, gebruik de `--no-verify` vlag:

```sh
git commit --no-verify -m "Uw commitbericht"
```

Let op: Dit moet alleen worden gebruikt wanneer het absoluut noodzakelijk is, omdat het belangrijke codekwaliteitscontroles omzeilt.

## Test Richtlijnen

Het project gebruikt pytest voor testing. Bij het toevoegen van nieuwe features of het fixen van bugs, voeg tests toe die uw wijzigingen dekken.

Merkt op dat de `scripts/` directory testscripts bevat voor functionaliteit die niet gemakkelijk met pytest getest kan worden.
Voel vrij om scripts hier toe te voegen voor het testen van complexe scenario's of integratietests die moeilijk te implementeren zouden zijn
met het standaard pytest framework.

### Tests Uitvoeren

```sh
# Voer standaard tests uit (exclusief integratietests met echte API aanroepen)
make test

# Voer alleen provider integratietests uit (vereist API sleutels)
make test-integration

# Voer alle tests uit inclusief provider integratietests
make test-all

# Voer tests uit met coverage
make test-cov

# Voer specifiek testbestand uit
uv run -- pytest tests/test_prompt.py

# Voer specifieke test uit
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### Provider Integratietests

Provider integratietests doen echte API aanroepen om te verifiëren dat providerimplementaties correct werken met daadwerkelijke API's. Deze tests zijn gemarkeerd met `@pytest.mark.integration` en worden standaard overgeslagen om:

- API credits te vermijden tijdens reguliere ontwikkeling
- Testfouten te voorkomen wanneer API sleutels niet geconfigureerd zijn
- Testuitvoering snel te houden voor snelle iteratie

Om provider integratietests uit te voeren:

1. **Stel API sleutels in** voor de providers die u wilt testen:

   ```sh
   export ANTHROPIC_API_KEY="uw-sleutel"
   export CEREBRAS_API_KEY="uw-sleutel"
   export GEMINI_API_KEY="uw-sleutel"
   export GROQ_API_KEY="uw-sleutel"
   export OPENAI_API_KEY="uw-sleutel"
   export OPENROUTER_API_KEY="uw-sleutel"
   export STREAMLAKE_API_KEY="uw-sleutel"
   export ZAI_API_KEY="uw-sleutel"
   # LM Studio en Ollama vereisen een lokaal instance dat draait
   # API sleutels voor LM Studio en Ollama zijn optioneel tenzij uw deployment authenticatie afdwingt
   ```

2. **Voer provider tests uit**:

   ```sh
   make test-integration
   ```

Tests slaan providers over waar API sleutels niet geconfigureerd zijn. Deze tests helpen bij het vroegtijdig detecteren van API wijzigingen en zorgen voor compatibiliteit met provider API's.

## Gedragscode

Wees respectvol en constructief. Intimidatie of misbruik gedrag wordt niet getolereerd.

## Licentie

Door bij te dragen, gaat u ermee akkoord dat uw bijdragen worden gelicenseerd onder dezelfde licentie als het project.

---

## Waar Hulp Krijgen

- Voor probleemoplossing, zie [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Voor gebruik en CLI opties, zie [USAGE.md](USAGE.md)
- Voor licentiedetails, zie [../../LICENSE](../../LICENSE)

Bedankt voor het helpen verbeteren van gac!
