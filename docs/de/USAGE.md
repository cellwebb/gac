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
    - [SSL-Zertifikatüberprüfung](#ssl-zertifikatüberprüfung)
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
  - [Nutzungsstatistiken](#nutzungsstatistiken)
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
- `e` oder `edit` - Die Commit-Nachricht bearbeiten. Standardmäßig wird eine In-Place-TUI mit vi/emacs-Keybindings geöffnet. Setzen Sie `GAC_EDITOR`, um stattdessen Ihren bevorzugten Editor zu öffnen (z.B. `GAC_EDITOR=code gac` für VS Code, `GAC_EDITOR=vim gac` für vim)
- Jeder andere Text - Neu generieren mit diesem Text als Feedback (z.B. `make it shorter`, `focus on performance`)
- Leere Eingabe (nur Enter) - Den Prompt erneut anzeigen

---

## Kern-Workflow-Flags

| Flag / Option        | Kurz | Beschreibung                                                             |
| -------------------- | ---- | ------------------------------------------------------------------------ |
| `--add-all`          | `-a` | Alle Änderungen vor dem Committen stagen                                 |
| `--stage`            | `-S` | Dateien interaktiv mit baumbasierter TUI zum Staging auswählen           |
| `--group`            | `-g` | Gestagete Änderungen in mehrere logische Commits gruppieren              |
| `--push`             | `-p` | Änderungen nach dem Committen auf das Remote pushen                      |
| `--yes`              | `-y` | Automatisch den Commit bestätigen ohne Aufforderung                      |
| `--dry-run`          |      | Zeigen, was passieren würde, ohne Änderungen vorzunehmen                 |
| `--message-only`     |      | Nur die generierte Commit-Nachricht ohne eigentlichen Commit ausgeben    |
| `--no-verify`        |      | Pre-commit und lefthook Hooks beim Committen überspringen                |
| `--skip-secret-scan` |      | Sicherheits-Scan für Geheimnisse in gestageten Änderungen überspringen   |
| `--no-verify-ssl`    |      | SSL-Zertifikatüberprüfung überspringen (nützlich für Unternehmensproxys) |
| `--signoff`          |      | Signed-off-by Zeile zur Commit-Nachricht hinzufügen (DCO-Konformität)    |
| `--interactive`      | `-i` | Fragen zu Änderungen stellen für bessere Commits                         |

**Hinweis:** `--stage` und `--add-all` schließen sich gegenseitig aus. Verwenden Sie `--stage`, um interaktiv Dateien zum Staging auszuwählen, und `--add-all`, um alle Änderungen auf einmal zu stagen.

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
| `--50-72`           |      | Die 50/72-Regel für Commit-Nachrichten-Formatierung erzwingen                         |

**Hinweis:** Das `--50-72` Flag erzwingt die [50/72-Regel](https://www.conventionalcommits.org/en/v1.0.0/#summary), wobei:

- Betreffzeile: maximal 50 Zeichen
- Body-Zeilen: maximal 72 Zeichen pro Zeile
- Dies hält Commit-Nachrichten in `git log --oneline` und GitHub's UI lesbar

Sie können auch `GAC_USE_50_72_RULE=true` in Ihrer `.gac.env` Datei setzen, um diese Regel immer anzuwenden.

**Hinweis:** Sie können Feedback interaktiv geben, indem Sie es einfach am Bestätigungs-Prompt eingeben - kein Präfix mit 'r' erforderlich. Geben Sie `r` für ein einfaches Reroll, `e` zum Bearbeiten der Nachricht (standardmäßig In-Place-TUI, oder `$GAC_EDITOR` falls gesetzt), oder geben Sie Ihr Feedback direkt ein wie `make it shorter`.

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

### SSL-Zertifikatüberprüfung

Das `--no-verify-ssl`-Flag ermöglicht es Ihnen, die SSL-Zertifikatüberprüfung für API-Aufrufe zu überspringen:

```sh
gac --no-verify-ssl  # SSL-Überprüfung für diesen Commit überspringen
```

**Um permanent einzustellen:** Setzen Sie `GAC_NO_VERIFY_SSL=true` in Ihrer `.gac.env`-Datei.

**Verwenden Sie `--no-verify-ssl` wenn:**

- Unternehmensproxys SSL-Verkehr abfangen (MITM-Proxys)
- Entwicklungsumgebungen selbstsignierte Zertifikate verwenden
- Sie SSL-Zertifikatfehler aufgrund von Netzwerk-Sicherheitseinstellungen erhalten

**Hinweis:** Verwenden Sie diese Option nur in vertrauenswürdigen Netzwerkumgebungen. Das Deaktivieren der SSL-Überprüfung verringert die Sicherheit und kann Ihre API-Anfragen anfällig für Man-in-the-Middle-Angriffe machen.

### Signed-off-by Zeile (DCO-Konformität)

gac unterstützt das Hinzufügen einer `Signed-off-by`-Zeile zu Commit-Nachrichten, was für die [Developer Certificate of Origin (DCO)](https://developercertificate.org/)-Konformität in vielen Open-Source-Projekten erforderlich ist.

**Signoff hinzufügen:**

```sh
gac --signoff  # Signed-off-by Zeile zum Commit hinzufügen
```

**Dauerhaft aktivieren:** Setzen Sie `GAC_SIGNOFF=true` in Ihrer `.gac.env`-Datei oder fügen Sie `signoff=true` zu Ihrer Konfiguration hinzu.

**Was es macht:**

- Fügt `Signed-off-by: Ihr Name <ihre.email@beispiel.com>` zur Commit-Nachricht hinzu
- Verwendet Ihre Git-Konfiguration (`user.name` und `user.email`) für die Zeile
- Erforderlich für Projekte wie Cherry Studio, Linux-Kernel und andere mit DCO

**Git-Identität einrichten:**

Stellen Sie sicher, dass Ihre Git-Konfiguration den richtigen Namen und die richtige E-Mail hat:

```sh
git config --global user.name "Ihr Vollständiger Name"
git config --global user.email "ihre.email@beispiel.com"
```

**Hinweis:** Die Signed-off-by-Zeile wird von Git während des Commits hinzugefügt, nicht von der KI während der Nachrichtengenerierung. Sie sehen sie nicht in der Vorschau, aber sie wird im endgültigen Commit sein (prüfen Sie mit `git log -1`).

## Konfigurationshinweise

- Die empfohlene Methode zur Einrichtung von gac ist, `gac init` auszuführen und den interaktiven Aufforderungen zu folgen.
- Bereits konfigurierte Sprache und nur Anbieter oder Modelle wechseln müssen? Führen Sie `gac model` aus, um die Einrichtung ohne Sprachfragen zu wiederholen.
- **Claude Code verwenden?** Siehe die [Claude Code-Einrichtungsanleitung](CLAUDE_CODE.md) für OAuth-Authentifizierungsanweisungen.
- **ChatGPT OAuth verwenden?** Siehe die [ChatGPT OAuth-Einrichtungsanleitung](CHATGPT_OAUTH.md) für browserbasierte Authentifizierungsanweisungen.
- **GitHub Copilot verwenden?** Siehe die [GitHub Copilot-Einrichtungsanleitung](GITHUB_COPILOT.md) für Device-Flow-Authentifizierungsanweisungen.
- gac lädt Konfiguration in der folgenden Rangfolge:
  1. CLI-Flags
  2. Umgebungsvariablen
  3. Projekt-weites `.gac.env`
  4. Benutzer-weites `~/.gac.env`

### Erweiterte Konfigurationsoptionen

Sie können das Verhalten von gac mit diesen optionalen Umgebungsvariablen anpassen:

- `GAC_EDITOR=code --wait` - Überschreibt den Editor, der beim Drücken von `e` am Bestätigungs-Prompt verwendet wird. Standardmäßig öffnet `e` eine In-Place-TUI; durch Setzen von `GAC_EDITOR` wird auf einen externen Editor umgeschaltet. Unterstützt jeden Editorbefehl mit Argumenten. Wait-Flags (`--wait`/`-w`) werden für bekannte GUI-Editoren (VS Code, Cursor, Zed, Sublime Text) automatisch eingefügt, sodass der Prozess blockiert, bis Sie die Datei schließen
- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Automatisch Scope herleiten und in Commit-Nachrichten einbeziehen (z.B. `feat(auth):` vs `feat:)
- `GAC_VERBOSE=true` - Detaillierte Commit-Nachrichten mit Motivation, Architektur und Auswirkungs-Abschnitten generieren
- `GAC_USE_50_72_RULE=true` - Die 50/72-Regel für Commit-Nachrichten immer erzwingen (Betreff ≤50 Zeichen, Body-Zeilen ≤72 Zeichen)
- `GAC_SIGNOFF=true` - Immer Signed-off-by Zeile zu Commits hinzufügen (für DCO-Konformität)
- `GAC_TEMPERATURE=0.7` - KI-Kreativität steuern (0.0-1.0, niedriger = fokussierter)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Maximale Tokens für generierte Nachrichten (automatisch 2-5x skaliert bei Verwendung von `--group` basierend auf Dateianzahl; überschreiben, um höher oder niedriger zu gehen)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Warnen, wenn Prompts diese Token-Anzahl überschreiten
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Einen benutzerdefinierten System-Prompt für die Commit-Nachrichtengenerierung verwenden
- `GAC_LANGUAGE=Spanish` - Commit-Nachrichten in einer bestimmten Sprache generieren (z.B. Spanish, French, Japanese, German). Unterstützt vollständige Namen oder ISO-Codes (es, fr, ja, de, zh-CN). Verwenden Sie `gac language` für interaktive Auswahl
- `GAC_TRANSLATE_PREFIXES=true` - Konventionelle Commit-Präfixe (feat, fix, etc.) in die Zielsprache übersetzen (Standard: false, behält Präfixe in Englisch)
- `GAC_SKIP_SECRET_SCAN=true` - Automatisches Sicherheits-Scanning für Geheimnisse in gestageten Änderungen deaktivieren (mit Vorsicht verwenden)
- `GAC_NO_VERIFY_SSL=true` - SSL-Zertifikatüberprüfung für API-Aufrufe überspringen (nützlich für Unternehmensproxys, die SSL-Verkehr abfangen)
- `GAC_DISABLE_STATS=true` - Erfassung von Nutzungsstatistiken deaktivieren (keine Lese- oder Schreibzugriffe auf die Statistikdatei; bestehende Daten bleiben erhalten). Nur truthy-Werte deaktivieren Statistiken; die Einstellung auf `false`/`0`/`no`/`off` hält Statistiken aktiviert, genauso wie das Weglassen der Variable

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
- `gac auth chatgpt login` — Anmelden zu ChatGPT mit OAuth (öffnet Browser)
- `gac auth chatgpt logout` — Abmelden von ChatGPT und gespeichertes Token entfernen
- `gac auth chatgpt status` — ChatGPT-Authentifizierungsstatus prüfen
- `gac auth copilot login` — Login zu GitHub Copilot mit Device Flow
- `gac auth copilot login --host ghe.mycompany.com` — Login zu Copilot auf einer GitHub Enterprise-Instanz
- `gac auth copilot logout` — Von Copilot abmelden und gespeicherte Tokens entfernen
- `gac auth copilot status` — Copilot-Authentifizierungsstatus prüfen
- `gac config show` — Aktuelle Konfiguration anzeigen
- `gac config set KEY VALUE` — Konfigurationsschlüssel in `$HOME/.gac.env` setzen
- `gac config get KEY` — Konfigurationswert abrufen
- `gac config unset KEY` — Konfigurationsschlüssel aus `$HOME/.gac.env` entfernen
- `gac language` (oder `gac lang`) — Interaktiver Sprachselektor für Commit-Nachrichten (setzt GAC_LANGUAGE)
- `gac editor` (oder `gac edit`) — Interaktiver Editor-Selektor für die `e`-Taste am Bestätigungsprompt (setzt GAC_EDITOR)
- `gac diff` — Gefiltertes git diff mit Optionen für gestufte/ungestufte Änderungen, Farbe und Kürzung anzeigen
- `gac serve` — GAC als [MCP-Server](MCP.md) für KI-Agenten-Integration starten (stdio-Transport)
- `gac stats show` — Ihre gac-Nutzungsstatistiken anzeigen (Summen, Streaks, tägliche & wöchentliche Aktivität, Token-Nutzung, Top-Projekte, Top-Modelle)
- `gac stats models` — Detaillierte Statistiken für alle Modelle mit Token-Aufschlüsselung und Geschwindigkeitsvergleich
- `gac stats projects` — Statistiken für alle Projekte mit Token-Aufschlüsselung anzeigen
- `gac stats reset` — Alle Statistiken auf Null zurücksetzen (mit Bestätigungsaufforderung)
- `gac stats reset model <model-id>` — Statistiken für ein bestimmtes Modell zurücksetzen (Groß-/Kleinschreibung wird nicht berücksichtigt)

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

## Nutzungsstatistiken

gac erfasst leichtgewichtige Nutzungsstatistiken, damit Sie Ihre Commit-Aktivität, Streaks, Token-Nutzung und aktivsten Projekte und Modelle sehen können. Statistiken werden lokal in `~/.gac_stats.json` gespeichert und niemals versendet — es gibt keine Telemetrie.

**Was erfasst wird:** Gesamtzahl der gac-Ausführungen, Gesamtzahl der Commits, Gesamtzahl der Prompt- und Completion-Tokens, erste/letzte Verwendungsdaten, tägliche und wöchentliche Zähler (gacs, Commits, Tokens), aktuelle und längste Streak, Aktivitätszähler pro Projekt (gacs, Commits, Prompt + Completion-Tokens) sowie Aktivitätszähler pro Modell (gacs, Prompt + Completion-Tokens).

**Was NICHT erfasst wird:** Commit-Nachrichten, Code-Inhalte, Dateipfade, persönliche Informationen oder sonst etwas über Zähler, Daten, Projektnamen (abgeleitet vom Git-Remote/Verzeichnisnamen) und Modellnamen hinaus.

### Opt-in oder Opt-out

`gac init` fragt, ob Sie Statistiken aktivieren möchten, und erklärt genau, was gespeichert wird. Sie können Ihre Meinung jederzeit ändern:

- **Statistiken aktivieren:** `GAC_DISABLE_STATS` entfernen oder auf `false`/`0`/`no`/`off`/leer setzen.
- **Statistiken deaktivieren:** `GAC_DISABLE_STATS` auf einen truthy-Wert setzen (`true`, `1`, `yes`, `on`).

Wenn Sie Statistiken während `gac init` ablehnen und eine vorhandene `~/.gac_stats.json` erkannt wird, wird Ihnen die Möglichkeit angeboten, diese zu löschen.

### Statistik-Unterbefehle

| Befehl                             | Beschreibung                                                                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `gac stats`                        | Ihre Statistiken anzeigen (gleich wie `gac stats show`)                                                                         |
| `gac stats show`                   | Vollständige Statistiken anzeigen: Summen, Streaks, tägliche & wöchentliche Aktivität, Token-Nutzung, Top-Projekte, Top-Modelle |
| `gac stats models`                 | Detaillierte Statistiken für **alle** verwendeten Modelle mit Token-Aufschlüsselung und Geschwindigkeitsvergleich               |
| `gac stats projects`               | Statistiken für **alle** Projekte mit Token-Aufschlüsselung anzeigen                                                            |
| `gac stats reset`                  | Alle Statistiken auf Null zurücksetzen (mit Bestätigungsaufforderung)                                                           |
| `gac stats reset model <model-id>` | Statistiken für ein bestimmtes Modell zurücksetzen (Groß-/Kleinschreibung wird nicht berücksichtigt)                            |

### Beispiele

```sh
# Ihre Gesamtstatistiken anzeigen
gac stats

# Detaillierte Aufschlüsselung aller verwendeten Modelle
gac stats models

# Statistiken für alle Projekte
gac stats projects

# Alle Statistiken zurücksetzen (mit Bestätigungsaufforderung)
gac stats reset

# Statistiken für ein bestimmtes Modell zurücksetzen
gac stats reset model wafer:deepseek-v4-pro
```

### Was Sie sehen werden

Die Ausführung von `gac stats` zeigt:

- **Gesamtanzahl gacs und Commits** — wie oft Sie gac verwendet haben und wie viele Commits es erstellt hat
- **Aktuelle und längste Streak** — aufeinanderfolgende Tage mit gac-Aktivität (🔥 ab 5+ Tagen)
- **Aktivitätszusammenfassung** — heutige und diese Woche gacs, Commits und Tokens im Vergleich zu Ihrem Spitzentag und Ihrer Spitzenwoche
- **Top-Projekte** — Ihre 5 aktivsten Repos nach gac- + Commit-Anzahl, mit Token-Nutzung pro Projekt

Running `gac stats projects` zeigt **alle** Projekte (nicht nur die Top 5) mit:

- **Alle Projekte-Tabelle** — jedes Projekt sortiert nach Aktivität, mit Gac-Anzahl, Commit-Anzahl, Prompt-Token, Completion-Token, Reasoning-Token und Gesamt-Token
- **Top-Modelle** — Ihre 5 am häufigsten verwendeten Modelle mit Prompt-, Completion- und insgesamt verbrauchten Tokens

Running `gac stats models` zeigt **alle** Modelle (nicht nur die Top 5) mit:

- **Alle Modelle-Tabelle** — jedes verwendete Modell sortiert nach Aktivität, mit Gac-Anzahl, Geschwindigkeit (Tokens/Sek), Prompt-Token, Completion-Token, Reasoning-Token und Gesamt-Token
- **Geschwindigkeitsvergleich** — ein horizontales Balkendiagramm aller Modelle mit bekannten Geschwindigkeiten, sortiert von schnellstem zu langsamstem, farbcodiert nach Geschwindigkeitsperzentil (🟡 blitzschnell, 🟢 schnell, 🔵 moderat, 🔘 langsam)
- **Highscore-Feiern** — 🏆 Trophäen, wenn Sie neue tägliche, wöchentliche, Token- oder Streak-Rekorde aufstellen; 🥈 wenn Sie diese einstellen
- **Ermutigungsnachrichten** — kontextbezogene Ermutigungen basierend auf Ihrer Aktivität

### Statistiken deaktivieren

Setzen Sie die Umgebungsvariable `GAC_DISABLE_STATS` auf einen truthy-Wert:

```sh
# Statistikerfassung deaktivieren
export GAC_DISABLE_STATS=true

# Oder in .gac.env
GAC_DISABLE_STATS=true
```

Falsy-Werte (`false`, `0`, `no`, `off`, leer) halten Statistiken aktiviert — genauso wie das Weglassen der Variable.

Wenn deaktiviert, überspringt gac die gesamte Statistikerfassung — es finden keine Lese- oder Schreibzugriffe auf Dateien statt. Bestehende Daten bleiben erhalten, werden jedoch erst aktualisiert, wenn Sie sie wieder aktivieren.

---

## Hilfe erhalten

- Für MCP-Server-Setup (KI-Agenten-Integration) siehe [docs/MCP.md](MCP.md)
- Für benutzerdefinierte System-Prompts siehe [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- Für Claude Code OAuth-Einrichtung siehe [CLAUDE_CODE.md](CLAUDE_CODE.md)
- Für ChatGPT OAuth-Einrichtung siehe [CHATGPT_OAUTH.md](CHATGPT_OAUTH.md)
- Für GitHub Copilot-Einrichtung siehe [GITHUB_COPILOT.md](GITHUB_COPILOT.md)
- Zur Fehlerbehebung und erweiterten Tipps siehe [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Für Installation und Konfiguration siehe [README.md#installation-and-configuration](README.md#installation-and-configuration)
- Zum Mitwirken siehe [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Lizenzinformationen: [LICENSE](LICENSE)
