# Claude Code mit GAC verwenden

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | **Deutsch** | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC unterstützt die Authentifizierung über Claude Code-Abonnements, sodass Sie Ihr Claude Code-Abonnement anstelle der Bezahlung für die teure Anthropic API verwenden können. Dies ist perfekt für Benutzer, die bereits über ihr Abonnement Zugriff auf Claude Code haben.

## Was ist Claude Code?

Claude Code ist der Abonnementdienst von Anthropic, der OAuth-basierten Zugriff auf Claude-Modelle bietet. Anstelle von API-Schlüsseln (die pro Token abgerechnet werden) verwendet Claude Code OAuth-Tokens aus Ihrem Abonnement.

## Vorteile

- **Kosteneffizient**: Nutzen Sie Ihr bestehendes Claude Code-Abonnement, anstatt separat für API-Zugriff zu zahlen
- **Gleiche Modelle**: Zugriff auf die gleichen Claude-Modelle (z.B. `claude-sonnet-4-5`)
- **Separate Abrechnung**: Claude Code-Nutzung ist von der Anthropic API-Abrechnung getrennt

## Einrichtung

GAC enthält integrierte OAuth-Authentifizierung für Claude Code. Der Einrichtungsprozess ist vollständig automatisiert und öffnet Ihren Browser zur Authentifizierung.

### Option 1: Während der Ersteinrichtung (Empfohlen)

Führen Sie `gac init` aus und wählen Sie einfach "Claude Code" als Ihren Anbieter:

```bash
gac init
```

Der Assistent wird:

1. Sie auffordern, "Claude Code" aus der Anbieterliste auszuwählen
2. Automatisch Ihren Browser zur OAuth-Authentifizierung öffnen
3. Ihren Zugriffstoken in `~/.gac.env` speichern
4. Das Standardmodell festlegen

### Option 2: Später zu Claude Code wechseln

Wenn Sie GAC bereits mit einem anderen Anbieter konfiguriert haben und zu Claude Code wechseln möchten:

```bash
gac model
```

Dann:

1. Wählen Sie "Claude Code" aus der Anbieterliste
2. Ihr Browser öffnet sich automatisch zur OAuth-Authentifizierung
3. Token in `~/.gac.env` gespeichert
4. Modell automatisch konfiguriert

### GAC normal verwenden

Nach der Authentifizierung verwenden Sie GAC wie gewohnt:

```bash
# Stagen Sie Ihre Änderungen
git add .

# Mit Claude Code generieren und committen
gac

# Oder überschreiben Sie das Modell für einen einzelnen Commit
gac -m claude-code:claude-sonnet-4-5
```

## Verfügbare Modelle

Claude Code bietet Zugriff auf die gleichen Modelle wie die Anthropic API. Aktuelle Claude 4.5-Familienmodelle umfassen:

- `claude-sonnet-4-5` - Neuestes und intelligentestes Sonnet-Modell, am besten für Codierung
- `claude-haiku-4-5` - Schnell und effizient
- `claude-opus-4-1` - Fähigstes Modell für komplexes Reasoning

Überprüfen Sie die [Claude-Dokumentation](https://docs.claude.com/en/docs/about-claude/models/overview) für die vollständige Liste der verfügbaren Modelle.

## Fehlerbehebung

### Token abgelaufen

Wenn Sie Authentifizierungsfehler sehen, ist Ihr Token möglicherweise abgelaufen. Reauthentifizieren Sie sich durch Ausführen von:

```bash
gac model
```

Wählen Sie dann "Claude Code" und wählen Sie "Reauthentifizieren (neuen Token erhalten)". Ihr Browser öffnet sich für neue OAuth-Authentifizierung.

### "CLAUDE_CODE_ACCESS_TOKEN nicht gefunden"

Dies bedeutet, dass GAC Ihren Zugriffstoken nicht finden kann. Authentifizieren Sie sich durch Ausführen von:

```bash
gac model
```

Wählen Sie dann "Claude Code" aus der Anbieterliste. Der OAuth-Flow startet automatisch.

### "Authentifizierung fehlgeschlagen"

Wenn die OAuth-Authentifizierung fehlschlägt:

1. Stellen Sie sicher, dass Sie ein aktives Claude Code-Abonnement haben
2. Überprüfen Sie, ob Ihr Browser korrekt öffnet
3. Versuchen Sie einen anderen Browser, wenn Probleme bestehen
4. Überprüfen Sie die Netzwerkverbindung zu `claude.ai`
5. Überprüfen Sie, ob die Ports 8765-8795 für den lokalen Callback-Server verfügbar sind

## Unterschiede zum Anthropic-Anbieter

| Funktion          | Anthropic (`anthropic:`)            | Claude Code (`claude-code:`)                                              |
| ----------------- | ----------------------------------- | ------------------------------------------------------------------------- |
| Authentifizierung | API-Schlüssel (`ANTHROPIC_API_KEY`) | OAuth (automatischer Browser-Flow)                                        |
| Abrechnung        | Pro-Token API-Abrechnung            | Abonnementsbasiert                                                        |
| Einrichtung       | Manuelle API-Schlüsseleingabe       | Automatisches OAuth über `gac init` oder `gac model`                      |
| Token-Verwaltung  | Langlebige API-Schlüssel            | OAuth-Tokens (können ablaufen, einfache Reauthentifizierung über `model`) |
| Modelle           | Gleiche Modelle                     | Gleiche Modelle                                                           |

## Sicherheitshinweise

- **Committen Sie niemals Ihren Zugriffstoken** in die Versionskontrolle
- GAC speichert Tokens automatisch in `~/.gac.env` (außerhalb Ihres Projektverzeichnisses)
- Tokens können ablaufen und erfordern Reauthentifizierung über `gac model`
- Der OAuth-Flow verwendet PKCE (Proof Key for Code Exchange) für erhöhte Sicherheit
- Der lokale Callback-Server läuft nur auf localhost (Ports 8765-8795)

## Siehe auch

- [Hauptdokumentation](USAGE.md)
- [Fehlerbehebungsleitfaden](TROUBLESHOOTING.md)
- [Claude Code-Dokumentation](https://claude.ai/code)
