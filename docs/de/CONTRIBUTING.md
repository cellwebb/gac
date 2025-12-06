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
