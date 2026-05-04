# ChatGPT OAuth mit GAC verwenden

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC unterstützt die Authentifizierung über ChatGPT OAuth, sodass Sie Ihr ChatGPT-Abonnement verwenden können, um auf die Codex-API von OpenAI zuzugreifen, anstatt separate OpenAI API-Schlüssel zu bezahlen. Dies spiegelt denselben OAuth-Flow wider, der von der Codex CLI von OpenAI verwendet wird.

> ⚠️ **Achtung — nicht genehmigte Verwendung:** Dies verwendet denselben OAuth-Flow wie die Codex CLI von OpenAI, und obwohl es derzeit funktioniert, kann OpenAI die Verwendung von Tokens durch Dritte jederzeit einschränken. GAC ist klein genug, um bisher unter dem Radar geblieben zu sein, aber die Verwendung von ChatGPT OAuth hier ist **nicht offiziell genehmigt** für Drittanbieter-Tools und kann jederzeit aufhören zu funktionieren. Wenn Sie eine zuverlässige Generierung von Commit-Nachrichten benötigen, verwenden Sie einen direkten API-Anbieter (`openai` usw.). Siehe [Codex-Dokumentation von OpenAI](https://openai.com/codex) für die aktuelle Richtlinie.

## Was ist ChatGPT OAuth?

ChatGPT OAuth ermöglicht es Ihnen, Ihr bestehendes ChatGPT Plus- oder Pro-Abonnement zu nutzen, um auf die Codex-API zuzugreifen, um Commit-Nachrichten zu generieren. Anstatt API-Schlüssel und Token-basierte Abrechnung zu verwalten, authentifizieren Sie sich einmal über Ihren Browser und GAC verwaltet den Token-Lebenszyklus automatisch.

## Vorteile

- **Kosteneffektiv**: Verwenden Sie Ihr bestehendes ChatGPT Plus/Pro-Abonnement, anstatt separat für API-Zugriff zu bezahlen
- **Gleiche Modelle**: Greifen Sie auf Codex-optimierte Modelle zu (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **Keine API-Schlüsselverwaltung**: Browserbasierter OAuth bedeutet, dass keine API-Schlüssel rotiert oder gespeichert werden müssen
- **Separate Abrechnung**: Die Verwendung von ChatGPT OAuth ist von der direkten OpenAI API-Abrechnung getrennt

## Einrichtung

GAC enthält eine integrierte OAuth-Authentifizierung für ChatGPT. Der Einrichtungsprozess ist vollständig automatisiert und öffnet Ihren Browser zur Authentifizierung.

### Option 1: Während der ersten Einrichtung (Empfohlen)

Wenn Sie `gac init` ausführen, wählen Sie einfach «ChatGPT OAuth» als Ihren Anbieter:

```bash
gac init
```

Der Assistent wird:

1. Sie auffordern, «ChatGPT OAuth» aus der Anbieterliste auszuwählen
2. Automatisch Ihren Browser zur OAuth-Authentifizierung öffnen
3. Ihren Zugriffstoken in `~/.gac/oauth/chatgpt-oauth.json` speichern
4. Das Standardmodell festlegen

### Option 2: Später zu ChatGPT OAuth wechseln

Wenn Sie GAC bereits mit einem anderen Anbieter konfiguriert haben und zu ChatGPT OAuth wechseln möchten:

```bash
gac model
```

Dann:

1. Wählen Sie «ChatGPT OAuth» aus der Anbieterliste
2. Ihr Browser wird automatisch zur OAuth-Authentifizierung geöffnet
3. Token gespeichert in `~/.gac/oauth/chatgpt-oauth.json`
4. Modell automatisch konfiguriert

### GAC normal verwenden

Nach der Authentifizierung verwenden Sie GAC wie gewohnt:

```bash
# Ihre Änderungen stagen
git add .

# Mit ChatGPT OAuth generieren und committen
gac

# Oder das Modell für einen einzelnen Commit überschreiben
gac -m chatgpt-oauth:gpt-5.5
```

## Verfügbare Modelle

ChatGPT OAuth bietet Zugriff auf Codex-optimierte Modelle. Aktuelle Modelle umfassen:

- `gpt-5.5` — Neuestes und leistungsfähigstes Codex-Modell
- `gpt-5.4` — Codex-Modell der vorherigen Generation
- `gpt-5.3-codex` — Codex-Modell der dritten Generation

Überprüfen Sie die [OpenAI-Dokumentation](https://platform.openai.com/docs/models) für die vollständige Liste der verfügbaren Modelle.

## CLI-Befehle

GAC bietet dedizierte CLI-Befehle für die ChatGPT OAuth-Verwaltung:

### Anmelden

Authentifizieren oder erneut authentifizieren Sie sich mit ChatGPT OAuth:

```bash
gac auth chatgpt login
```

Ihr Browser wird automatisch geöffnet, um den OAuth-Flow abzuschließen. Wenn Sie bereits authentifiziert sind, werden Ihre Tokens aktualisiert.

### Abmelden

Entfernen Sie gespeicherte ChatGPT OAuth-Tokens:

```bash
gac auth chatgpt logout
```

Dies löscht die gespeicherte Token-Datei unter `~/.gac/oauth/chatgpt-oauth.json`.

### Status

Überprüfen Sie Ihren aktuellen ChatGPT OAuth-Authentifizierungsstatus:

```bash
gac auth chatgpt status
```

Oder überprüfen Sie alle Anbieter auf einmal:

```bash
gac auth
```

## Fehlerbehebung

### Token abgelaufen

Wenn Sie Authentifizierungsfehler sehen, ist Ihr Token möglicherweise abgelaufen. Authentifizieren Sie sich erneut, indem Sie Folgendes ausführen:

```bash
gac auth chatgpt login
```

Ihr Browser wird automatisch für eine neue OAuth-Authentifizierung geöffnet. GAC verwendet automatisch Aktualisierungs-Tokens, um den Zugriff ohne erneute Authentifizierung zu erneuern, wenn dies möglich ist.

### Authentifizierungsstatus überprüfen

Um zu überprüfen, ob Sie derzeit authentifiziert sind:

```bash
gac auth chatgpt status
```

Oder überprüfen Sie alle Anbieter auf einmal:

```bash
gac auth
```

### Abmelden

So entfernen Sie Ihren gespeicherten Token:

```bash
gac auth chatgpt logout
```

### «ChatGPT OAuth-Token nicht gefunden»

Dies bedeutet, dass GAC Ihren Zugriffstoken nicht finden kann. Authentifizieren Sie sich, indem Sie Folgendes ausführen:

```bash
gac model
```

Wählen Sie dann «ChatGPT OAuth» aus der Anbieterliste. Der OAuth-Flow wird automatisch gestartet.

### «Authentifizierung fehlgeschlagen»

Wenn die OAuth-Authentifizierung fehlschlägt:

1. Stellen Sie sicher, dass Sie ein aktives ChatGPT Plus- oder Pro-Abonnement haben
2. Überprüfen Sie, ob Ihr Browser korrekt geöffnet wird
3. Versuchen Sie einen anderen Browser, wenn die Probleme weiterhin bestehen
4. Überprüfen Sie die Netzwerkverbindung zu `auth.openai.com`
5. Überprüfen Sie, ob die Ports 1455-1465 für den lokalen Callback-Server verfügbar sind

### Port bereits verwendet

Der OAuth-Callback-Server versucht automatisch die Ports 1455-1465. Wenn alle Ports belegt sind:

```bash
# Unter macOS/Linux:
lsof -ti:1455-1465 | xargs kill -9

# Unter Windows (PowerShell):
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Führen Sie dann `gac auth chatgpt login` erneut aus.

## Unterschiede zum OpenAI-Anbieter

| Funktion          | OpenAI (`openai:`)               | ChatGPT OAuth (`chatgpt-oauth:`)                                      |
| ----------------- | -------------------------------- | --------------------------------------------------------------------- |
| Authentifizierung | API-Schlüssel (`OPENAI_API_KEY`) | OAuth (automatisierter Browser-Flow)                                  |
| Abrechnung        | Token-basierte API-Abrechnung    | Abonnementbasiert (ChatGPT Plus/Pro)                                  |
| Einrichtung       | Manuelle API-Schlüsseleingabe    | Automatischer OAuth über `gac init` oder `gac model`                  |
| Token-Verwaltung  | Langlebige API-Schlüssel         | OAuth-Tokens (automatische Aktualisierung mit Aktualisierungs-Tokens) |
| Modelle           | Alle OpenAI-Modelle              | Codex-optimierte Modelle                                              |

## Sicherheitshinweise

- **Committen Sie niemals Ihren Zugriffstoken** in die Versionskontrolle
- GAC speichert OAuth-Tokens in `~/.gac/oauth/chatgpt-oauth.json` (außerhalb Ihres Projektverzeichnisses)
- Der OAuth-Flow verwendet PKCE (Proof Key for Code Exchange) für erhöhte Sicherheit
- Der lokale Callback-Server läuft nur auf localhost (Ports 1455-1465)
- Aktualisierungs-Tokens werden verwendet, um den Zugriff automatisch ohne erneute Authentifizierung zu erneuern

## Siehe auch

- [Hauptdokumentation](USAGE.md)
- [Fehlerbehebungsanleitung](TROUBLESHOOTING.md)
- [Codex-Dokumentation von OpenAI](https://openai.com/codex)
