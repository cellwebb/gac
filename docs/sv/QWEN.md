[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | **Svenska** | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# Använda Qwen.ai med GAC

GAC stöder autentisering via Qwen.ai OAuth, vilket gör att du kan använda ditt Qwen.ai-konto för generering av commit-meddelanden. Detta använder OAuth-enhetsflödesautentisering för en sömlös inloggningsupplevelse.

## Vad är Qwen.ai?

Qwen.ai är Alibaba Clouds AI-plattform som ger tillgång till Qwen-familjen av stora språkmodeller. GAC stöder OAuth-baserad autentisering, vilket gör att du kan använda ditt Qwen.ai-konto utan att behöva hantera API-nycklar manuellt.

## Fördelar

- **Enkel autentisering**: OAuth-enhetsflöde - logga bara in med din webbläsare
- **Ingen API-nyckelhantering**: Autentisering hanteras automatiskt
- **Tillgång till Qwen-modeller**: Använd kraftfulla Qwen-modeller för generering av commit-meddelanden

## Installation

GAC inkluderar inbyggd OAuth-autentisering för Qwen.ai med hjälp av enhetsflödet. Installationsprocessen visar en kod och öppnar din webbläsare för autentisering.

### Alternativ 1: Under första installationen (Rekommenderas)

När du kör `gac init`, välj helt enkelt "Qwen.ai (OAuth)" som din leverantör:

```bash
gac init
```

Guiden kommer att:

1. Be dig välja "Qwen.ai (OAuth)" från leverantörslistan
2. Visa en enhetskod och öppna din webbläsare
3. Du autentiserar på Qwen.ai och anger koden
4. Spara din åtkomsttoken säkert
5. Ställa in standardmodellen

### Alternativ 2: Byt till Qwen.ai senare

Om du redan har konfigurerat GAC med en annan leverantör och vill byta till Qwen.ai:

```bash
gac model
```

Sedan:

1. Välj "Qwen.ai (OAuth)" från leverantörslistan
2. Följ autentiseringsflödet för enhetskod
3. Token sparas säkert till `~/.gac/oauth/qwen.json`
4. Modellen konfigureras automatiskt

### Alternativ 3: Direkt inloggning

Du kan också autentisera direkt med:

```bash
gac auth qwen login
```

Detta kommer att:

1. Visa en enhetskod
2. Öppna din webbläsare till Qwen.ai-autentiseringssidan
3. Efter att du har autentiserat sparas token automatiskt

### Använd GAC normalt

När du är autentiserad, använd GAC som vanligt:

```bash
# Staga dina ändringar
git add .

# Generera och committa med Qwen.ai
gac

# Eller åsidosätt modellen för en enda commit
gac -m qwen:qwen3-coder-plus
```

## Tillgängliga modeller

Qwen.ai OAuth-integrationen använder:

- `qwen3-coder-plus` - Optimerad för kodningsuppgifter (standard)

Detta är modellen som är tillgänglig via portal.qwen.ai OAuth-slutpunkten. För andra Qwen-modeller, överväg att använda OpenRouter-leverantören som erbjuder ytterligare Qwen-modellalternativ.

## Autentiseringskommandon

GAC tillhandahåller flera kommandon för att hantera Qwen.ai-autentisering:

```bash
# Logga in på Qwen.ai
gac auth qwen login

# Kontrollera autentiseringsstatus
gac auth qwen status

# Logga ut och ta bort lagrad token
gac auth qwen logout

# Kontrollera status för alla OAuth-leverantörer
gac auth
```

### Inloggningsalternativ

```bash
# Standardinloggning (öppnar webbläsare automatiskt)
gac auth qwen login

# Logga in utan att öppna webbläsare (visar URL att besöka manuellt)
gac auth qwen login --no-browser

# Tyst läge (minimal utdata)
gac auth qwen login --quiet
```

## Felsökning

### Token utgången

Om du ser autentiseringsfel kan din token ha gått ut. Återautentisera genom att köra:

```bash
gac auth qwen login
```

Enhetskodsflödet startar och din webbläsare öppnas för återautentisering.

### Kontrollera autentiseringsstatus

För att kontrollera om du för närvarande är autentiserad:

```bash
gac auth qwen status
```

Eller kontrollera alla leverantörer samtidigt:

```bash
gac auth
```

### Logga ut

För att ta bort din lagrade token:

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (Qwen-autentisering hittades inte)

Detta innebär att GAC inte kan hitta din åtkomsttoken. Autentisera genom att köra:

```bash
gac auth qwen login
```

Eller kör `gac model` och välj "Qwen.ai (OAuth)" från leverantörslistan.

### "Authentication failed" (Autentisering misslyckades)

Om OAuth-autentisering misslyckas:

1. Se till att du har ett Qwen.ai-konto
2. Kontrollera att din webbläsare öppnas korrekt
3. Verifiera att du angav enhetskoden korrekt
4. Prova en annan webbläsare om problemen kvarstår
5. Verifiera nätverksanslutning till `qwen.ai`

### Enhetskod fungerar inte

Om autentisering med enhetskod inte fungerar:

1. Se till att koden inte har gått ut (koder är giltiga under en begränsad tid)
2. Försök köra `gac auth qwen login` igen för en ny kod
3. Använd flaggan `--no-browser` och besök URL:en manuellt om öppning av webbläsare misslyckas

## Säkerhetsanmärkningar

- **Committa aldrig din åtkomsttoken** till versionskontroll
- GAC lagrar automatiskt tokens i `~/.gac/oauth/qwen.json` (utanför din projektkatalog)
- Tokenfiler har begränsade behörigheter (endast läsbara av ägare)
- Tokens kan gå ut och kommer att kräva återautentisering
- OAuth-enhetsflödet är utformat för säker autentisering på headless-system

## Se även

- [Huvuddokumentation](USAGE.md)
- [Claude Code-installation](CLAUDE_CODE.md)
- [Felsökningsguide](TROUBLESHOOTING.md)
- [Qwen.ai-dokumentation](https://qwen.ai)
