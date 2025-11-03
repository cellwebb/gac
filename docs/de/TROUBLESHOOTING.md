# Fehlersuche bei gac

**English** | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | [Français](../fr/TROUBLESHOOTING.md) | [Русский](../ru/TROUBLESHOOTING.md) | [Español](../es/TROUBLESHOOTING.md) | [Português](../pt/TROUBLESHOOTING.md) | [हिन्दी](../hi/CONTRIBUTING.md)

Dieser Leitfaden behandelt häufige Probleme und Lösungen für die Installation, Konfiguration und Ausführung von gac.

## Inhaltsverzeichnis

- [Fehlersuche bei gac](#fehlersuche-bei-gac)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [1. Installationsprobleme](#1-installationsprobleme)
  - [2. Konfigurationsprobleme](#2-konfigurationsprobleme)
  - [3. Anbieter/API-Fehler](#3-anbieterapi-fehler)
  - [4. Commit-Gruppierungsprobleme](#4-commit-gruppierungsprobleme)
  - [5. Sicherheit und Geheimnis-Erkennung](#5-sicherheit-und-geheimnis-erkennung)
  - [6. Pre-commit und Lefthook Hook-Probleme](#6-pre-commit-und-lefthook-hook-probleme)
  - [7. Gemeinsame Workflow-Probleme](#7-gemeinsame-workflow-probleme)
  - [8. Allgemeines Debugging](#8-allgemeines-debugging)
  - [Immer noch festgefahren?](#immer-noch-festgefahren)
  - [Wo man weitere Hilfe bekommt](#wo-man-weitere-hilfe-bekommt)

## 1. Installationsprobleme

**Problem:** `gac` Befehl nach der Installation nicht gefunden

- Stellen Sie sicher, dass Sie mit `uv tool install gac` oder `uvx gac` installiert haben
- Wenn Sie `uv tool install` verwendet haben, überprüfen Sie die Installation mit `uv tool list`
- Stellen Sie sicher, dass `uv` installiert ist und in Ihrem `$PATH` liegt
- Starten Sie Ihr Terminal nach der Installation neu

**Problem:** Berechtigung verweigert oder Dateien können nicht geschrieben werden

- Verzeichnisberechtigungen überprüfen
- Versuchen Sie, mit geeigneten Berechtigungen auszuführen oder Verzeichniseigentümer zu ändern

## 2. Konfigurationsprobleme

**Problem:** gac kann Ihren API-Schlüssel oder Ihr Modell nicht finden

- Wenn Sie neu sind, führen Sie `gac init` aus, um interaktiv Ihren Anbieter, Ihr Modell und Ihre API-Schlüssel einzurichten
- Stellen Sie sicher, dass Ihre `.gac.env` oder Umgebungsvariablen korrekt gesetzt sind
- Führen Sie `gac --log-level=debug` aus, um zu sehen, welche Konfigurationsdateien geladen werden und Konfigurationsprobleme zu debuggen
- Überprüfen Sie auf Tippfehler in Variablennamen (z.B. `GAC_GROQ_API_KEY`)

**Problem:** Benutzer-weite `$HOME/.gac.env` Änderungen werden nicht übernommen

- Stellen Sie sicher, dass Sie die richtige Datei für Ihr Betriebssystem bearbeiten:
  - Auf macOS/Linux: `$HOME/.gac.env` (gewöhnlich `/Users/<ihr-benutzername>/.gac.env` oder `/home/<ihr-benutzername>/.gac.env`)
  - Auf Windows: `$HOME/.gac.env` (typischerweise `C:\Users\<ihr-benutzername>\.gac.env` oder verwenden Sie `%USERPROFILE%`)
- Führen Sie `gac --log-level=debug` aus, um zu bestätigen, dass die Benutzer-weite Konfiguration geladen wird
- Starten Sie Ihr Terminal neu oder führen Sie Ihre Shell erneut aus, um Umgebungsvariablen neu zu laden
- Wenn es immer noch nicht funktioniert, überprüfen Sie auf Tippfehler und Dateiberechtigungen

**Problem:** Projekt-weite `.gac.env` Änderungen werden nicht übernommen

- Stellen Sie sicher, dass Ihr Projekt eine `.gac.env`-Datei im Root-Verzeichnis enthält (neben Ihrem `.git`-Ordner)
- Führen Sie `gac --log-level=debug` aus, um zu bestätigen, dass die projekt-weite Konfiguration geladen wird
- Wenn Sie `.gac.env` bearbeiten, starten Sie Ihr Terminal neu oder führen Sie Ihre Shell erneut aus, um Umgebungsvariablen neu zu laden
- Wenn es immer noch nicht funktioniert, überprüfen Sie auf Tippfehler und Dateiberechtigungen

**Problem:** Sprache für Commit-Nachrichten kann nicht gesetzt oder geändert werden

- Führen Sie `gac language` (oder `gac lang`) aus, um interaktiv aus 25+ unterstützten Sprachen auszuwählen
- Verwenden Sie `-l <language>`-Flag, um die Sprache für einen einzelnen Commit zu überschreiben (z.B. `gac -l zh-CN`, `gac -l Spanish`)
- Überprüfen Sie Ihre Konfiguration mit `gac config show`, um die aktuelle Spracheinstellung zu sehen
- Spracheinstellung wird in `GAC_LANGUAGE` in Ihrer `.gac.env`-Datei gespeichert

## 3. Anbieter/API-Fehler

**Problem:** Authentifizierungs- oder API-Fehler

- Stellen Sie sicher, dass Sie die korrekten API-Schlüssel für Ihr gewähltes Modell gesetzt haben (z.B. `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- Überprüfen Sie Ihren API-Schlüssel und Anbieter-Kontostatus doppelt
- Für Ollama und LM Studio bestätigen Sie, dass die API-URL Ihrer lokalen Instanz entspricht. API-Schlüssel werden nur benötigt, wenn Sie Authentifizierung aktiviert haben.

**Problem:** Modell nicht verfügbar oder nicht unterstützt

- Streamlake verwendet Inferenz-Endpunkt-IDs anstelle von Modellnamen. Stellen Sie sicher, dass Sie die Endpunkt-ID aus ihrer Konsole liefern.
- Überprüfen Sie, ob der Modellname korrekt und von Ihrem Anbieter unterstützt ist
- Überprüfen Sie die Anbieter-Dokumentation für verfügbare Modelle

## 4. Commit-Gruppierungsprobleme

**Problem:** `--group` Flag funktioniert nicht wie erwartet

- Das `--group` Flag analysiert automatisch gestagete Änderungen und kann mehrere logische Commits erstellen
- Die KI kann entscheiden, dass ein einzelner Commit für Ihre Menge gestageter Änderungen sinnvoll ist, sogar mit `--group`
- Dies ist beabsichtigtes Verhalten - die KI gruppiert Änderungen basierend auf logischen Beziehungen, nicht nur auf Menge
- Stellen Sie sicher, dass Sie mehrere nicht zusammenhängende Änderungen gestagt haben (z.B. Fehlerbehebung + Funktionszusatz) für beste Ergebnisse
- Verwenden Sie `gac --show-prompt` zum Debuggen, was die KI sieht

**Problem:** Commits falsch gruppiert oder nicht gruppiert, wenn erwartet

- Die Gruppierung wird von der Analyse Ihrer Änderungen durch die KI bestimmt
- Die KI kann einen einzelnen Commit erstellen, wenn sie feststellt, dass die Änderungen logisch zusammenhängend sind
- Versuchen Sie, Hinweise mit `-h "hint"` hinzuzufügen, um die Gruppierungslogik zu leiten (z.B. `-h "separate bug fix from refactoring"`)
- Überprüfen Sie die generierten Gruppen vor der Bestätigung
- Wenn die Gruppierung für Ihren Anwendungsfall nicht gut funktioniert, committen Sie Änderungen stattdessen getrennt

## 5. Sicherheit und Geheimnis-Erkennung

**Problem:** Falsch positiv: Geheimnis-Scan erkennt Nicht-Geheimnisse

- Der Sicherheits-Scanner sucht nach Mustern, die API-Schlüssel, Tokens und Passwörter ähneln
- Wenn Sie Beispielcode, Test-Fixtures oder Dokumentation mit Platzhalter-Schlüsseln committen, sehen Sie möglicherweise falsch positive Ergebnisse
- Verwenden Sie `--skip-secret-scan`, um den Scan zu umgehen, wenn Sie sicher sind, dass die Änderungen sicher sind
- Erwägen Sie, Test/Beispieldateien von Commits auszuschließen oder verwenden Sie deutlich markierte Platzhalter

**Problem:** Geheimnis-Scan erkennt tatsächliche Geheimnisse nicht

- Der Scanner verwendet Pattern-Matching und kann nicht alle Geheimnis-Typen erfassen
- Überprüfen Sie immer Ihre gestageten Änderungen mit `git diff --staged` vor dem Committen
- Erwägen Sie die Verwendung zusätzlicher Sicherheitswerkzeuge wie `git-secrets` oder `gitleaks` für umfassenden Schutz
- Melden Sie verpasste Muster als Probleme, um die Erkennung zu verbessern

**Problem:** Geheimnis-Scanning permanent deaktivieren müssen

- Setzen Sie `GAC_SKIP_SECRET_SCAN=true` in Ihrer `.gac.env`-Datei
- Verwenden Sie `gac config set GAC_SKIP_SECRET_SCAN true`
- Hinweis: Deaktivieren Sie nur, wenn Sie andere Sicherheitsmaßnahmen an Ort und Stelle haben

## 6. Pre-commit und Lefthook Hook-Probleme

**Problem:** Pre-commit oder lefthook Hooks schlagen fehl und blockieren Commits

- Verwenden Sie `gac --no-verify`, um alle pre-commit und lefthook Hooks vorübergehend zu überspringen
- Beheben Sie die zugrundeliegenden Probleme, die das Fehlschlagen der Hooks verursachen
- Erwägen Sie, Ihre pre-commit oder lefthook Konfiguration anzupassen, wenn die Hooks zu streng sind

**Problem:** Pre-commit oder lefthook Hooks dauern zu lange oder stören den Workflow

- Verwenden Sie `gac --no-verify`, um alle pre-commit und lefthook Hooks vorübergehend zu überspringen
- Erwägen Sie, pre-commit Hooks in `.pre-commit-config.yaml` oder lefthook Hooks in `.lefthook.yml` zu konfigurieren, um weniger aggressiv für Ihren Workflow zu sein
- Überprüfen Sie Ihre Hook-Konfiguration zur Leistungsoptimierung

## 7. Gemeinsame Workflow-Probleme

**Problem:** Keine Änderungen zum Committen / nichts gestagt

- gac erfordert gestagete Änderungen, um eine Commit-Nachricht zu generieren
- Verwenden Sie `git add <files>` zum Stagen von Änderungen, oder verwenden Sie `gac -a`, um alle Änderungen automatisch zu stagen
- Überprüfen Sie `git status`, um zu sehen, welche Dateien geändert wurden
- Verwenden Sie `gac diff`, um eine gefilterte Ansicht Ihrer Änderungen zu sehen

**Problem:** Commit-Nachricht nicht wie erwartet

- Verwenden Sie das interaktive Feedback-System: Geben Sie `r` für Reroll, `e` zum Bearbeiten oder geben Sie natürlich sprachliches Feedback
- Fügen Sie Kontext mit `-h "Ihr Hinweis"` hinzu, um die KI zu leiten
- Verwenden Sie `-o` für einfachere einzeilige Nachrichten oder `-v` für detailliertere Nachrichten
- Verwenden Sie `--show-prompt`, um zu sehen, welche Informationen die KI erhält

**Problem:** gac ist zu langsam

- Verwenden Sie `gac -y`, um den Bestätigungs-Prompt zu überspringen
- Verwenden Sie `gac -q` für den stillen Modus mit weniger Ausgabe
- Erwägen Sie die Verwendung schnellerer/billigerer Modelle für routinemäßige Commits
- Verwenden Sie `gac --no-verify`, um Hooks zu überspringen, wenn sie Sie verlangsamen

**Problem:** Kann nicht bearbeiten oder Feedback nach Nachrichtengenerierung geben

- Am Prompt geben Sie `e` ein, um in den Bearbeitungsmodus zu gelangen (unterstützt vi/emacs Keybindings)
- Geben Sie `r` ein, um ohne Feedback neu zu generieren
- Oder geben Sie einfach Ihr Feedback direkt ein (z.B. "make it shorter", "focus on the bug fix")
- Drücken Sie Enter bei leerer Eingabe, um den Prompt erneut zu sehen

## 8. Allgemeines Debugging

- Verwenden Sie `gac init`, um Ihre Konfiguration interaktiv zurückzusetzen oder zu aktualisieren
- Verwenden Sie `gac --log-level=debug` für detaillierte Debug-Ausgabe und Logging
- Verwenden Sie `gac --show-prompt`, um zu sehen, welcher Prompt an die KI gesendet wird
- Verwenden Sie `gac --help`, um alle verfügbaren Kommandozeilen-Flags zu sehen
- Verwenden Sie `gac config show`, um alle aktuellen Konfigurationswerte zu sehen
- Überprüfen Sie Logs auf Fehlermeldungen und Stack-Traces
- Überprüfen Sie das Haupt-[README.md](../README.md) für Funktionen, Beispiele und schnelle Startanweisungen

## Immer noch festgefahren?

- Suchen Sie nach bestehenden Issues oder öffnen Sie ein neues im [GitHub-Repository](https://github.com/cellwebb/gac)
- Fügen Sie Details über Ihr Betriebssystem, Python-Version, gac-Version, Anbieter und Fehlerausgabe hinzn
- Je mehr Details Sie bereitstellen, desto schneller kann Ihr Problem gelöst werden

## Wo man weitere Hilfe bekommt

- Für Funktionen und Nutzungsbeispiele siehe das Haupt-[README.md](../README.md)
- Für benutzerdefinierte System-Prompts siehe [CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)
- Für Mitwirkungsrichtlinien siehe [CONTRIBUTING.md](../CONTRIBUTING.md)
- Für Lizenzinformationen siehe [../LICENSE](../LICENSE)
