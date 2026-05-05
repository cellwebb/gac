# GitHub Copilot mit GAC verwenden

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | **Deutsch** | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC unterstützt die Authentifizierung über GitHub Copilot, sodass Sie Ihr Copilot-Abonnement verwenden können, um auf Modelle von OpenAI, Anthropic, Google und mehr zuzugreifen — alles in Ihrem GitHub Copilot-Plan enthalten.

## Was ist GitHub Copilot OAuth?

GitHub Copilot OAuth verwendet den **Device Flow** — eine sichere, browserbasierte Authentifizierungsmethode, die keinen lokalen Callback-Server erfordert. Sie besuchen eine URL, geben einen Einmalcode ein und autorisieren GAC, Ihren Copilot-Zugang zu nutzen. Im Hintergrund tauscht GAC Ihr langlebiges GitHub-OAuth-Token gegen kurzlebige Copilot-Sitzungstoken (~30 Min.) aus, die den Zugang zur Copilot-API gewähren.

Dies gibt Ihnen Zugang zu Modellen mehrerer Anbieter über ein einzelnes Abonnement:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Vorteile

- **Multi-Anbieter-Zugang**: Verwenden Sie Modelle von OpenAI, Anthropic und Google über ein einzelnes Abonnement
- **Kosteneffektiv**: Nutzen Sie Ihr bestehendes Copilot-Abonnement anstatt separat für API-Schlüssel zu bezahlen
- **Keine API-Schlüsselverwaltung**: Device-Flow-Authentifizierung — keine Schlüssel zum Rotieren oder Speichern
- **GitHub Enterprise-Unterstützung**: Funktioniert mit GHE-Instanzen über das `--host`-Flag

## Einrichtung

### Option 1: Während der ersten Einrichtung (Empfohlen)

Wenn Sie `gac init` ausführen, wählen Sie einfach „Copilot" als Ihren Anbieter:

```bash
gac init
```

Der Assistent wird:

1. Sie auffordern, „Copilot" aus der Anbieterliste auszuwählen
2. Einen Einmalcode anzeigen und Ihren Browser für die Device-Flow-Authentifizierung öffnen
3. Ihr OAuth-Token in `~/.gac/oauth/copilot.json` speichern
4. Das Standardmodell festlegen

### Option 2: Später zu Copilot wechseln

Wenn Sie GAC bereits mit einem anderen Anbieter konfiguriert haben:

```bash
gac model
```

Wählen Sie dann „Copilot" aus der Anbieterliste und authentifizieren Sie sich.

### Option 3: Direkte Anmeldung

Authentifizieren Sie sich direkt, ohne Ihr Standardmodell zu ändern:

```bash
gac auth copilot login
```

### GAC normal verwenden

Nach der Authentifizierung verwenden Sie GAC wie gewohnt:

