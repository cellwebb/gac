# Använda GitHub Copilot med GAC

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | **Svenska** | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC stöder autentisering via GitHub Copilot, vilket gör att du kan använda ditt Copilot-abonnemang för att få tillgång till modeller från OpenAI, Anthropic, Google och mer — allt inkluderat i ditt GitHub Copilot-abonnemang.

## Vad är GitHub Copilot OAuth?

GitHub Copilot OAuth använder **Device Flow** — en säker, webbläsarbaserad autentiseringsmetod som inte kräver en lokal callback-server. Du besöker en URL, anger en engångskod och auktoriserar GAC att använda din Copilot-åtkomst. Bakom kulisserna byter GAC din långlivade GitHub OAuth-token mot kortlivade Copilot-sessionstokens (~30 min) som ger åtkomst till Copilot API.

Detta ger dig tillgång till modeller från flera leverantörer genom ett enda abonnemang:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Fördelar

- **Flerleverantörsåtkomst**: Använd modeller från OpenAI, Anthropic och Google genom ett enda abonnemang
- **Kostnadseffektivt**: Använd ditt befintliga Copilot-abonnemang istället för att betala för separata API-nycklar
- **Ingen API-nyckelhantering**: Device Flow-autentisering — inga nycklar att rotera eller lagra
- **GitHub Enterprise-stöd**: Fungerar med GHE-instanser via `--host` flaggan

## Konfiguration

### Alternativ 1: Under första konfigurationen (Rekommenderas)

När du kör `gac init`, välj helt enkelt «Copilot» som din leverantör:

```bash
gac init
```

Guiden kommer att:

1. Be dig att välja «Copilot» från leverantörslistan
2. Visa en engångskod och öppna din webbläsare för Device Flow-autentisering
3. Spara din OAuth-token i `~/.gac/oauth/copilot.json`
4. Ställa in standardmodellen

### Alternativ 2: Byt till Copilot senare

Om du redan har konfigurerat GAC med en annan leverantör:

```bash
gac model
```

Välj sedan «Copilot» från leverantörslistan och autentisera.

### Alternativ 3: Direkt inloggning

Autentisera direkt utan att ändra din standardmodell:

```bash
gac auth copilot login
```

### Använd GAC som vanligt

När du är autentiserad, använd GAC som vanligt:

