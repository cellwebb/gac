# Använda Claude Code med GAC

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | **Svenska** | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC stöder autentisering via Claude Code-abonnemang, vilket låter dig använda ditt Claude Code-abonnemang istället för att betala för den dyra Anthropic API:en. Detta är perfekt för användare som redan har tillgång till Claude Code via sitt abonnemang.

## Vad är Claude Code?

Claude Code är Anthropics prenumerationstjänst som tillhandahåller OAuth-baserad åtkomst till Claude-modeller. Istället för att använda API-nycklar (som faktureras per token) använder Claude Code OAuth-tokens från ditt abonnemang.

## Fördelar

- **Kostnadseffektivt**: Använd ditt befintliga Claude Code-abonnemang istället för att betala separat för API-åtkomst
- **Samma modeller**: Åtkomst till samma Claude-modeller (t.ex. `claude-sonnet-4-5`)
- **Separater fakturering**: Claude Code-användning är separerad från Anthropic API-fakturering

## Konfiguration

GAC inkluderar inbyggd OAuth-autentisering för Claude Code. Konfigureringsprocessen är helt automatiserad och kommer att öppna din webbläsare för autentisering.

### Alternativ 1: Under initial konfiguration (Rekommenderas)

När du kör `gac init`, välj helt enkelt "Claude Code" som din leverantör:

```bash
gac init
```

Guiden kommer att:

1. Be dig välja "Claude Code" från leverantörslistan
2. Automatiskt öppna din webbläsare för OAuth-autentisering
3. Spara din åtkomsttoken i `~/.gac.env`
4. Ställa in standardmodellen

### Alternativ 2: Byt till Claude Code senare

Om du redan har konfigurerat GAC med en annan leverantör och vill byta till Claude Code:

```bash
gac model
```

Sedan:

1. Välj "Claude Code" från leverantörslistan
2. Din webbläsare öppnas automatiskt för OAuth-autentisering
3. Token sparad i `~/.gac.env`
4. Modell konfigurerad automatiskt

### Använd GAC normalt

När du är autentiserad, använd GAC som vanligt:

```bash
# Stage dina ändringar
git add .

# Generera och committa med Claude Code
gac

# Eller åsidosätt modellen för ett enskilt commit
gac -m claude-code:claude-sonnet-4-5
```

## Tillgängliga modeller

Claude Code ger tillgång till samma modeller som Anthropic API:en. Nuvarande Claude 4.5-familjmodeller inkluderar:

- `claude-sonnet-4-5` - Senaste och mest intelligenta Sonnet-modellen, bäst för kodning
- `claude-haiku-4-5` - Snabb och effektiv
- `claude-opus-4-5` - Mest kapabla modellen för komplex resonemang

Se [Claude-dokumentationen](https://docs.claude.com/en/docs/about-claude/models/overview) för fullständig lista över tillgängliga modeller.

## Felsökning

### Token har utgått

Om du ser autentiseringsfel kan din token ha löpt ut. Autentisera igen genom att köra:

```bash
gac auth claude-code login
```

Din webbläsare öppnas automatiskt för ny OAuth-autentisering. Alternativt kan du köra `gac model`, välja "Claude Code (OAuth)" och välja "Autentisera igen (få ny token)".

### Kontrollera autentiseringsstatus

För att kontrollera om du är autentiserad för tillfället:

```bash
gac auth claude-code status
```

Eller kontrollera alla leverantörer samtidigt:

```bash
gac auth
```

### Logga ut

För att ta bort din sparade token:

```bash
gac auth claude-code logout
```

### "CLAUDE_CODE_ACCESS_TOKEN hittades inte"

Detta betyder att GAC inte hittar din åtkomsttoken. Autentisera genom att köra:

```bash
gac model
```

Välj sedan "Claude Code" från leverantörslistan. OAuth-flödet kommer att starta automatiskt.

### "Autentisering misslyckades"

Om OAuth-autentisering misslyckas:

1. Se till att du har ett aktivt Claude Code-abonnemang
2. Kontrollera att din webbläsare öppnas korrekt
3. Prova en annan webbläsare om problemen kvarstår
4. Verifiera nätverksanslutning till `claude.ai`
5. Kontrollera att portar 8765-8795 är tillgängliga för lokal callback-server

## Skillnader från Anthropic-leverantör

| Funktion        | Anthropic (`anthropic:`)         | Claude Code (`claude-code:`)                                 |
| --------------- | -------------------------------- | ------------------------------------------------------------ |
| Autentisering   | API-nyckel (`ANTHROPIC_API_KEY`) | OAuth (automatisk webbläsarflöde)                            |
| Fakturering     | Per-token API-fakturering        | Prenumerationsbaserat                                        |
| Konfiguration   | Manuell API-nyckelinmatning      | Automatisk OAuth via `gac init` eller `gac model`            |
| Token-hantering | Långlivade API-nycklar           | OAuth-tokens (kan utgå, enkel återautentisering via `model`) |
| Modeller        | Samma modeller                   | Samma modeller                                               |

## Säkerhetsnoteringar

- **Committa aldrig din åtkomsttoken** till versionskontroll
- GAC lagrar automatiskt tokens i `~/.gac.env` (utanför din projektkatalog)
- Tokens kan utgå och kommer att kräva återautentisering via `gac model`
- OAuth-flödet använder PKCE (Proof Key for Code Exchange) för förbättrad säkerhet
- Lokal callback-server körs endast på localhost (portar 8765-8795)

## Se även

- [Huvuddokumentation](USAGE.md)
- [Qwen.ai-installation och autentisering](QWEN.md)
- [Felsökningsguide](TROUBLESHOOTING.md)
- [Claude Code-dokumentation](https://claude.ai/code)
