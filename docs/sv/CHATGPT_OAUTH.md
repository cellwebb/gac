# Använda ChatGPT OAuth med GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC stöder autentisering via ChatGPT OAuth, vilket gör att du kan använda ditt ChatGPT-abonnemang för att få tillgång till OpenAI:s Codex API istället för att betala för OpenAI API-nycklar separat. Detta speglar samma OAuth-flöde som används av OpenAI:s Codex CLI.

> ⚠️ **Observera — ej godkänd användning:** Detta använder samma OAuth-flöde som OpenAI:s Codex CLI, och även om det för närvarande fungerar, kan OpenAI när som helst begränsa tredjeparts tokenanvändning. GAC är litet nog att det har flugit under radarn hittills, men användning av ChatGPT OAuth här är **inte officiellt godkänt** för tredjepartsverktyg och kan sluta fungera när som helst. Om du behöver tillförlitlig generering av commit-meddelanden, använd en direkt API-leverantör (`openai` etc.). Se [OpenAI:s Codex-dokumentation](https://openai.com/codex) för gällande policy.

## Vad är ChatGPT OAuth?

ChatGPT OAuth låter dig utnyttja ditt befintliga ChatGPT Plus- eller Pro-abonnemang för att få tillgång till Codex API för att generera commit-meddelanden. Istället för att hantera API-nycklar och tokenbaserad fakturering autentiserar du dig en gång via din webbläsare och GAC hanterar tokenens livscykel automatiskt.

## Fördelar

- **Kostnadseffektivt**: Använd ditt befintliga ChatGPT Plus/Pro-abonnemang istället för att betala separat för API-åtkomst
- **Samma modeller**: Få tillgång till Codex-optimerade modeller (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **Ingen API-nyckelhantering**: Webbläsarbaserad OAuth innebär att det inte finns några API-nycklar att rotera eller lagra
- **Separat fakturering**: ChatGPT OAuth-användning är separat från direkt OpenAI API-fakturering

## Konfiguration

GAC inkluderar inbyggd OAuth-autentisering för ChatGPT. Konfigurationsprocessen är helt automatiserad och öppnar din webbläsare för autentisering.

### Alternativ 1: Under första konfigurationen (Rekommenderas)

När du kör `gac init`, välj helt enkelt «ChatGPT OAuth» som din leverantör:

```bash
gac init
```

Guiden kommer att:

1. Be dig att välja «ChatGPT OAuth» från leverantörslistan
2. Automatiskt öppna din webbläsare för OAuth-autentisering
3. Spara din åtkomsttoken i `~/.gac/oauth/chatgpt-oauth.json`
4. Ställa in standardmodellen

### Alternativ 2: Byt till ChatGPT OAuth senare

Om du redan har konfigurerat GAC med en annan leverantör och vill byta till ChatGPT OAuth:

```bash
gac model
```

Sedan:

1. Välj «ChatGPT OAuth» från leverantörslistan
2. Din webbläsare öppnas automatiskt för OAuth-autentisering
3. Token sparad i `~/.gac/oauth/chatgpt-oauth.json`
4. Modell konfigurerad automatiskt

### Använd GAC som vanligt

När du är autentiserad, använd GAC som vanligt:

```bash
# Staga dina ändringar
git add .

# Generera och commit:a med ChatGPT OAuth
gac

# Eller åsidosätt modellen för en enda commit
gac -m chatgpt-oauth:gpt-5.5
```

## Tillgängliga modeller

ChatGPT OAuth ger tillgång till Codex-optimerade modeller. Nuvarande modeller inkluderar:

- `gpt-5.5` — Senaste och mest kraftfulla Codex-modellen
- `gpt-5.4` — Föregående generations Codex-modell
- `gpt-5.3-codex` — Tredje generationens Codex-modell

Kontrollera [OpenAI-dokumentationen](https://platform.openai.com/docs/models) för fullständig lista över tillgängliga modeller.

## CLI-kommandon

GAC tillhandahåller dedikerade CLI-kommandon för ChatGPT OAuth-hantering:

### Logga in

Autentisera eller autentisera om med ChatGPT OAuth:

```bash
gac auth chatgpt login
```

Din webbläsare öppnas automatiskt för att slutföra OAuth-flödet. Om du redan är autentiserad kommer detta att uppdatera dina tokens.

### Logga ut

Ta bort lagrade ChatGPT OAuth-tokens:

```bash
gac auth chatgpt logout
```

Detta tar bort den lagrade tokenfilen på `~/.gac/oauth/chatgpt-oauth.json`.

### Status

Kontrollera din nuvarande ChatGPT OAuth-autentiseringsstatus:

```bash
gac auth chatgpt status
```

Eller kontrollera alla leverantörer på en gång:

```bash
gac auth
```

## Felsökning

### Token utgången

Om du ser autentiseringsfel kan din token ha löpt ut. Autentisera om genom att köra:

```bash
gac auth chatgpt login
```

Din webbläsare öppnas automatiskt för ny OAuth-autentisering. GAC använder automatiskt uppdateringstokens för att förnya åtkomst utan autentisering om när det är möjligt.

### Kontrollera autentiseringsstatus

För att kontrollera om du för närvarande är autentiserad:

```bash
gac auth chatgpt status
```

Eller kontrollera alla leverantörer på en gång:

```bash
gac auth
```

### Logga ut

För att ta bort din lagrade token:

```bash
gac auth chatgpt logout
```

### «ChatGPT OAuth-token hittades inte»

Detta betyder att GAC inte kan hitta din åtkomsttoken. Autentisera genom att köra:

```bash
gac model
```

Välj sedan «ChatGPT OAuth» från leverantörslistan. OAuth-flödet startar automatiskt.

### «Autentisering misslyckades»

Om OAuth-autentisering misslyckas:

1. Se till att du har ett aktivt ChatGPT Plus- eller Pro-abonnemang
2. Kontrollera att din webbläsare öppnas korrekt
3. Prova en annan webbläsare om problemen kvarstår
   4.Verifiera nätverksanslutning till `auth.openai.com`
4. Kontrollera att portarna 1455-1465 är tillgängliga för den lokala callback-servern

### Port redan upptagen

OAuth-callback-servern försöker automatiskt portarna 1455-1465. Om alla portar är upptagna:

```bash
# På macOS/Linux:
lsof -ti:1455-1465 | xargs kill -9

# På Windows (PowerShell):
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Kör sedan `gac auth chatgpt login` igen.

## Skillnader från OpenAI-leverantören

| Funktion       | OpenAI (`openai:`)            | ChatGPT OAuth (`chatgpt-oauth:`)                             |
| -------------- | ----------------------------- | ------------------------------------------------------------ |
| Autentisering  | API-nyckel (`OPENAI_API_KEY`) | OAuth (automatiserat webbläsarflöde)                         |
| Fakturering    | Tokenbaserad API-fakturering  | Abonnemangsbaserat (ChatGPT Plus/Pro)                        |
| Konfiguration  | Manuell API-nyckelinmatning   | Automatisk OAuth via `gac init` eller `gac model`            |
| Tokenhantering | Långlivade API-nycklar        | OAuth-tokens (automatisk uppdatering med uppdateringstokens) |
| Modeller       | Alla OpenAI-modeller          | Codex-optimerade modeller                                    |

## Säkerhetsanteckningar

- **Commit:a aldrig din åtkomsttoken** till versionskontroll
- GAC lagrar OAuth-tokens i `~/.gac/oauth/chatgpt-oauth.json` (utanför din projektkatalog)
- OAuth-flödet använder PKCE (Proof Key for Code Exchange) för ökad säkerhet
- Lokal callback-server körs endast på localhost (portar 1455-1465)
- Uppdateringstokens används för att automatiskt förnya åtkomst utan autentisering om

## Se även

- [Huvuddokumentation](USAGE.md)
- [Felsökningsguide](TROUBLESHOOTING.md)
- [OpenAI:s Codex-dokumentation](https://openai.com/codex)