```bash
# Staga dina ändringar
git add .

# Generera och commit:a med Copilot
gac

# Eller åsidosätt modellen för en enda commit
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Tillgängliga modeller

Copilot ger tillgång till modeller från flera leverantörer. Nuvarande modeller inkluderar:

| Leverantör | Modeller                                                                                       |
| ---------- | ---------------------------------------------------------------------------------------------- |
| OpenAI     | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic  | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google     | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Obs:** Modellanvisningen som visas efter inloggning är informativ och kan bli inaktuell allt eftersom GitHub lägger till nya modeller. Kontrollera [GitHub Copilot-dokumentationen](https://docs.github.com/en/copilot) för de senaste tillgängliga modellerna.

## GitHub Enterprise

För att autentisera med en GitHub Enterprise-instans:

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC använder automatiskt rätt Device Flow- och API-ändpunkter för din GHE-instans. Sessionstoken cachelagras per värd, så olika GHE-instanser hanteras oberoende.

## CLI-kommandon

GAC tillhandahåller dedikerade CLI-kommandon för Copilot-autentiseringshantering:

### Logga in

Autentisera eller autentisera om med GitHub Copilot:

```bash
gac auth copilot login
```

Din webbläsare öppnas till en Device Flow-sida där du anger en engångskod. Om du redan är autentiserad kommer du att bli tillfrågad om du vill autentisera om.

För GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Logga ut

Ta bort lagrade Copilot-tokens:

```bash
gac auth copilot logout
```

Detta tar bort den lagrade tokenfilen på `~/.gac/oauth/copilot.json` och sessionens cache.

### Status

Kontrollera din nuvarande Copilot-autentiseringsstatus:

```bash
gac auth copilot status
```

Eller kontrollera alla leverantörer på en gång:

```bash
gac auth
```

## Hur det fungerar

Copilot-autentiseringsflödet skiljer sig från ChatGPT och Claude Code OAuth:

1. **Device Flow** — GAC begär en enhetskod från GitHub och visar den
2. **Webbläsarauktorisering** — Du besöker URL:en och anger koden
3. **Tokenpollning** — GAC pollar GitHub tills du slutför auktoriseringen
4. **Sessionstokenutbyte** — GitHub OAuth-token byts mot en kortlivad Copilot-sessionstoken
5. **Autouppdatering** — Sessionstokens (~30 min) uppdateras automatiskt från den cachade OAuth-tokenen

Till skillnad från PKCE-baserad OAuth (ChatGPT/Claude Code) kräver inte Device Flow en lokal callback-server eller portshantering.

## Felsökning

### «Copilot-autentisering hittades inte»

Kör inloggningskommandot för att autentisera:

```bash
gac auth copilot login
```

### «Kunde inte hämta Copilot-sessionstoken»

Detta betyder att GAC fick en GitHub OAuth-token men inte kunde byta den mot en Copilot-sessionstoken. Vanligtvis betyder detta:

1. **Inget Copilot-abonnemang** — Ditt GitHub-konto har inget aktivt Copilot-abonnemang
2. **Token återkallad** — OAuth-token återkallades; autentisera om med `gac auth copilot login`

### Sessionstoken utgången

Sessionstokens löper ut efter ca 30 minuter. GAC uppdaterar dem automatiskt från den cachade OAuth-tokenen, så du bör inte behöva autentisera om ofta. Om autouppdatering misslyckas:

```bash
gac auth copilot login
```

### «Ogiltigt eller osäkert värdnamn»

Flaggan `--host` validerar värdnamn strikt för att förhindra SSRF-attacker. Om du ser detta fel:

- Se till att värdnamnet inte inkluderar portar (t.ex., använd `ghe.company.com` inte `ghe.company.com:8080`)
- Inkludera inte protokoll eller sökvägar (t.ex., använd `ghe.company.com` inte `https://ghe.company.com/api`)
- Privata IP-adresser och `localhost` är blockerade av säkerhetsskäl

### GitHub Enterprise-problem

Om GHE-autentisering misslyckas:

1. Verifiera att din GHE-instans har Copilot aktiverat
2. Kontrollera att ditt GHE-värdnamn är tillgängligt från din maskin
3. Se till att ditt GHE-konto har en Copilot-licens
4. Försök med `--host` flaggan explicit: `gac auth copilot login --host ghe.mycompany.com`

## Skillnader från andra OAuth-leverantörer

| Funktion            | ChatGPT OAuth                | Claude Code               | Copilot                                      |
| ------------------- | ---------------------------- | ------------------------- | -------------------------------------------- |
| Autentiseringsmetod | PKCE (webbläsarcallback)     | PKCE (webbläsarcallback)  | Device Flow (engångskod)                     |
| Callback-server     | Portar 1455-1465             | Portar 8765-8795          | Behövs inte                                  |
| Tokenlivstid        | Långlivade (autouppdatering) | Utgående (autentisera om) | Session ~30 min (autouppdatering)            |
| Modeller            | Codex-optimerade OpenAI      | Claude-familjen           | Flerleverantör (OpenAI + Anthropic + Google) |
| GHE-stöd            | Nej                          | Nej                       | Ja (`--host` flaggan)                        |

## Säkerhetsanteckningar

- **Commit:a aldrig din OAuth-token** till versionskontroll
- GAC lagrar OAuth-tokens i `~/.gac/oauth/copilot.json` (utanför din projektkatalog)
- Sessionstokens cachelagras i `~/.gac/oauth/copilot_session.json` med `0o600` behörigheter
- Värdnamn valideras strikt för att förhindra SSRF- och URL-injektionsattacker
- Privata IP-adresser, loopback-adresser och `localhost` är blockerade som värdnamn
- Device Flow exponerar inga lokala portar, vilket minskar angreppsytan

## Se även

- [Huvuddokumentation](USAGE.md)
- [Felsökningsguide](TROUBLESHOOTING.md)
- [ChatGPT OAuth-guide](CHATGPT_OAUTH.md)
- [Claude Code-guide](CLAUDE_CODE.md)
- [GitHub Copilot-dokumentation](https://docs.github.com/en/copilot)
