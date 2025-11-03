# gac Kommandozeilen-Nutzung

**English** | [简体中文](USAGE.zh-CN.md) | [繁體中文](USAGE.zh-TW.md) | [日本語](USAGE.ja.md) | [Français](USAGE.fr.md) | [Русский](USAGE.ru.md) | [Español](USAGE.es.md) | [Português](USAGE.pt.md) | [हिन्दी](USAGE.hi.md)

Dieses Dokument beschreibt alle verfügbaren Flags und Optionen für das `gac` CLI-Werkzeug.

## Inhaltsverzeichnis

- [gac Kommandozeilen-Nutzung](#gac-kommandozeilen-nutzung)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Grundlegende Nutzung](#grundlegende-nutzung)
  - [Core Workflow Flags](#core-workflow-flags)
  - [Nachrichten-Anpassung](#nachrichten-anpassung)
  - [Ausgabe und Ausführlichkeit](#ausgabe-und-ausführlichkeit)
  - [Hilfe und Version](#hilfe-und-version)
  - [Beispiel-Workflows](#beispiel-workflows)
  - [Erweitert](#erweitert)
    - [Pre-commit und Lefthook Hooks überspringen](#pre-commit-und-lefthook-hooks-überspringen)
  - [Konfigurationshinweise](#konfigurationshinweise)
    - [Erweiterte Konfigurationsoptionen](#erweiterte-konfigurationsoptionen)
    - [Konfigurations-Unterbefehle](#konfigurations-unterbefehle)
  - [Hilfe erhalten](#hilfe-erhalten)

## Grundlegende Nutzung

```sh
gac init
# Dann folgen Sie den Aufforderungen, um Ihren Anbieter, Ihr Modell und Ihre API-Schlüssel interaktiv zu konfigurieren
gac
```

Generiert eine KI-gestützte Commit-Nachricht für gestagete Änderungen und fordert zur Bestätigung auf. Der Bestätigungs-Prompt akzeptiert:

- `y` oder `yes` - Mit dem Commit fortfahren
- `n` oder `no` - Den Commit abbrechen
- `r` oder `reroll` - Die Commit-Nachricht mit demselben Kontext neu generieren
- `e` oder `edit` - Die Commit-Nachricht direkt bearbeiten mit rich Terminal-Bearbeitung (vi/emacs Keybindings)
- Jeder andere Text - Neu generieren mit diesem Text als Feedback (z.B. `make it shorter`, `focus on performance`)
- Leere Eingabe (nur Enter) - Den Prompt erneut anzeigen

---

## Core Workflow Flags

| Flag / Option        | Kurz | Beschreibung                                                           |
| -------------------- | ---- | ---------------------------------------------------------------------- |
| `--add-all`          | `-a` | Alle Änderungen vor dem Committen stagen                               |
| `--group`            | `-g` | Gestagete Änderungen in mehrere logische Commits gruppieren            |
| `--push`             | `-p` | Änderungen nach dem Committen auf das Remote pushen                    |
| `--yes`              | `-y` | Automatisch den Commit bestätigen ohne Aufforderung                    |
| `--dry-run`          |      | Zeigen, was passieren würde, ohne Änderungen vorzunehmen               |
| `--no-verify`        |      | Pre-commit und lefthook Hooks beim Committen überspringen              |
| `--skip-secret-scan` |      | Sicherheits-Scan für Geheimnisse in gestageten Änderungen überspringen |

**Hinweis:** Kombinieren Sie `-a` und `-g` (d.h. `-ag`) um ALLE Änderungen zuerst zu staggen, dann sie in Commits zu gruppieren.

**Hinweis:** Bei Verwendung von `--group` wird das maximale Ausgabe-Token-Limit automatisch basierend auf der Anzahl der Dateien, die committet werden, skaliert (2x für 1-9 Dateien, 3x für 10-19 Dateien, 4x für 20-29 Dateien, 5x für 30+ Dateien). Dies stellt sicher, dass die KI genügend Tokens hat, um alle gruppierten Commits ohne Abschneidung zu generieren, selbst bei großen Änderungssätzen.

## Nachrichten-Anpassung

| Flag / Option       | Kurz | Beschreibung                                                                          |
| ------------------- | ---- | ------------------------------------------------------------------------------------- |
| `--one-liner`       | `-o` | Eine einzeilige Commit-Nachricht generieren                                           |
| `--verbose`         | `-v` | Detaillierte Commit-Nachrichten mit Motivation, Architektur & Auswirkungen generieren |
| `--hint <text>`     | `-h` | Einen Hinweis hinzufügen, um die KI zu leiten                                         |
| `--model <model>`   | `-m` | Das zu verwendende Modell für diesen Commit angeben                                   |
| `--language <lang>` | `-l` | Sprache überschreiben (Name oder Code: 'Spanish', 'es', 'zh-CN', 'ja')                |
| `--scope`           | `-s` | Einen geeigneten Scope für den Commit herleiten                                       |

**Hinweis:** Sie können Feedback interaktiv geben, indem Sie es einfach am Bestätigungs-Prompt eingeben - kein Präfix mit 'r' erforderlich. Geben Sie `r` für ein einfaches Reroll, `e` zum direkten Bearbeiten mit vi/emacs Keybindings, oder geben Sie Ihr Feedback direkt ein wie `make it shorter`.

## Ausgabe und Ausführlichkeit

| Flag / Option         | Kurz | Beschreibung                                                 |
| --------------------- | ---- | ------------------------------------------------------------ |
| `--quiet`             | `-q` | Alle außer Fehlern unterdrücken                              |
| `--log-level <level>` |      | Log-Level setzen (debug, info, warning, error)               |
| `--show-prompt`       |      | Den KI-Prompt für die Commit-Nachrichtengenerierung ausgeben |

## Hilfe und Version

| Flag / Option | Kurz | Beschreibung                         |
| ------------- | ---- | ------------------------------------ |
| `--version`   |      | gac-Version anzeigen und beenden     |
| `--help`      |      | Hilfe-Nachricht anzeigen und beenden |

---

## Beispiel-Workflows

- **Alle Änderungen stagen und committen:**

  ```sh
  gac -a
  ```

- **Committen und pushen in einem Schritt:**

  ```sh
  gac -ap
  ```

- **Eine einzeilige Commit-Nachricht generieren:**

  ```sh
  gac -o
  ```

- **Eine detaillierte Commit-Nachricht mit strukturierten Abschnitten generieren:**

  ```sh
  gac -v
  ```

- **Einen Hinweis für die KI hinzufügen:**

  ```sh
  gac -h "Refactor authentication logic"
  ```

- **Scope für den Commit herleiten:**

  ```sh
  gac -s
  ```

- **Gestagete Änderungen in logische Commits gruppieren:**

  ```sh
  gac -g
  # Gruppiert nur die Dateien, die Sie bereits gestagt haben
  ```

- **Alle Änderungen gruppieren (gestagt + ungestagt) und automatisch bestätigen:**

  ```sh
  gac -agy
  # Staged alles, gruppiert es und bestätigt automatisch
  ```

- **Ein bestimmtes Modell nur für diesen Commit verwenden:**

  ```sh
  gac -m anthropic:claude-3-5-haiku-latest
  ```

- **Commit-Nachricht in einer bestimmten Sprache generieren:**

  ```sh
  # Sprachcodes verwenden (kürzer)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # Vollständige Namen verwenden
  gac -l "Simplified Chinese"
  gac -l Japanese
  gac -l Spanish
  ```

- **Trockenlauf (sehen, was passieren würde):**

  ```sh
  gac --dry-run
  ```

## Erweitert

- Kombinieren Sie Flags für leistungsfähigere Workflows (z.B. `gac -ayp` zum stagen, automatischen Bestätigen und pushen)
- Verwenden Sie `--show-prompt` zum Debuggen oder Überprüfen des an die KI gesendeten Prompts
- Passen Sie die Ausführlichkeit mit `--log-level` oder `--quiet` an

### Pre-commit und Lefthook Hooks überspringen

Das `--no-verify`-Flag ermöglicht es Ihnen, alle in Ihrem Projekt konfigurierten pre-commit oder lefthook Hooks zu überspringen:

```sh
gac --no-verify  # Alle pre-commit und lefthook Hooks überspringen
```

**Verwenden Sie `--no-verify`, wenn:**

- Pre-commit oder lefthook Hooks vorübergehend fehlschlagen
- Bei zeitintensiven Hooks arbeiten
- Bei Arbeit in Bearbeitung befindlichem Code, der noch nicht allen Prüfungen standhält

**Hinweis:** Verwenden Sie mit Vorsicht, da diese Hooks Codequalitätsstandards aufrechterhalten.

### Sicherheits-Scanning

gac enthält integriertes Sicherheits-Scanning, das automatisch potenzielle Geheimnisse und API-Schlüssel in Ihren gestageten Änderungen vor dem Committen erkennt. Dies hilft, versehentliches Committen sensibler Informationen zu verhindern.

**Sicherheits-Scans überspringen:**

```sh
gac --skip-secret-scan  # Sicherheits-Scan für diesen Commit überspringen
```

**Permanent deaktivieren:** Setzen Sie `GAC_SKIP_SECRET_SCAN=true` in Ihrer `.gac.env`-Datei.

**Wann überspringen:**

- Committen von Beispielcode mit Platzhalter-Schlüsseln
- Arbeiten mit Test-Fixtures, die Dummy-Anmeldeinformationen enthalten
- Wenn Sie überprüft haben, dass die Änderungen sicher sind

**Hinweis:** Der Scanner verwendet Pattern-Matching, um gängige Geheimnisformate zu erkennen. Überprüfen Sie immer Ihre gestageten Änderungen vor dem Committen.

## Konfigurationshinweise

- Die empfohlene Methode zur Einrichtung von gac ist, `gac init` auszuführen und den interaktiven Aufforderungen zu folgen.
- Bereits konfigurierte Sprache und nur Anbieter oder Modelle wechseln müssen? Führen Sie `gac model` aus, um die Einrichtung ohne Sprachfragen zu wiederholen.
- gac lädt Konfiguration in der folgenden Rangfolge:
  1. CLI-Flags
  2. Umgebungsvariablen
  3. Projekt-weites `.gac.env`
  4. Benutzer-weites `~/.gac.env`

### Erweiterte Konfigurationsoptionen

Sie können das Verhalten von gac mit diesen optionalen Umgebungsvariablen anpassen:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Automatisch Scope herleiten und in Commit-Nachrichten einbeziehen (z.B. `feat(auth):` vs `feat:`)
- `GAC_VERBOSE=true` - Detaillierte Commit-Nachrichten mit Motivation, Architektur und Auswirkungs-Abschnitten generieren
- `GAC_TEMPERATURE=0.7` - KI-Kreativität steuern (0.0-1.0, niedriger = fokussierter)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Maximale Tokens für generierte Nachrichten (automatisch 2-5x skaliert bei Verwendung von `--group` basierend auf Dateianzahl; überschreiben, um höher oder niedriger zu gehen)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Warnen, wenn Prompts diese Token-Anzahl überschreiten
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Einen benutzerdefinierten System-Prompt für die Commit-Nachrichtengenerierung verwenden
- `GAC_LANGUAGE=Spanish` - Commit-Nachrichten in einer bestimmten Sprache generieren (z.B. Spanish, French, Japanese, German). Unterstützt vollständige Namen oder ISO-Codes (es, fr, ja, de, zh-CN). Verwenden Sie `gac language` für interaktive Auswahl
- `GAC_TRANSLATE_PREFIXES=true` - Konventionelle Commit-Präfixe (feat, fix, etc.) in die Zielsprache übersetzen (Standard: false, behält Präfixe in Englisch)
- `GAC_SKIP_SECRET_SCAN=true` - Automatisches Sicherheits-Scanning für Geheimnisse in gestageten Änderungen deaktivieren (mit Vorsicht verwenden)

Siehe `.gac.env.example` für eine vollständige Konfigurationsvorlage.

Für detaillierte Anleitung zum Erstellen benutzerdefinierter System-Prompts siehe [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md).

### Konfigurations-Unterbefehle

Die folgenden Unterbefehle sind verfügbar:

- `gac init` — Interaktiver Einrichtungs-Assistent für Anbieter, Modell und Sprachkonfiguration
- `gac model` — Anbieter/Modell/API-Schlüssel-Einrichtung ohne Sprachaufforderungen (ideal für schnelle Wechsel)
- `gac config show` — Aktuelle Konfiguration anzeigen
- `gac config set KEY VALUE` — Einen Konfigurationsschlüssel in `$HOME/.gac.env` setzen
- `gac config get KEY` — Einen Konfigurationswert erhalten
- `gac config unset KEY` — Einen Konfigurationsschlüssel aus `$HOME/.gac.env` entfernen
- `gac language` (oder `gac lang`) — Interaktiver Sprachwähler für Commit-Nachrichten (setzt GAC_LANGUAGE)
- `gac diff` — Gefilterten git diff mit Optionen für gestagete/unstagte Änderungen, Farbe und Kürzung anzeigen

## Hilfe erhalten

- Für benutzerdefinierte System-Prompts siehe [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- Zur Fehlerbehebung und erweiterten Tipps siehe [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Für Installation und Konfiguration siehe [README.md#installation-and-configuration](README.md#installation-and-configuration)
- Zum Mitwirken siehe [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Lizenzinformationen: [LICENSE](LICENSE)
