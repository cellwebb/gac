# Mitwirken an gac

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Norsk](../no/CONTRIBUTING.md) | [Svenska](../sv/CONTRIBUTING.md) | **Deutsch** | [Nederlands](../nl/CONTRIBUTING.md) | [Italiano](../it/CONTRIBUTING.md)

Vielen Dank für Ihr Interesse an der Mitarbeit an diesem Projekt! Ihre Hilfe wird geschätzt. Bitte befolgen Sie diese Richtlinien, um den Prozess für alle reibungslos zu gestalten.

## Inhaltsverzeichnis

- [Mitwirken an gac](#mitwirken-an-gac)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Entwicklungsumgebung einrichten](#entwicklungsumgebung-einrichten)
    - [Schnelleinrichtung](#schnelleinrichtung)
    - [Alternative Einrichtung (wenn Sie Schritt-für-Schritt bevorzugen)](#alternative-einrichtung-wenn-sie-schritt-für-schritt-bevorzugen)
    - [Verfügbare Befehle](#verfügbare-befehle)
  - [Versionserhöhung](#versionserhöhung)
    - [Version erhöhen](#version-erhöhen)
    - [Veröffentlichungsprozess](#veröffentlichungsprozess)
    - [bump-my-version verwenden (optional)](#bump-my-version-verwenden-optional)
  - [Neuen KI-Anbieter hinzufügen](#neuen-ki-anbieter-hinzufügen)
    - [Checkliste für das Hinzufügen eines neuen Anbieters](#checkliste-für-das-hinzufügen-eines-neuen-anbieters)
    - [Beispiel-Implementierung](#beispiel-implementierung)
    - [Wichtige Punkte](#wichtige-punkte)
  - [Codierungsstandards](#codierungsstandards)
  - [Git Hooks (Lefthook)](#git-hooks-lefthook)
    - [Einrichtung](#einrichtung)
    - [Git Hooks überspringen](#git-hooks-überspringen)
  - [Testrichtlinien](#testrichtlinien)
    - [Tests ausführen](#tests-ausführen)
      - [Anbieter-Integrationstests](#anbieter-integrationstests)
  - [Verhaltenskodex](#verhaltenskodex)
  - [Lizenz](#lizenz)
  - [Wo man Hilfe bekommt](#wo-man-hilfe-bekommt)

## Entwicklungsumgebung einrichten

Dieses Projekt verwendet `uv` für die Abhängigkeitsverwaltung und stellt eine Makefile für häufige Entwicklungsaufgaben bereit:

### Schnelleinrichtung

```bash
# Ein Befehl zur Einrichtung von allem, einschließlich Lefthook-Hooks
make dev
```

Dieser Befehl wird:

- Entwicklungsabhängigkeiten installieren
- Git-Hooks installieren
- Lefthook-Hooks für alle Dateien ausführen, um bestehende Probleme zu beheben

### Alternative Einrichtung (wenn Sie Schritt-für-Schritt bevorzugen)

```bash
# Virtuelle Umgebung erstellen und Abhängigkeiten installieren
make setup

# Entwicklungsabhängigkeiten installieren
make dev

# Lefthook-Hooks installieren
brew install lefthook  # oder siehe unten für Alternativen
lefthook install
lefthook run pre-commit --all
```

### Verfügbare Befehle

- `make setup` - Virtuelle Umgebung erstellen und alle Abhängigkeiten installieren
- `make dev` - **Vollständige Entwicklungseinrichtung** - einschließlich Lefthook-Hooks
- `make test` - Standardtests ausführen (schließt Integrationstests aus)
- `make test-integration` - Nur Integrationstests ausführen (benötigt API-Schlüssel)
- `make test-all` - Alle Tests ausführen
- `make test-cov` - Tests mit Coverage-Bericht ausführen
- `make lint` - Codequalität prüfen (ruff, prettier, markdownlint)
- `make format` - Code-Formatierungsprobleme automatisch beheben

## Versionserhöhung

**Wichtig**: Pull Requests sollten eine Versionserhöhung in `src/gac/__version__.py` enthalten, wenn sie Änderungen enthalten, die veröffentlicht werden sollen.

### Version erhöhen

1. Bearbeiten Sie `src/gac/__version__.py` und erhöhen Sie die Versionsnummer
2. Folgen Sie der [Semantischen Versionierung](https://semver.org/):
   - **Patch** (1.6.X): Fehlerbehebungen, kleine Verbesserungen
   - **Minor** (1.X.0): Neue Funktionen, abwärtskompatible Änderungen (z.B. Hinzufügen eines neuen Anbieters)
   - **Major** (X.0.0): Breaking Changes

### Veröffentlichungsprozess

Veröffentlichungen werden durch das Pushen von Version-Tags ausgelöst:

1. PR(s) mit Versionserhöhungen in main zusammenführen
2. Einen Tag erstellen: `git tag v1.6.1`
3. Den Tag pushen: `git push origin v1.6.1`
4. GitHub Actions veröffentlicht automatisch auf PyPI

Beispiel:

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # Erhöht von 1.6.0
```

### bump-my-version verwenden (optional)

Wenn Sie `bump-my-version` installiert haben, können Sie es lokal verwenden:

```bash
# Für Fehlerbehebungen:
bump-my-version bump patch

# Für neue Funktionen:
bump-my-version bump minor

# Für Breaking Changes:
bump-my-version bump major
```

## Neuen KI-Anbieter hinzufügen

Beim Hinzufügen eines neuen KI-Anbieters müssen Sie mehrere Dateien im gesamten Codebase aktualisieren. Befolgen Sie diese umfassende Checkliste:

### Checkliste für das Hinzufügen eines neuen Anbieters

- [ ] **1. Anbieter-Implementierung erstellen** (`src/gac/providers/<provider_name>.py`)

  - Eine neue Datei nach dem Anbieter benennen (z.B. `minimax.py`)
  - `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str` implementieren
  - OpenAI-kompatibles Format verwenden, wenn der Anbieter es unterstützt
  - API-Schlüssel aus Umgebungsvariable `<PROVIDER>_API_KEY` behandeln
  - Fehlerbehandlung mit `AIError`-Typen einbeziehen:
    - `AIError.authentication_error()` für Auth-Probleme
    - `AIError.rate_limit_error()` für Ratenlimits (HTTP 429)
    - `AIError.timeout_error()` für Timeouts
    - `AIError.model_error()` für Modellfehler und leere/null Inhalte
  - API-Endpunkt-URL setzen
  - 120-Sekunden-Timeout für HTTP-Anfragen verwenden

- [ ] **2. Anbieter im Paket registrieren** (`src/gac/providers/__init__.py`)

  - Import hinzufügen: `from .<provider> import call_<provider>_api`
  - Zur `__all__`-Liste hinzufügen: `"call_<provider>_api"`

- [ ] **3. Anbieter in AI-Modul registrieren** (`src/gac/ai.py`)

  - Import im Abschnitt `from gac.providers import (...)` hinzufügen
  - Zum `provider_funcs`-Dictionary hinzufügen: `"provider-name": call_<provider>_api`

- [ ] **4. Zur Liste der unterstützten Anbieter hinzufügen** (`src/gac/ai_utils.py`)

  - `"provider-name"` zur `supported_providers`-Liste in `generate_with_retries()` hinzufügen
  - Die Liste alphabetisch sortiert halten

- [ ] **5. Zur interaktiven Einrichtung hinzufügen** (`src/gac/init_cli.py`)

  - Tupel zur `providers`-Liste hinzufügen: `("Provider Name", "default-model-name")`
  - Die Liste alphabetisch sortiert halten
  - Spezielle Behandlung hinzufügen, falls erforderlich (wie Ollama/LM Studio für lokale Anbieter)

- [ ] **6. Beispiel-Konfiguration aktualisieren** (`.gac.env.example`)

  - Beispiel-Modellkonfiguration im Format hinzufügen: `# GAC_MODEL=provider:model-name`
  - API-Schlüssel-Eintrag hinzufügen: `# <PROVIDER>_API_KEY=your_key_here`
  - Einträge alphabetisch sortiert halten
  - Kommentare für optionale Schlüssel hinzufügen, falls zutreffend

- [ ] **7. Dokumentation aktualisieren** (`README.md` und `docs/zh-CN/README.md`)

  - Anbietername zum Abschnitt "Supported Providers" in beiden englischen und chinesischen READMEs hinzufügen
  - Die Liste innerhalb ihrer Aufzählungspunkte alphabetisch sortiert halten

- [ ] **8. Umfassende Tests erstellen** (`tests/providers/test_<provider>.py`)

  - Testdatei nach Namenskonvention erstellen
  - Diese Testklassen einschließen:
    - `Test<Provider>Imports` - Modul- und Funktions-Imports testen
    - `Test<Provider>APIKeyValidation` - Fehler bei fehlendem API-Schlüssel testen
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - Von `BaseProviderTest` erben für 9 Standardtests
    - `Test<Provider>EdgeCases` - Null-Inhalte und andere Grenzfälle testen
    - `Test<Provider>Integration` - Echte API-Aufruf-Tests (markiert mit `@pytest.mark.integration`)
  - Erforderliche Eigenschaften in der Mock-Testklasse implementieren:
    - `provider_name` - Anbietername (kleingeschrieben)
    - `provider_module` - Vollständiger Modulpfad
    - `api_function` - Die API-Funktionsreferenz
    - `api_key_env_var` - Umgebungsvariablenname für API-Schlüssel (oder None für lokale Anbieter)
    - `model_name` - Standard-Modellname für Tests
    - `success_response` - Mock-erfolgreiche API-Antwort
    - `empty_content_response` - Mock-Antwort mit leerem Inhalt

- [ ] **9. Version erhöhen** (`src/gac/__version__.py`)
  - Die **Minor**-Version erhöhen (z.B. 1.10.2 → 1.11.0)
  - Das Hinzufügen eines Anbieters ist eine neue Funktion und erfordert eine Minor-Versionserhöhung

### Beispiel-Implementierung

Siehe die MiniMax-Anbieter-Implementierung als Referenz:

- Anbieter: `src/gac/providers/minimax.py`
- Tests: `tests/providers/test_minimax.py`

### Wichtige Punkte

1. **Fehlerbehandlung**: Immer den geeigneten `AIError`-Typ für unterschiedliche Fehlerszenarien verwenden
2. **Null/Leere Inhalte**: Immer sowohl `None` als auch leere Zeichenketten-Inhalte in Antworten prüfen
3. **Testing**: Die `BaseProviderTest`-Klasse bietet 9 Standardtests, die jeder Anbieter erben sollte
4. **Alphabetische Reihenfolge**: Anbieterlisten alphabetisch sortiert halten für Wartbarkeit
5. **API-Schlüssel-Benennung**: Format `<PROVIDER>_API_KEY` verwenden (alles großgeschrieben, Unterstriche für Leerzeichen)
6. **Anbietername-Format**: Kleinbuchstaben mit Bindestrichen für mehrwortige Namen (z.B. "lm-studio")
7. **Versionserhöhung**: Hinzufügen eines Anbieters erfordert eine **Minor**-Versionserhöhung (neue Funktion)

## Codierungsstandards

- Ziel Python 3.10+ (3.10, 3.11, 3.12, 3.13, 3.14)
- Type Hints für alle Funktionsparameter und Rückgabewerte verwenden
- Code sauber, kompakt und lesbar halten
- Unnötige Komplexität vermeiden
- Logging anstelle von print-Anweisungen verwenden
- Formatierung wird von `ruff` gehandhabt (Linting, Formatierung und Import-Sortierung in einem Werkzeug; maximale Zeilenlänge: 120)
- Minimale, effektive Tests mit `pytest` schreiben

## Git Hooks (Lefthook)

Dieses Projekt verwendet [Lefthook](https://github.com/evilmartians/lefthook), um Codequalitätsprüfungen schnell und konsistent zu halten. Die konfigurierten Hooks spiegeln unsere vorherige Pre-Commit-Einrichtung wider:

- `ruff` - Python Linting und Formatierung (ersetzt black, isort und flake8)
- `markdownlint-cli2` - Markdown Linting
- `prettier` - Dateiformatierung (markdown, yaml, json)
- `check-upstream` - Benutzerdefinierter Hook zur Prüfung auf Upstream-Änderungen

### Einrichtung

**Empfohlener Ansatz:**

```bash
make dev
```

**Manuelle Einrichtung (wenn Sie Schritt-für-Schritt bevorzugen):**

1. Lefthook installieren (wählen Sie die Option, die Ihrer Einrichtung entspricht):

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # oder
   cargo install lefthook         # Rust toolchain
   # oder
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. Die git-Hooks installieren:

   ```sh
   lefthook install
   ```

3. (Optional) Gegen alle Dateien ausführen:

   ```sh
   lefthook run pre-commit --all
   ```

Die Hooks werden jetzt automatisch bei jedem Commit ausgeführt. Wenn Prüfungen fehlschlagen, müssen Sie die Probleme beheben, bevor Sie committen.

### Git Hooks überspringen

Wenn Sie die Lefthook-Prüfungen vorübergehend überspringen müssen, verwenden Sie das `--no-verify`-Flag:

```sh
git commit --no-verify "Ihre Commit-Nachricht"
```

Hinweis: Dies sollte nur verwendet werden, wenn es absolut notwendig ist, da es wichtige Codequalitätsprüfungen umgeht.

## Testrichtlinien

Das Projekt verwendet pytest für Tests. Beim Hinzufügen neuer Funktionen oder Beheben von Fehlern schließen Sie bitte Tests ein, die Ihre Änderungen abdecken.

Beachten Sie, dass das `scripts/`-Verzeichnis Testskripte für Funktionalität enthält, die nicht leicht mit pytest getestet werden kann. Fühlen Sie sich frei, Skripte hier hinzuzufügen zum Testen komplexer Szenarien oder Integrationstests, die schwer mit dem Standard-pytest-Framework zu implementieren wären.

### Tests ausführen

```sh
# Standardtests ausführen (schließt Integrationstests mit echten API-Aufrufen aus)
make test

# Nur Anbieter-Integrationstests ausführen (benötigt API-Schlüssel)
make test-integration

# Alle Tests einschließlich Anbieter-Integrationstests ausführen
make test-all

# Tests mit Coverage ausführen
make test-cov

# Spezielle Testdatei ausführen
uv run -- pytest tests/test_prompt.py

# Speziellen Test ausführen
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### Anbieter-Integrationstests

Anbieter-Integrationstests machen echte API-Aufrufe, um zu überprüfen, dass Anbieter-Implementierungen korrekt mit tatsächlichen APIs funktionieren. Diese Tests sind mit `@pytest.mark.integration` markiert und werden standardmäßig übersprungen, um:

- API-Credits während der regulären Entwicklung zu vermeiden
- Testfehlschläge zu verhindern, wenn API-Schlüssel nicht konfiguriert sind
- Testausführung für schnelle Iteration zu beschleunigen

Um Anbieter-Integrationstests auszuführen:

1. **API-Schlüssel einrichten** für die Anbieter, die Sie testen möchten:

   ```sh
   export ANTHROPIC_API_KEY="Ihr-Schlüssel"
   export CEREBRAS_API_KEY="Ihr-Schlüssel"
   export GEMINI_API_KEY="Ihr-Schlüssel"
   export GROQ_API_KEY="Ihr-Schlüssel"
   export OPENAI_API_KEY="Ihr-Schlüssel"
   export OPENROUTER_API_KEY="Ihr-Schlüssel"
   export STREAMLAKE_API_KEY="Ihr-Schlüssel"
   export ZAI_API_KEY="Ihr-Schlüssel"
   # LM Studio und Ollama erfordern eine lokale laufende Instanz
   # API-Schlüssel für LM Studio und Ollama sind optional, es sei denn, Ihre Durchsetzung erzwingt Authentifizierung
   ```

2. **Anbieter-Tests ausführen**:

   ```sh
   make test-integration
   ```

Tests überspringen Anbieter, bei denen API-Schlüssel nicht konfiguriert sind. Diese Tests helfen, API-Änderungen frühzeitig zu erkennen und stellen die Kompatibilität mit Anbieter-APIs sicher.

## Verhaltenskodex

Seien Sie respektvoll und konstruktiv. Belästigungen oder missbräuchliches Verhalten werden nicht toleriert.

## Lizenz

Durch Ihre Mitarbeit stimmen Sie zu, dass Ihre Beiträge unter derselben Lizenz wie das Projekt lizenziert werden.

---

## Wo man Hilfe bekommt

- Zur Fehlerbehebung siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Für Nutzung und CLI-Optionen siehe [USAGE.md](USAGE.md)
- Für Lizenzdetails siehe [../../LICENSE](../../LICENSE)

Vielen Dank, dass Sie bei der Verbesserung von gac helfen!
