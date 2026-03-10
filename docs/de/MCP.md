# GAC als MCP-Server verwenden

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | **Deutsch** | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC kann als [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)-Server betrieben werden, sodass KI-Agenten und Editoren Commits durch strukturierte Tool-Aufrufe statt Shell-Befehle erstellen koennen.

## Inhaltsverzeichnis

- [GAC als MCP-Server verwenden](#gac-als-mcp-server-verwenden)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Was ist MCP?](#was-ist-mcp)
  - [Vorteile](#vorteile)
  - [Einrichtung](#einrichtung)
    - [Claude Code](#claude-code)
    - [Cursor](#cursor)
    - [Andere MCP-Clients](#andere-mcp-clients)
  - [Verfuegbare Tools](#verfuegbare-tools)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Workflows](#workflows)
    - [Einfacher Commit](#einfacher-commit)
    - [Vorschau vor dem Commit](#vorschau-vor-dem-commit)
    - [Gruppierte Commits](#gruppierte-commits)
    - [Commit mit Kontext](#commit-mit-kontext)
  - [Konfiguration](#konfiguration)
  - [Fehlerbehebung](#fehlerbehebung)
  - [Siehe auch](#siehe-auch)

## Was ist MCP?

Das Model Context Protocol ist ein offener Standard, der es KI-Anwendungen ermoeglicht, externe Tools ueber eine strukturierte Schnittstelle aufzurufen. Indem GAC als MCP-Server ausgefuehrt wird, kann jeder MCP-kompatible Client den Repository-Status pruefen und KI-gestuetzte Commits erstellen, ohne Shell-Befehle direkt aufzurufen.

## Vorteile

- **Strukturierte Interaktion**: Agenten rufen typisierte Tools mit validierten Parametern auf, anstatt Shell-Ausgaben zu parsen
- **Zwei-Tool-Workflow**: `gac_status` zum Inspizieren, `gac_commit` zum Handeln - ideal fuer agentenbasiertes Reasoning
- **Volle GAC-Funktionalitaet**: KI-Commit-Nachrichten, gruppierte Commits, Geheimnis-Scanning und Push - alles ueber MCP verfuegbar
- **Keine zusaetzliche Konfiguration**: Der Server verwendet Ihre bestehende GAC-Konfiguration (`~/.gac.env`, Provider-Einstellungen usw.)

## Einrichtung

Der MCP-Server wird mit `gac serve` gestartet und kommuniziert ueber stdio, den Standard-MCP-Transport.

### Claude Code

Fuegen Sie dies zu Ihrer Projekt-Datei `.mcp.json` oder globalen `~/.claude/claude_code_config.json` hinzu:

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

Oder wenn GAC global installiert ist:

```json
{
  "mcpServers": {
    "gac": {
      "command": "gac",
      "args": ["serve"]
    }
  }
}
```

### Cursor

Fuegen Sie dies zu Ihren Cursor MCP-Einstellungen hinzu (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### Andere MCP-Clients

Jeder MCP-kompatible Client kann GAC verwenden. Der Server-Einstiegspunkt ist:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

Wenn GAC installiert ist (ueber `uv tool install gac`), koennen Sie `gac` direkt anstelle von `uvx gac` verwenden.

## Verfuegbare Tools

Der Server stellt zwei Tools bereit:

### gac_status

Inspiziert den Repository-Status. Verwenden Sie dies vor dem Commit, um zu verstehen, was committet wird.

**Parameter:**

| Parameter           | Type                                    | Default     | Beschreibung                                 |
| ------------------- | --------------------------------------- | ----------- | -------------------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Ausgabeformat                                |
| `include_diff`      | bool                                    | `false`     | Vollstaendigen Diff-Inhalt einschliessen     |
| `include_stats`     | bool                                    | `true`      | Statistiken der Zeilenaenderungen anzeigen   |
| `include_history`   | int                                     | `0`         | Anzahl der letzten Commits zum Einschliessen |
| `staged_only`       | bool                                    | `false`     | Nur gestufte Aenderungen anzeigen            |
| `include_untracked` | bool                                    | `true`      | Nicht verfolgte Dateien einschliessen        |
| `max_diff_lines`    | int                                     | `500`       | Diff-Ausgabe begrenzen (0 = unbegrenzt)      |

**Rueckgabe:** Branch-Name, Dateistatus (gestuftet/ungestuftet/nicht verfolgt/Konflikte), optionaler Diff-Inhalt, optionale Statistiken und optionaler Commit-Verlauf.

### gac_commit

Generiert eine KI-gestuetzte Commit-Nachricht und fuehrt optional den Commit aus.

**Parameter:**

| Parameter          | Type           | Default | Beschreibung                                                          |
| ------------------ | -------------- | ------- | --------------------------------------------------------------------- |
| `stage_all`        | bool           | `false` | Alle Aenderungen vor dem Commit stufen (`git add -A`)                 |
| `files`            | list[str]      | `[]`    | Bestimmte Dateien zum Stufen                                          |
| `dry_run`          | bool           | `false` | Vorschau ohne Ausfuehrung                                             |
| `message_only`     | bool           | `false` | Nachricht generieren ohne Commit                                      |
| `push`             | bool           | `false` | Nach dem Commit zum Remote pushen                                     |
| `group`            | bool           | `false` | Aenderungen in mehrere logische Commits aufteilen                     |
| `one_liner`        | bool           | `false` | Einzeilige Commit-Nachricht                                           |
| `scope`            | string \| null | `null`  | Conventional Commit Scope (automatisch erkannt, wenn nicht angegeben) |
| `hint`             | string         | `""`    | Zusaetzlicher Kontext fuer bessere Nachrichten                        |
| `model`            | string \| null | `null`  | KI-Modell ueberschreiben (`provider:model_name`)                      |
| `language`         | string \| null | `null`  | Sprache der Commit-Nachricht ueberschreiben                           |
| `skip_secret_scan` | bool           | `false` | Sicherheitsscan ueberspringen                                         |
| `no_verify`        | bool           | `false` | Pre-Commit-Hooks ueberspringen                                        |
| `auto_confirm`     | bool           | `false` | Bestaetigungsaufforderungen ueberspringen (fuer Agenten erforderlich) |

**Rueckgabe:** Erfolgsstatus, generierte Commit-Nachricht, Commit-Hash (falls committed), Liste der geaenderten Dateien und eventuelle Warnungen.

## Workflows

### Einfacher Commit

```text
1. gac_status()                              → Sehen, was sich geaendert hat
2. gac_commit(stage_all=true, auto_confirm=true)  → Stufen, Nachricht generieren und committen
```

### Vorschau vor dem Commit

```text
1. gac_status(include_diff=true, include_stats=true)  → Aenderungen im Detail pruefen
2. gac_commit(stage_all=true, dry_run=true)            → Commit-Nachricht in der Vorschau ansehen
3. gac_commit(stage_all=true, auto_confirm=true)       → Commit ausfuehren
```

### Gruppierte Commits

```text
1. gac_status()                                           → Alle Aenderungen anzeigen
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Logische Gruppierungen in der Vorschau ansehen
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Gruppierte Commits ausfuehren
```

### Commit mit Kontext

```text
1. gac_status(include_history=5)  → Letzte Commits als Stilreferenz anzeigen
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Konfiguration

Der MCP-Server verwendet Ihre bestehende GAC-Konfiguration. Ueber Folgendes hinaus ist keine zusaetzliche Einrichtung erforderlich:

1. **Provider und Modell**: Fuehren Sie `gac init` oder `gac model` aus, um Ihren KI-Provider zu konfigurieren
2. **API-Schluessel**: Gespeichert in `~/.gac.env` (eingerichtet waehrend `gac init`)
3. **Optionale Einstellungen**: Alle GAC-Umgebungsvariablen gelten (`GAC_LANGUAGE`, `GAC_VERBOSE` usw.)

Siehe die [Hauptdokumentation](USAGE.md#konfigurationshinweise) fuer alle Konfigurationsoptionen.

## Fehlerbehebung

### "No model configured"

Fuehren Sie `gac init` aus, um Ihren KI-Provider und Ihr Modell einzurichten, bevor Sie den MCP-Server verwenden.

### "No staged changes found"

Stufen Sie Dateien manuell (`git add`) oder verwenden Sie `stage_all=true` im `gac_commit`-Aufruf.

### Server startet nicht

Ueberpruefen Sie, ob GAC installiert und zugaenglich ist:

```bash
uvx gac --version
# oder
gac --version
```

Wenn Sie `uvx` verwenden, stellen Sie sicher, dass `uv` installiert und in Ihrem PATH ist.

### Agent findet den Server nicht

Stellen Sie sicher, dass die MCP-Konfigurationsdatei am richtigen Ort fuer Ihren Client liegt und dass der `command`-Pfad von Ihrer Shell-Umgebung aus zugaenglich ist.

### Rich-Ausgabe-Korruption

Der MCP-Server leitet alle Rich-Konsolenausgaben automatisch auf stderr um, um stdio-Protokoll-Korruption zu verhindern. Wenn Sie fehlerhafte Ausgaben sehen, stellen Sie sicher, dass Sie `gac serve` (nicht `gac` direkt) ausfuehren, wenn Sie MCP verwenden.

## Siehe auch

- [Hauptdokumentation](USAGE.md)
- [Claude Code OAuth-Einrichtung](CLAUDE_CODE.md)
- [Qwen.ai OAuth-Einrichtung](QWEN.md)
- [Fehlerbehebungsleitfaden](TROUBLESHOOTING.md)
- [MCP-Spezifikation](https://modelcontextprotocol.io/)
