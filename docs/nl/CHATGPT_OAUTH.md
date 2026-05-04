# ChatGPT OAuth gebruiken met GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC ondersteunt authenticatie via ChatGPT OAuth, waardoor u uw ChatGPT-abonnement kunt gebruiken om toegang te krijgen tot de Codex API van OpenAI in plaats van apart te betalen voor OpenAI API-sleutels. Dit weerspiegelt dezelfde OAuth-flow die wordt gebruikt door de Codex CLI van OpenAI.

> ⚠️ **Let op — niet-goedgekeurd gebruik:** Dit gebruikt dezelfde OAuth-flow als de Codex CLI van OpenAI, en hoewel het momenteel werkt, kan OpenAI het gebruik van tokens door derden op elk moment beperken. GAC is klein genoeg om tot nu toe onder de radar te zijn gebleven, maar het gebruik van ChatGPT OAuth hier is **niet officieel goedgekeurd** voor tools van derden en kan op elk moment stoppen met werken. Als u betrouwbare generatie van commit-berichten nodig heeft, gebruik dan een directe API-provider (`openai`, enz.). Zie [Codex-documentatie van OpenAI](https://openai.com/codex) voor het huidige beleid.

## Wat is ChatGPT OAuth?

ChatGPT OAuth stelt u in staat om uw bestaande ChatGPT Plus- of Pro-abonnement te gebruiken om toegang te krijgen tot de Codex API voor het genereren van commit-berichten. In plaats van het beheren van API-sleutels en token-gebaseerde facturatie, authenticert u eenmaal via uw browser en beheert GAC de token-levenscyclus automatisch.

## Voordelen

- **Kosteneffectief**: Gebruik uw bestaande ChatGPT Plus/Pro-abonnement in plaats van apart te betalen voor API-toegang
- **Dezelfde modellen**: Toegang tot Codex-geoptimaliseerde modellen (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **Geen API-sleutelbeheer**: Browser-gebaseerde OAuth betekent dat er geen API-sleutels hoeven te worden geroteerd of opgeslagen
- **Separate facturatie**: ChatGPT OAuth-gebruik is gescheiden van directe OpenAI API-facturatie

## Installatie

GAC bevat ingebouwde OAuth-authenticatie voor ChatGPT. Het installatieproces is volledig geautomatiseerd en opent uw browser voor authenticatie.

### Optie 1: Tijdens eerste installatie (Aanbevolen)

Wanneer u `gac init` uitvoert, selecteert u eenvoudig «ChatGPT OAuth» als uw provider:

```bash
gac init
```

De wizard zal:

1. U vragen om «ChatGPT OAuth» te selecteren uit de providerlijst
2. Automatisch uw browser openen voor OAuth-authenticatie
3. Uw toegangstoken opslaan in `~/.gac/oauth/chatgpt-oauth.json`
4. Het standaardmodel instellen

### Optie 2: Later overschakelen naar ChatGPT OAuth

Als u GAC al hebt geconfigureerd met een andere provider en wilt overschakelen naar ChatGPT OAuth:

```bash
gac model
```

Vervolgens:

1. Selecteer «ChatGPT OAuth» uit de providerlijst
2. Uw browser wordt automatisch geopend voor OAuth-authenticatie
3. Token opgeslagen in `~/.gac/oauth/chatgpt-oauth.json`
4. Model automatisch geconfigureerd

### GAC normaal gebruiken

Na authenticatie gebruikt u GAC zoals gewoonlijk:

```bash
# Stage uw wijzigingen
git add .

# Genereer en commit met ChatGPT OAuth
gac

# Of overschrijf het model voor één commit
gac -m chatgpt-oauth:gpt-5.5
```

## Beschikbare modellen

ChatGPT OAuth biedt toegang tot Codex-geoptimaliseerde modellen. Huidige modellen omvatten:

- `gpt-5.5` — Nieuwste en krachtigste Codex-model
- `gpt-5.4` — Vorige generatie Codex-model
- `gpt-5.3-codex` — Derde generatie Codex-model

Raadpleeg de [OpenAI-documentatie](https://platform.openai.com/docs/models) voor de volledige lijst met beschikbare modellen.

## CLI-opdrachten

GAC biedt toegewijde CLI-opdrachten voor ChatGPT OAuth-beheer:

### Inloggen

Authenticeer of herauthenticeer met ChatGPT OAuth:

```bash
gac auth chatgpt login
```

Uw browser wordt automatisch geopend om de OAuth-flow te voltooien. Als u al bent geauthenticeerd, worden uw tokens vernieuwd.

### Uitloggen

Verwijder opgeslagen ChatGPT OAuth-tokens:

```bash
gac auth chatgpt logout
```

Dit verwijdert het opgeslagen tokenbestand op `~/.gac/oauth/chatgpt-oauth.json`.

### Status

Controleer uw huidige ChatGPT OAuth-authenticatiestatus:

```bash
gac auth chatgpt status
```

Of controleer alle providers in één keer:

```bash
gac auth
```

## Problemen oplossen

### Token verlopen

Als u authenticatiefouten ziet, is uw token mogelijk verlopen. Authenticeer opnieuw door uit te voeren:

```bash
gac auth chatgpt login
```

Uw browser wordt automatisch geopend voor nieuwe OAuth-authenticatie. GAC gebruikt automatisch vernieuwingstokens om toegang te verlengen zonder herauthenticatie wanneer mogelijk.

### Authenticatiestatus controleren

Om te controleren of u momenteel bent geauthenticeerd:

```bash
gac auth chatgpt status
```

Of controleer alle providers in één keer:

```bash
gac auth
```

### Uitloggen

Om uw opgeslagen token te verwijderen:

```bash
gac auth chatgpt logout
```

### «ChatGPT OAuth-token niet gevonden»

Dit betekent dat GAC uw toegangstoken niet kan vinden. Authenticeer door uit te voeren:

```bash
gac model
```

Selecteer vervolgens «ChatGPT OAuth» uit de providerlijst. De OAuth-flow start automatisch.

### «Authenticatie mislukt»

Als OAuth-authenticatie mislukt:

1. Zorg ervoor dat u een actief ChatGPT Plus- of Pro-abonnement heeft
2. Controleer of uw browser correct opent
3. Probeer een andere browser als de problemen aanhouden
4. Verifieer netwerkconnectiviteit met `auth.openai.com`
5. Controleer of de poorten 1455-1465 beschikbaar zijn voor de lokale callback-server

### Poort al in gebruik

De OAuth-callback-server probeert automatisch de poorten 1455-1465. Als alle poorten bezet zijn:

```bash
# Op macOS/Linux:
lsof -ti:1455-1465 | xargs kill -9

# Op Windows (PowerShell):
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Voer vervolgens `gac auth chatgpt login` opnieuw uit.

## Verschillen met de OpenAI-provider

| Functie       | OpenAI (`openai:`)              | ChatGPT OAuth (`chatgpt-oauth:`)                               |
| ------------- | ------------------------------- | -------------------------------------------------------------- |
| Authenticatie | API-sleutel (`OPENAI_API_KEY`)  | OAuth (geautomatiseerde browser-flow)                          |
| Facturatie    | Token-gebaseerde API-facturatie | Abonnement-gebaseerd (ChatGPT Plus/Pro)                        |
| Installatie   | Handmatige API-sleutelinvoer    | Automatische OAuth via `gac init` of `gac model`               |
| Token-beheer  | Langlevende API-sleutels        | OAuth-tokens (automatische vernieuwing met vernieuwingstokens) |
| Modellen      | Alle OpenAI-modellen            | Codex-geoptimaliseerde modellen                                |

## Veiligheidsopmerkingen

- **Commit nooit uw toegangstoken** naar versiebeheer
- GAC slaat OAuth-tokens op in `~/.gac/oauth/chatgpt-oauth.json` (buiten uw projectmap)
- OAuth-flow gebruikt PKCE (Proof Key for Code Exchange) voor verbeterde beveiliging
- Lokale callback-server draait alleen op localhost (poorten 1455-1465)
- Vernieuwingstokens worden gebruikt om toegang automatisch te verlengen zonder herauthenticatie

## Zie ook

- [Hoofddocumentatie](USAGE.md)
- [Probleemoplossingsgids](TROUBLESHOOTING.md)
- [Codex-documentatie van OpenAI](https://openai.com/codex)
