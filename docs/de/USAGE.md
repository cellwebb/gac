# gac Kommandozeilen-Nutzung

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Рус../](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | **Deutsch** | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

Dieses Dokument beschreibt alle verfügbaren Flags und Optionen für das `gac` CLI-Werkzeug.

## Inhaltsverzeichnis

- [gac Kommandozeilen-Nutzung](#gac-kommandozeilen-nutzung)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Grundlegende Nutzung](#grundlegende-nutzung)
  - [Kern-Workflow-Flags](#kern-workflow-flags)
  - [Nachrichten-Anpassung](#nachrichten-anpassung)
  - [Ausgabe und Ausführlichkeit](#ausgabe-und-ausführlichkeit)
  - [Hilfe und Version](#hilfe-und-version)
  - [Beispiel-Workflows](#beispiel-workflows)
  - [Erweitert](#erweitert)
    - [Skript-Integration und externe Verarbeitung](#skript-integration-und-externe-verarbeitung)
    - [Pre-commit und Lefthook Hooks überspringen](#pre-commit-und-lefthook-hooks-überspringen)
    - [Sicherheits-Scanning](#sicherheits-scanning)
  - [Konfigurationshinweise](#konfigurationshinweise)
    - [Erweiterte Konfigurationsoptionen](#erweiterte-konfigurationsoptionen)
    - [Konfigurations-Unterbefehle](#konfigurations-unterbefehle)
  - [Interaktiver Modus](#interaktiver-modus)
    - [Wie es funktioniert](#wie-es-funktioniert)
    - [Wann man den interaktiven Modus verwenden sollte](#wann-man-den-interaktiven-modus-verwenden-sollte)
    - [Nutzungsbeispiele](#nutzungsbeispiele)
    - [Frage-Antwort-Workflow](#frage-antwort-workflow)
    - [Kombination mit anderen Flags](#kombination-mit-anderen-flags)
    - [Bewährte Praktiken](#bewährte-praktiken)
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

## Kern-Workflow-Flags

| Flag / Option        | Kurz | Beschreibung                                                           |
| -------------------- | ---- | ---------------------------------------------------------------------- |
| `--add-all`          | `-a` | Alle Änderungen vor dem Committen stagen                               |
| `--group`            | `-g` | Gestagete Änderungen in mehrere logische Commits gruppieren            |
| `--push`             | `-p` | Änderungen nach dem Committen auf das Remote pushen                    |
| `--yes`              | `-y` | Automatisch den Commit bestätigen ohne Aufforderung                    |
| `--dry-run`          |      | Zeigen, was passieren würde, ohne Änderungen vorzunehmen               |
| `--message-only`     |      | Nur die generierte Commit-Nachricht ohne eigentlichen Commit ausgeben  |
| `--no-verify`        |      | Pre-commit und lefthook Hooks beim Committen überspringen              |
| `--skip-secret-scan` |      | Sicherheits-Scan für Geheimnisse in gestageten Änderungen überspringen |
| `--interactive`      | `-i` | Fragen zu Änderungen stellen für bessere Commits                       |

**Hinweis:** Kombinieren Sie `-a` und `-g` (d.h. `-ag`) um ALLE Änderungen zuerst zu staggen, dann sie in Commits zu gruppieren.

**Hinweis:** Bei Verwendung von `--group` wird das maximale Ausgabe-Token-Limit automatisch basierend auf der Anzahl der Dateien, die committet werden, skaliert (2x für 1-9 Dateien, 3x für 10-19 Dateien, 4x für 20-29 Dateien, 5x für 30+ Dateien). Dies stellt sicher, dass die KI genügend Tokens hat, um alle gruppierten Commits ohne Abschneidung zu generieren, selbst bei großen Änderungssätzen.

**Hinweis:** `--message-only` und `--group` schließen sich gegenseitig aus. Verwenden Sie `--message-only`, wenn Sie die Commit-Nachricht für externe Verarbeitung benötigen, und `--group`, wenn Sie mehrere Commits im aktuellen Git-Workflow organisieren möchten.

**Hinweis:** Das `--interactive`-Flag liefert zusätzlichen Kontext an die KI, indem es Fragen zu Ihren Änderungen stellt, was zu genaueren und detaillierteren Commit-Nachrichten führt. Dies ist besonders nützlich für komplexe Änderungen oder wenn Sie sicherstellen möchten, dass die Commit-Nachricht den vollen Kontext Ihrer Arbeit erfasst.

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
  gac -m anthropic:claude-haiku-4-5
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

- **Nur die Commit-Nachricht erhalten (für Skript-Integration):**

  ```sh
  gac --message-only
  # Ausgabe: feat: add user authentication system
  ```

- **Commit-Nachricht im Einzeilenformat erhalten:**

  ```sh
  gac --message-only --one-liner
  # Ausgabe: feat: add user authentication system
  ```

- **Interaktiven Modus für Kontext verwenden:**

  ```sh
  gac -i
  # Was ist das Hauptziel dieser Änderungen?
  # Welches Problem lösen Sie?
  # Gibt es Implementierungsdetails, die erwähnt werden sollten?
  ```

- **Interaktiver Modus mit detaillierter Ausgabe:**

  ```sh
  gac -i -v
  # Fragen stellen und detaillierte Commit-Nachrichten generieren
  ```

## Erweitert

- Kombinieren Sie Flags für leistungsfähigere Workflows (z.B. `gac -ayp` zum stagen, automatischen Bestätigen und pushen)
- Verwenden Sie `--show-prompt` zum Debuggen oder Überprüfen des an die KI gesendeten Prompts
- Passen Sie die Ausführlichkeit mit `--log-level` oder `--quiet` an
- Verwenden Sie `--message-only` für Skript-Integration und automatisierte Workflows

### Skript-Integration und externe Verarbeitung

Das Flag `--message-only` ist für Skript-Integration und externe Tool-Workflows gedacht. Es gibt nur die rohe Commit-Nachricht ohne zusätzliche Formatierung, Spinner oder UI-Elemente aus.

**Anwendungsfälle:**

- **Agent-Integration:** KI-Agenten können Commit-Nachrichten abrufen und Commits selbst ausführen
- **Alternative VCS:** Generierte Nachrichten mit anderen Versionskontrollsystemen verwenden (Mercurial, Jujutsu usw.)
- **Benutzerdefinierte Commit-Workflows:** Nachricht vor dem Commit weiterverarbeiten oder anpassen
- **CI/CD-Pipelines:** Commit-Nachrichten für automatisierte Prozesse extrahieren

**Beispiel-Skriptverwendung:**

```sh
#!/bin/bash
# Commit-Nachricht abrufen und mit benutzerdefinierter Commit-Funktion verwenden
MESSAGE=$(gac --message-only --add-all --yes)
git commit -m "$MESSAGE"
```

```python
# Python-Integrationsbeispiel
import subprocess


def get_commit_message() -> str:
    result = subprocess.run(
        ["gac", "--message-only", "--yes"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


message = get_commit_message()
print(f"Generated message: {message}")
```

**Wichtige Eigenschaften für Skripte:**

- Saubere Ausgabe ohne Rich-Formatierung oder Spinner
- Umgeht Bestätigungs-Prompts automatisch
- Es wird kein tatsächlicher Git-Commit ausgeführt
- Funktioniert mit `--one-liner` für vereinfachte Ausgabe
- Kann mit anderen Flags wie `--hint`, `--model` usw. kombiniert werden

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
- **Claude Code verwenden?** Siehe die [Claude Code-Einrichtungsanleitung](CLAUDE_CODE.md) für OAuth-Authentifizierungsanweisungen.
- **Qwen.ai verwenden?** Siehe den [Qwen.ai-Einrichtungsleitfaden](QWEN.md) für OAuth-Authentifizierungsanweisungen.
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
- `GAC_NO_TIKTOKEN=true` - Vollständig offline bleiben, indem der `tiktoken` Download-Schritt umgangen und der eingebaute grobe Token-Schätzer verwendet wird

Siehe `.gac.env.example` für eine vollständige Konfigurationsvorlage.

Für detaillierte Anleitung zum Erstellen benutzerdefinierter System-Prompts siehe [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md).

### Konfigurations-Unterbefehle

Die folgenden Unterbefehle sind verfügbar:

- `gac init` — Interaktiver Einrichtungs-Assistent für Anbieter, Modell und Sprachkonfiguration
- `gac model` — Anbieter/Modell/API-Schlüssel-Einrichtung ohne Sprachaufforderungen (ideal für schnelle Wechsel)
- `gac auth` — Zeige OAuth-Authentifizierungsstatus für alle Anbieter an
- `gac auth claude-code login` — Anmelden zu Claude Code mit OAuth (öffnet Browser)
- `gac auth claude-code logout` — Abmelden von Claude Code und gespeichertes Token entfernen
- `gac auth claude-code status` — Claude Code-Authentifizierungsstatus prüfen
- `gac auth qwen login` — Anmelden zu Qwen mit OAuth-Gerätefluss (öffnet Browser)
- `gac auth qwen logout` — Abmelden von Qwen und gespeichertes Token entfernen
- `gac auth qwen status` — Qwen-Authentifizierungsstatus prüfen
- `gac config show` — Aktuelle Konfiguration anzeigen
- `gac config set KEY VALUE` — Konfigurationsschlüssel in `$HOME/.gac.env` setzen
- `gac config get KEY` — Konfigurationswert abrufen
- `gac config unset KEY` — Konfigurationsschlüssel aus `$HOME/.gac.env` entfernen
- `gac language` (oder `gac lang`) — Interaktiver Sprachselektor für Commit-Nachrichten (setzt GAC_LANGUAGE)
- `gac diff` — Gefiltertes git diff mit Optionen für gestufte/ungestufte Änderungen, Farbe und Kürzung anzeigen

## Interaktiver Modus

Das `--interactive` (`-i`) Flag verbessert die Commit-Nachrichtengenerierung von gac, indem es gezielte Fragen zu Ihren Änderungen stellt. Dieser zusätzliche Kontext hilft der KI, genauere, detailliertere und kontextbezogene Commit-Nachrichten zu erstellen.

### Wie es funktioniert

Wenn Sie `--interactive` verwenden, stellt gac Fragen wie:

- **Was ist das Hauptziel dieser Änderungen?** - Hilft, das übergeordnete Ziel zu verstehen
- **Welches Problem lösen Sie?** - Liefert Kontext über die Motivation
- **Gibt es Implementierungsdetails, die erwähnt werden sollten?** - Erfasst technische Spezifikationen
- **Gibt es Breaking Changes?** - Identifiziert potenzielle Auswirkungsprobleme
- **Ist dies mit einem Issue oder Ticket verbunden?** - Verbindet mit dem Projektmanagement

### Wann man den interaktiven Modus verwenden sollte

Der interaktive Modus ist besonders nützlich für:

- **Komplexe Änderungen**, bei denen der Kontext nicht allein aus dem diff ersichtlich ist
- **Refactoring-Arbeiten**, die sich über mehrere Dateien und Konzepte erstrecken
- **Neue Funktionen**, die eine Erklärung des übergeordneten Zwecks erfordern
- **Bug-Fixes**, bei denen die Ursache nicht sofort sichtbar ist
- **Performance-Optimierungen**, bei denen die Logik nicht offensichtlich ist
- **Code Review-Vorbereitung** - Fragen helfen Ihnen, über Ihre Änderungen nachzudenken

### Nutzungsbeispiele

**Grundlegender interaktiver Modus:**

```sh
gac -i
```

Dies wird:

1. Eine Zusammenfassung der gestageten Änderungen anzeigen
2. Fragen zu den Änderungen stellen
3. Eine Commit-Nachricht mit Ihren Antworten generieren
4. Um Bestätigung bitten (oder automatisch bestätigen, wenn mit `-y` kombiniert)

**Interaktiver Modus mit gestageten Änderungen:**

```sh
gac -ai
# Alle Änderungen stagen, dann Fragen für besseren Kontext stellen
```

**Interaktiver Modus mit spezifischen Hinweisen:**

```sh
gac -i -h "Datenbankmigration für Benutzerprofile"
# Fragen stellen, während ein spezifischer Hinweis zur Fokussierung der KI bereitgestellt wird
```

**Interaktiver Modus mit detaillierter Ausgabe:**

```sh
gac -i -v
# Fragen stellen und eine detaillierte, strukturierte Commit-Nachricht generieren
```

**Automatisch bestätigter interaktiver Modus:**

```sh
gac -i -y
# Fragen stellen, aber den resultierenden Commit automatisch bestätigen
```

### Frage-Antwort-Workflow

Der interaktive Workflow folgt diesem Muster:

1. **Änderungsüberprüfung** - gac zeigt eine Zusammenfassung dessen, was Sie committen
2. **Auf Fragen antworten** - Beantworten Sie jede Aufforderung mit relevanten Details
3. **Kontextverbesserung** - Ihre Antworten werden zum KI-Prompt hinzugefügt
4. **Nachrichtengenerierung** - Die KI erstellt eine Commit-Nachricht mit vollem Kontext
5. **Bestätigung** - Überprüfen und bestätigen Sie den Commit (oder automatisch mit `-y`)

**Tipps für nützliche Antworten:**

- **Kurz aber vollständig** - Wichtige Details liefern, ohne übermäßig ausführlich zu sein
- **Auf "warum" konzentrieren** - Die Begründung hinter Ihren Änderungen erklären
- **Einschränkungen erwähnen** - Einschränkungen oder besondere Überlegungen notieren
- **Mit externem Kontext verlinken** - Auf Issues, Dokumentation oder Designdokumente verweisen
- **Leere Antworten sind in Ordnung** - Wenn eine Frage nicht zutrifft, einfach Enter drücken

### Kombination mit anderen Flags

Der interaktive Modus funktioniert gut mit den meisten anderen Flags:

```sh
# Alle Änderungen stagen und Fragen stellen
gac -ai

# Fragen mit detaillierter Ausgabe stellen
gac -i -v
```

### Bewährte Praktiken

- **Für komplexe PRs verwenden** - Besonders nützlich für Pull Requests, die detaillierte Erklärungen benötigen
- **Team-Zusammenarbeit** - Fragen helfen Ihnen, über Änderungen nachzudenken, die andere überprüfen werden
- **Dokumentationsvorbereitung** - Ihre Antworten können die Grundlage für Release Notes bilden
- **Lernwerkzeug** - Fragen stärken gute Praktiken für Commit-Nachrichten
- **Bei einfachen Änderungen überspringen** - Für trivial Fixes kann der grundlegende Modus schneller sein

## Hilfe erhalten

- Für benutzerdefinierte System-Prompts siehe [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- Zur Fehlerbehebung und erweiterten Tipps siehe [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Für Installation und Konfiguration siehe [README.md#installation-and-configuration](README.md#installation-and-configuration)
- Zum Mitwirken siehe [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Lizenzinformationen: [LICENSE](LICENSE)
