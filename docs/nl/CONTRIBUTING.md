# Bijdragen aan gac

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Norsk](../no/CONTRIBUTING.md) | [Svenska](../sv/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | **Nederlands** | [Italiano](../it/CONTRIBUTING.md)

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
