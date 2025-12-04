[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | **Deutsch** | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# Verwendung von Qwen.ai mit GAC

GAC unterstützt die Authentifizierung über Qwen.ai OAuth, sodass Sie Ihr Qwen.ai-Konto für die Generierung von Commit-Nachrichten verwenden können. Dies verwendet die OAuth-Gerätefluss-Authentifizierung für ein nahtloses Anmeldeerlebnis.

## Was ist Qwen.ai?

Qwen.ai ist die KI-Plattform von Alibaba Cloud, die Zugriff auf die Qwen-Familie großer Sprachmodelle bietet. GAC unterstützt die OAuth-basierte Authentifizierung, sodass Sie Ihr Qwen.ai-Konto verwenden können, ohne API-Schlüssel manuell verwalten zu müssen.

## Vorteile

- **Einfache Authentifizierung**: OAuth-Gerätefluss – melden Sie sich einfach mit Ihrem Browser an
- **Keine API-Schlüsselverwaltung**: Die Authentifizierung wird automatisch abgewickelt
- **Zugriff auf Qwen-Modelle**: Verwenden Sie leistungsstarke Qwen-Modelle für die Generierung von Commit-Nachrichten

## Einrichtung

GAC enthält eine integrierte OAuth-Authentifizierung für Qwen.ai unter Verwendung des Geräteflusses. Der Einrichtungsprozess zeigt einen Code an und öffnet Ihren Browser zur Authentifizierung.

### Option 1: Während der Ersteinrichtung (Empfohlen)

Wählen Sie beim Ausführen von `gac init` einfach "Qwen.ai (OAuth)" als Ihren Anbieter aus:

```bash
gac init
```

Der Assistent wird:

1. Sie bitten, "Qwen.ai (OAuth)" aus der Anbieterliste auszuwählen
2. Einen Gerätecode anzeigen und Ihren Browser öffnen
3. Sie authentifizieren sich bei Qwen.ai und geben den Code ein
4. Ihr Zugriffstoken sicher speichern
5. Das Standardmodell festlegen

### Option 2: Später zu Qwen.ai wechseln

Wenn Sie GAC bereits mit einem anderen Anbieter konfiguriert haben und zu Qwen.ai wechseln möchten:

```bash
gac model
```

Dann:

1. Wählen Sie "Qwen.ai (OAuth)" aus der Anbieterliste
2. Folgen Sie dem Gerätecode-Authentifizierungsfluss
3. Token sicher in `~/.gac/oauth/qwen.json` gespeichert
4. Modell automatisch konfiguriert

### Option 3: Direkte Anmeldung

Sie können sich auch direkt authentifizieren mit:

```bash
gac auth qwen login
```

Dies wird:

1. Einen Gerätecode anzeigen
2. Ihren Browser auf der Qwen.ai-Authentifizierungsseite öffnen
3. Nachdem Sie sich authentifiziert haben, wird das Token automatisch gespeichert

### GAC normal verwenden

Sobald Sie authentifiziert sind, verwenden Sie GAC wie gewohnt:

```bash
# Ihre Änderungen stagen
git add .

# Generieren und committen mit Qwen.ai
gac

# Oder das Modell für einen einzelnen Commit überschreiben
gac -m qwen:qwen3-coder-plus
```

## Verfügbare Modelle

Die Qwen.ai OAuth-Integration verwendet:

- `qwen3-coder-plus` – Optimiert für Codierungsaufgaben (Standard)

Dies ist das Modell, das über den portal.qwen.ai OAuth-Endpunkt verfügbar ist. Für andere Qwen-Modelle sollten Sie den OpenRouter-Anbieter in Betracht ziehen, der zusätzliche Qwen-Modelloptionen bietet.

## Authentifizierungsbefehle

GAC bietet mehrere Befehle zur Verwaltung der Qwen.ai-Authentifizierung:

```bash
# Bei Qwen.ai anmelden
gac auth qwen login

# Authentifizierungsstatus prüfen
gac auth qwen status

# Abmelden und gespeichertes Token entfernen
gac auth qwen logout

# Status aller OAuth-Anbieter prüfen
gac auth
```

### Anmeldeoptionen

```bash
# Standardanmeldung (öffnet Browser automatisch)
gac auth qwen login

# Anmeldung ohne Browseröffnung (zeigt URL zum manuellen Besuch an)
gac auth qwen login --no-browser

# Stiller Modus (minimale Ausgabe)
gac auth qwen login --quiet
```

## Fehlerbehebung

### Token abgelaufen

Wenn Sie Authentifizierungsfehler sehen, ist Ihr Token möglicherweise abgelaufen. Authentifizieren Sie sich erneut, indem Sie Folgendes ausführen:

```bash
gac auth qwen login
```

Der Gerätecodefluss beginnt und Ihr Browser öffnet sich zur erneuten Authentifizierung.

### Authentifizierungsstatus prüfen

Um zu überprüfen, ob Sie derzeit authentifiziert sind:

```bash
gac auth qwen status
```

Oder überprüfen Sie alle Anbieter auf einmal:

```bash
gac auth
```

### Abmelden

Um Ihr gespeichertes Token zu entfernen:

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (Qwen-Authentifizierung nicht gefunden)

Dies bedeutet, dass GAC Ihr Zugriffstoken nicht finden kann. Authentifizieren Sie sich, indem Sie Folgendes ausführen:

```bash
gac auth qwen login
```

Oder führen Sie `gac model` aus und wählen Sie "Qwen.ai (OAuth)" aus der Anbieterliste.

### "Authentication failed" (Authentifizierung fehlgeschlagen)

Wenn die OAuth-Authentifizierung fehlschlägt:

1. Stellen Sie sicher, dass Sie ein Qwen.ai-Konto haben
2. Überprüfen Sie, ob sich Ihr Browser korrekt öffnet
3. Überprüfen Sie, ob Sie den Gerätecode korrekt eingegeben haben
4. Versuchen Sie einen anderen Browser, wenn die Probleme bestehen bleiben
5. Überprüfen Sie die Netzwerkverbindung zu `qwen.ai`

### Gerätecode funktioniert nicht

Wenn die Gerätecode-Authentifizierung nicht funktioniert:

1. Stellen Sie sicher, dass der Code nicht abgelaufen ist (Codes sind für eine begrenzte Zeit gültig)
2. Versuchen Sie, `gac auth qwen login` erneut auszuführen, um einen neuen Code zu erhalten
3. Verwenden Sie das Flag `--no-browser` und besuchen Sie die URL manuell, wenn das Öffnen des Browsers fehlschlägt

## Sicherheitshinweise

- **Committen Sie niemals Ihr Zugriffstoken** in die Versionskontrolle
- GAC speichert Token automatisch in `~/.gac/oauth/qwen.json` (außerhalb Ihres Projektverzeichnisses)
- Token-Dateien haben eingeschränkte Berechtigungen (nur vom Eigentümer lesbar)
- Token können ablaufen und erfordern eine erneute Authentifizierung
- Der OAuth-Gerätefluss ist für die sichere Authentifizierung auf Headless-Systemen konzipiert

## Siehe auch

- [Hauptdokumentation](USAGE.md)
- [Claude Code-Einrichtung](CLAUDE_CODE.md)
- [Fehlerbehebungshandbuch](TROUBLESHOOTING.md)
- [Qwen.ai-Dokumentation](https://qwen.ai)
