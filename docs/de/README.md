<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

# 🚀 Git Auto Commit (gac)

[![PyPI version](https://img.shields.io/pypi/v/gac.svg)](https://pypi.org/project/gac/)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/de/CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](../../README.md) | [简体中文](../zh-CN/README.md) | [繁體中文](../zh-TW/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [हिन्दी](../hi/README.md) | [Tiếng Việt](../vi/README.md) | [Français](../fr/README.md) | [Русский](../ru/README.md) | [Español](../es/README.md) | [Português](../pt/README.md) | [Norsk](../no/README.md) | [Svenska](../sv/README.md) | **Deutsch** | [Nederlands](../nl/README.md) | [Italiano](../it/README.md)

**KI-gestützte Commit-Nachrichten, die Ihren Code verstehen!**

**Automatisieren Sie Ihre Commits!** Ersetzen Sie `git commit -m "..."` durch `gac` für kontextbezogene, gut formatierte Commit-Nachrichten, die von großen Sprachmodellen generiert werden!

---

## Was Sie erhalten

Intelligente, kontextbezogene Nachrichten, die das **Warum** hinter Ihren Änderungen erklären:

![GAC generating a contextual commit message](../../assets/gac-simple-usage.de.png)

---

</div>

<!-- markdownlint-enable MD033 MD036 -->

## Schnellstart

### gac ohne Installation verwenden

```bash
uvx gac init   # Konfigurieren Sie Ihren Provider, Ihr Modell und Ihre Sprache
uvx gac  # Generieren und committen mit KI
```

Das ist alles! Überprüfen Sie die generierte Nachricht und bestätigen Sie mit `y`.

### gac installieren und verwenden

```bash
uv tool install gac
gac init
gac
```

### Installiertes gac aktualisieren

```bash
uv tool upgrade gac
```

---

## Hauptfunktionen

### 🌐 **25+ Unterstützte Provider**

- **Anthropic** • **Azure OpenAI** • **Cerebras** • **Chutes.ai** • **Claude Code (OAuth)**
- **DeepSeek** • **Fireworks** • **Gemini** • **Groq** • **Kimi for Coding** • **LM Studio**
- **MiniMax.io** • **Mistral AI** • **Moonshot AI** • **Ollama** • **OpenAI** • **OpenRouter**
- **Qwen Cloud (CN & INTL)** • **Replicate** • **Streamlake** • **Synthetic.new** • **Together AI**
- **Wafer.ai** • **Z.AI** • **Z.AI Coding** • **Custom Endpoints (Anthropic/OpenAI)**

### 🧠 **Intelligente KI-Analyse**

- **Versteht die Absicht**: Analysiert Code-Struktur, Logik und Muster, um das "Warum" hinter Ihren Änderungen zu verstehen, nicht nur was sich geändert hat
- **Semantisches Bewusstsein**: Erkennt Refactoring, Bug-Fixes, Features und Breaking Changes, um kontextbezogene Nachrichten zu generieren
- **Intelligentes Filtern**: Priorisiert sinnvolle Änderungen und ignoriert generierte Dateien, Abhängigkeiten und Artefakte
- **Intelligentes Commit-Grouping** - Gruppiert automatisch zusammengehörige Änderungen in mehreren logischen Commits mit `--group`

### 📝 **Mehrere Nachrichtenformate**

- **Einzeiler** (-o Flag): Einzeilige Commit-Nachricht im conventional commit Format
- **Standard** (Standard): Zusammenfassung mit Stichpunkten zur Erklärung der Implementierungsdetails
- **Ausführlich** (-v Flag): Umfassende Erklärungen inklusive Motivation, technischer Herangehensweise und Impact-Analyse
- **50/72 Regel** (--50-72 Flag): Erzwingt das klassische Commit-Message-Format für optimale Lesbarkeit in git log und GitHub UI
- **DCO/Signoff** (--signoff Flag): Fügt Signed-off-by Zeile für Developer Certificate of Origin Compliance hinzu (erforderlich von Cherry Studio, Linux Kernel und anderen Projekten)

### 🌍 **Mehrsprachige Unterstützung**

- **25+ Sprachen**: Generieren Sie Commit-Nachrichten in Englisch, Chinesisch, Japanisch, Koreanisch, Spanisch, Französisch, Deutsch und 20+ weiteren Sprachen
- **Flexible Übersetzung**: Wählen Sie, ob Sie conventional commit Präfixe auf Englisch für Tool-Kompatibilität belassen oder vollständig übersetzen möchten
- **Mehrere Workflows**: Stellen Sie eine Standardsprache mit `gac language` ein oder verwenden Sie das `-l <Sprache>`-Flag für einmalige Überschreibungen
- **Unterstützung für native Skripte**: Volle Unterstützung für nicht-lateinische Skripte inklusive CJK, Kyrillisch, Thai und mehr

### 💻 **Developer Experience**

- **Interaktives Feedback**: Geben Sie `r` ein zum erneuten Generieren, `e` zum direkten Bearbeiten mit vi/emacs Tastaturbelegungen oder geben Sie direkt Ihr Feedback ein wie `mache es kürzer` oder `konzentriere dich auf den Bug-Fix`
- **Interaktive Befragung**: Verwenden Sie `--interactive` (`-i`) um gezielte Fragen zu Ihren Änderungen zu beantworten für mehr kontextbezogene Commit-Nachrichten
- **Ein-Befehl-Workflows**: Vollständige Workflows mit Flags wie `gac -ayp` (alles hinzufügen, automatisch Bestätigen, pushen)
- **Git-Integration**: Respektiert pre-commit und leftthook Hooks, führt sie vor teuren KI-Operationen aus
- **MCP-Server**: Führen Sie `gac serve` aus, um Commit-Tools über das [Model Context Protocol](https://modelcontextprotocol.io/) für KI-Agenten bereitzustellen

### 📊 **Nutzungsstatistiken**

- **Verfolgen Sie Ihre gacs**: Sehen Sie, wie viele Commits Sie mit gac gemacht haben, Ihren aktuellen Streak, die höchste tägliche/wöchentliche Aktivität und Top-Projekte
- **Projektspezifische Statistiken**: Zeigen Sie Statistiken für das aktuelle Repo mit `gac stats project` an
- **Highscore-Feiern**: 🏆 Trophäen, wenn Sie neue tägliche, wöchentliche oder Streak-Rekorde aufstellen; 🥈 wenn Sie diese einstellen
- **Opt-out-freundlich**: Setzen Sie `GAC_DISABLE_STATS=1`, um die Erfassung zu deaktivieren — es werden keine Daten geschrieben
- **Datenschutz zuerst**: Speichert nur Zähler, Daten und Projektnamen (abgeleitet vom Git-Remote/Verzeichnis) — keine Commit-Nachrichten, Code oder persönliche Daten

### 🛡️ **Eingebaute Sicherheit**

- **Automatische Geheimnis-Erkennung**: Scannt vor dem Commit nach API-Schlüsseln, Passwörtern und Tokens
- **Interaktiver Schutz**: Fordert vor dem Commit potenziell sensible Daten auf mit klaren Korrekturoptionen
- **Intelligentes Filtern**: Ignoriert Beispieldateien, Vorlagendateien und Platzhaltertext zur Reduzierung von Falschpositiven

---

## Verwendungsbeispiele

### Basis-Workflow

```bash
# Ihre Änderungen hinzufügen
git add .

# Generieren und committen mit KI
gac

# Überprüfen → y (commit) | n (abbrechen) | r (erneut generieren) | e (bearbeiten) | oder Feedback eingeben
```

### Häufige Befehle

| Befehl             | Beschreibung                                                                         |
| ------------------ | ------------------------------------------------------------------------------------ |
| `gac`              | Commit-Nachricht generieren                                                          |
| `gac -y`           | Automatisch bestätigen (keine Überprüfung erforderlich)                              |
| `gac -a`           | Alle Änderungen vor der Generierung der Commit-Nachricht hinzufügen                  |
| `gac -o`           | Einzeilige Nachricht für triviale Änderungen                                         |
| `gac -v`           | Ausführliches Format mit Motivation, technischer Herangehensweise und Impact-Analyse |
| `gac -h "hinweis"` | Kontext für KI hinzufügen (z.B. `gac -h "bug fix"`)                                  |
| `gac -s`           | Scope einschließen (z.B. feat(auth):)                                                |
| `gac -i`           | Fragen zu Änderungen stellen für besseren Kontext                                    |
| `gac -g`           | Änderungen in mehrere logische Commits gruppieren                                    |
| `gac -p`           | Commit und push                                                                      |
| `gac stats`        | Ihre gac-Nutzungsstatistiken anzeigen                                                |

### Power-User-Beispiele

```bash
# Vollständiger Workflow in einem Befehl
# Ihre Commit-Statistiken anzeigen
gac stats

# Statistiken nur für das aktuelle Projekt
gac stats project

gac -ayp -h "Release-Vorbereitung"

# Detaillierte Erklärung mit Scope
gac -v -s

# Schneller Einzeiler für kleine Änderungen
gac -o

# Änderungen in logisch zusammengehörige Commits gruppieren
gac -ag

# Interaktiver Modus mit ausführlicher Ausgabe für detaillierte Erklärungen
gac -iv

# Debuggen, was die KI sieht
gac --show-prompt

# Sicherheits-Scan überspringen (vorsichtig verwenden)
gac --skip-secret-scan

# Signoff für DCO Compliance hinzufügen (Cherry Studio, Linux Kernel, etc.)
gac --signoff
```

### Interaktives Feedback-System

Nicht zufrieden mit dem Ergebnis? Sie haben mehrere Optionen:

```bash
# Einfaches erneutes Generieren (kein Feedback)
r

# Direkt bearbeiten mit erweitertem Terminal-Editing
e
# Verwendet prompt_toolkit für mehrzeiliges Editing mit vi/emacs Tastaturbelegungen
# Esc+Enter oder Ctrl+S zum Absenden, Ctrl+C zum Abbrechen
# Oder geben Sie Ihr Feedback direkt ein!
mache es kürzer und konzentriere dich auf die Performance-Verbesserung
verwende conventional commit Format mit Scope
erkläre die Sicherheitsimplikationen

# Enter bei leerer Eingabe drücken, um die Eingabeaufforderung erneut zu sehen
```

Die Bearbeitungsfunktion (`e`) bietet erweitertes direktes Terminal-Editing, das es Ihnen ermöglicht:

- **Natürlich bearbeiten**: Mehrzeiliges Editing mit bekannten vi/emacs Tastaturbelegungen
- **Schnelle Korrekturen**: Tippfehler korrigieren, Wortlaut anpassen oder Formatierung verfeinern
- **Details hinzufügen**: Informationen einfügen, die die KI möglicherweise übersehen hat
- **Umstrukturieren**: Stichpunkte neu anordnen oder Nachrichtenstruktur ändern

---

## Konfiguration

Führen Sie `gac init` aus, um Ihren Provider interaktiv zu konfigurieren, oder setzen Sie Umgebungsvariablen:

Später Provider oder Modelle ändern, ohne Spracheinstellungen zu berühren? Verwenden Sie `gac model` für einen Optimierten Ablauf, der die Spracheingabeaufforderungen überspringt.

```bash
# Beispielkonfiguration
GAC_MODEL=anthropic:your-model-name
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Siehe `.gac.env.example` für alle verfügbaren Optionen.

**Möchten Sie Commit-Nachrichten in einer anderen Sprache?** Führen Sie `gac language` aus, um aus 25+ Sprachen zu wählen, inklusive Español, Français, 日本語 und mehr.

**Möchten Sie den Stil der Commit-Nachrichten anpassen?** Siehe [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/de/CUSTOM_SYSTEM_PROMPTS.md) für Anleitungen zum Schreiben von benutzerdefinierten System-Prompts.

---

## Projekt-Analytics

📊 **[Live-Nutzungsanalytics und Statistiken ansehen →](https://clickpy.clickhouse.com/dashboard/gac)**

Verfolgen Sie Echtzeit-Installationsmetriken und Paket-Download-Statistiken.

---

## Hilfe erhalten

- **Vollständige Dokumentation**: [docs/USAGE.md](docs/de/USAGE.md) - Vollständige CLI-Referenz
- **MCP-Server**: [docs/MCP.md](MCP.md) - GAC als MCP-Server für KI-Agenten verwenden
- **Claude Code OAuth**: [docs/CLAUDE_CODE.md](docs/de/CLAUDE_CODE.md) - Claude Code Einrichtung und Authentifizierung
- **Benutzerdefinierte Prompts**: [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/de/CUSTOM_SYSTEM_PROMPTS.md) - Commit-Nachrichten-Stil anpassen
- **Nutzungsstatistiken**: Siehe `gac stats --help` oder die [vollständige Doku](docs/de/USAGE.md#nutzungsstatistiken)
- **Fehlerbehebung**: [docs/TROUBLESHOOTING.md](docs/de/TROUBLESHOOTING.md) - Häufige Probleme und Lösungen
- **Mitwirken**: [docs/CONTRIBUTING.md](docs/de/CONTRIBUTING.md) - Entwicklungseinrichtung und Richtlinien

---

<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

Mit ❤️ gemacht für Entwickler, die bessere Commit-Nachrichten wollen

[⭐ Star uns auf GitHub](https://github.com/cellwebb/gac) • [🐛 Probleme melden](https://github.com/cellwebb/gac/issues) • [📖 Vollständige Doku](docs/de/USAGE.md)

</div>

<!-- markdownlint-enable MD033 MD036 -->