```bash
# Ihre Änderungen stagen
git add .

# Mit Copilot generieren und committen
gac

# Oder das Modell für einen einzelnen Commit überschreiben
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Verfügbare Modelle

Copilot bietet Zugang zu Modellen mehrerer Anbieter. Aktuelle Modelle umfassen:

| Anbieter  | Modelle                                                                                        |
| --------- | ---------------------------------------------------------------------------------------------- |
| OpenAI    | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google    | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Hinweis:** Die nach der Anmeldung angezeigte Modellliste ist informativ und kann veralten, wenn GitHub neue Modelle hinzufügt. Überprüfen Sie die [GitHub Copilot-Dokumentation](https://docs.github.com/en/copilot) für die aktuell verfügbaren Modelle.

## GitHub Enterprise

Um sich bei einer GitHub Enterprise-Instanz zu authentifizieren:

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC verwendet automatisch die korrekten Device-Flow- und API-Endpunkte für Ihre GHE-Instanz. Das Sitzungstoken wird pro Host zwischengespeichert, sodass verschiedene GHE-Instanzen unabhängig voneinander verwaltet werden.

## CLI-Befehle

GAC bietet dedizierte CLI-Befehle für die Copilot-Authentifizierungsverwaltung:

### Anmelden

Authentifizieren oder erneut authentifizieren Sie sich mit GitHub Copilot:

```bash
gac auth copilot login
```

Ihr Browser öffnet sich zu einer Device-Flow-Seite, auf der Sie einen Einmalcode eingeben. Wenn Sie bereits authentifiziert sind, werden Sie gefragt, ob Sie sich erneut authentifizieren möchten.

Für GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Abmelden

Entfernen Sie gespeicherte Copilot-Tokens:

```bash
gac auth copilot logout
```

Dies löscht die gespeicherte Token-Datei unter `~/.gac/oauth/copilot.json` und den Sitzungs-Cache.

### Status

Überprüfen Sie Ihren aktuellen Copilot-Authentifizierungsstatus:

```bash
gac auth copilot status
```

Oder überprüfen Sie alle Anbieter auf einmal:

```bash
gac auth
```

## Wie es funktioniert

Der Copilot-Authentifizierungsflow unterscheidet sich von ChatGPT und Claude Code OAuth:

1. **Device Flow** — GAC fordert einen Gerätcode von GitHub an und zeigt ihn an
2. **Browser-Autorisierung** — Sie besuchen die URL und geben den Code ein
3. **Token-Polling** — GAC fragt GitHub ab, bis Sie die Autorisierung abschließen
4. **Sitzungstoken-Austausch** — Das GitHub-OAuth-Token wird gegen ein kurzlebiges Copilot-Sitzungstoken ausgetauscht
5. **Automatische Aktualisierung** — Sitzungstoken (~30 Min.) werden automatisch aus dem zwischengespeicherten OAuth-Token erneuert

Im Gegensatz zu PKCE-basiertem OAuth (ChatGPT/Claude Code) erfordert der Device Flow keinen lokalen Callback-Server oder Port-Verwaltung.

## Fehlerbehebung

### „Copilot-Authentifizierung nicht gefunden"

Führen Sie den Anmeldebefehl aus, um sich zu authentifizieren:

```bash
gac auth copilot login
```

### „Copilot-Sitzungstoken konnte nicht abgerufen werden"

Dies bedeutet, dass GAC ein GitHub-OAuth-Token erhalten hat, aber es nicht gegen ein Copilot-Sitzungstoken austauschen konnte. Normalerweise bedeutet dies:

1. **Kein Copilot-Abonnement** — Ihr GitHub-Konto hat kein aktives Copilot-Abonnement
2. **Token widerrufen** — Das OAuth-Token wurde widerrufen; authentifizieren Sie sich erneut mit `gac auth copilot login`

### Sitzungstoken abgelaufen

Sitzungstoken laufen nach ~30 Minuten ab. GAC erneuert sie automatisch aus dem zwischengespeicherten OAuth-Token, sodass Sie sich nicht häufig neu authentifizieren müssen. Wenn die automatische Aktualisierung fehlschlägt:

```bash
gac auth copilot login
```

### „Ungültiger oder unsicherer Hostname"

Das `--host`-Flag validiert Hostnamen streng, um SSRF-Angriffe zu verhindern. Wenn Sie diesen Fehler sehen:

- Stellen Sie sicher, dass der Hostname keine Ports enthält (z.B. `ghe.company.com` statt `ghe.company.com:8080`)
- Keine Protokolle oder Pfade einschließen (z.B. `ghe.company.com` statt `https://ghe.company.com/api`)
- Private IP-Adressen und `localhost` sind aus Sicherheitsgründen blockiert

### GitHub Enterprise-Probleme

Wenn die GHE-Authentifizierung fehlschlägt:

1. Überprüfen Sie, ob Ihre GHE-Instanz Copilot aktiviert hat
2. Prüfen Sie, ob Ihr GHE-Hostname von Ihrem Computer aus erreichbar ist
3. Stellen Sie sicher, dass Ihr GHE-Konto eine Copilot-Lizenz hat
4. Versuchen Sie es mit dem `--host`-Flag explizit: `gac auth copilot login --host ghe.mycompany.com`

## Unterschiede zu anderen OAuth-Anbietern

| Funktion          | ChatGPT OAuth            | Claude Code             | Copilot                                      |
| ----------------- | ------------------------ | ----------------------- | -------------------------------------------- |
| Auth-Methode      | PKCE (Browser-Callback)  | PKCE (Browser-Callback) | Device Flow (Einmalcode)                     |
| Callback-Server   | Ports 1455-1465          | Ports 8765-8795         | Nicht erforderlich                           |
| Token-Lebensdauer | Langlebig (Auto-Refresh) | Ablaufend (Neu-Auth)    | Sitzung ~30 Min. (Auto-Refresh)              |
| Modelle           | Codex-optimiertes OpenAI | Claude-Familie          | Multi-Anbieter (OpenAI + Anthropic + Google) |
| GHE-Unterstützung | Nein                     | Nein                    | Ja (`--host`-Flag)                           |

## Sicherheitshinweise

- **Committen Sie niemals Ihr OAuth-Token** in die Versionskontrolle
- GAC speichert OAuth-Tokens in `~/.gac/oauth/copilot.json` (außerhalb Ihres Projektverzeichnisses)
- Sitzungstoken werden in `~/.gac/oauth/copilot_session.json` mit `0o600`-Berechtigungen zwischengespeichert
- Hostnamen werden streng validiert, um SSRF- und URL-Injektionsangriffe zu verhindern
- Private IP-Adressen, Loopback-Adressen und `localhost` sind als Hostnamen blockiert
- Der Device Flow öffnet keine lokalen Ports, was die Angriffsfläche verringert

## Siehe auch

- [Hauptdokumentation](USAGE.md)
- [Fehlerbehebungsanleitung](TROUBLESHOOTING.md)
- [ChatGPT OAuth-Anleitung](CHATGPT_OAUTH.md)
- [Claude Code-Anleitung](CLAUDE_CODE.md)
- [GitHub Copilot-Dokumentation](https://docs.github.com/en/copilot)
