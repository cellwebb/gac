# GitHub Copilot gebruiken met GAC

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | **Nederlands** | [Italiano](../it/GITHUB_COPILOT.md)

GAC ondersteunt authenticatie via GitHub Copilot, waardoor u uw Copilot-abonnement kunt gebruiken om toegang te krijgen tot modellen van OpenAI, Anthropic, Google en meer — allemaal inbegrepen bij uw GitHub Copilot-abonnement.

## Wat is GitHub Copilot OAuth?

GitHub Copilot OAuth gebruikt de **Device Flow** — een veilige, browser-gebaseerde authenticatiemethode die geen lokale callback-server vereist. U bezoekt een URL, voert een eenmalige code in en autoriseert GAC om uw Copilot-toegang te gebruiken. Achter de schermen wisselt GAC uw langlevende GitHub OAuth-token in voor kortlevende Copilot-sessietokens (~30 min) die toegang verlenen tot de Copilot API.

Dit geeft u toegang tot modellen van meerdere providers via één abonnement:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Voordelen

- **Multi-provider toegang**: Gebruik modellen van OpenAI, Anthropic en Google via één abonnement
- **Kosteneffectief**: Gebruik uw bestaande Copilot-abonnement in plaats van apart te betalen voor API-sleutels
- **Geen API-sleutelbeheer**: Device Flow-authenticatie — geen sleutels om te roteren of op te slaan
- **GitHub Enterprise-ondersteuning**: Werkt met GHE-instanties via de `--host` vlag

## Installatie

### Optie 1: Tijdens eerste installatie (Aanbevolen)

Wanneer u `gac init` uitvoert, selecteert u eenvoudig «Copilot» als uw provider:

```bash
gac init
```

De wizard zal:

1. U vragen om «Copilot» te selecteren uit de providerlijst
2. Een eenmalige code weergeven en uw browser openen voor Device Flow-authenticatie
3. Uw OAuth-token opslaan in `~/.gac/oauth/copilot.json`
4. Het standaardmodel instellen

### Optie 2: Later overschakelen naar Copilot

Als u GAC al hebt geconfigureerd met een andere provider:

```bash
gac model
```

Selecteer vervolgens «Copilot» uit de providerlijst en authenticeer.

### Optie 3: Direct inloggen

Authenticeer direct zonder uw standaardmodel te wijzigen:

```bash
gac auth copilot login
```

### GAC normaal gebruiken

Na authenticatie gebruikt u GAC zoals gewoonlijk:

```bash
# Stage uw wijzigingen
git add .

# Genereer en commit met Copilot
gac

# Of overschrijf het model voor één commit
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Beschikbare modellen

Copilot biedt toegang tot modellen van meerdere providers. Huidige modellen omvatten:

| Provider  | Modellen                                                                                       |
| --------- | ---------------------------------------------------------------------------------------------- |
| OpenAI    | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google    | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Let op:** De modellenlijst die na inloggen wordt getoond is informatief en kan verouderd raken naarmate GitHub nieuwe modellen toevoegt. Raadpleeg de [GitHub Copilot-documentatie](https://docs.github.com/en/copilot) voor de nieuwste beschikbare modellen.

## GitHub Enterprise

Om te authentiseren met een GitHub Enterprise-instantie:

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC zal automatisch de juiste Device Flow en API-eindpunten gebruiken voor uw GHE-instantie. Het sessietoken wordt per host gecached, zodat verschillende GHE-instanties onafhankelijk worden afgehandeld.

## CLI-opdrachten

GAC biedt toegewijde CLI-opdrachten voor Copilot-authenticatiebeheer:

### Inloggen

Authenticeer of herauthenticeer met GitHub Copilot:

```bash
gac auth copilot login
```

Uw browser wordt geopend naar een Device Flow-pagina waar u een eenmalige code invoert. Als u al bent geauthenticeerd, wordt u gevraagd of u opnieuw wilt authentiseren.

Voor GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Uitloggen

Verwijder opgeslagen Copilot-tokens:

```bash
gac auth copilot logout
```

Dit verwijdert het opgeslagen tokenbestand op `~/.gac/oauth/copilot.json` en de sessiecache.

### Status

Controleer uw huidige Copilot-authenticatiestatus:

```bash
gac auth copilot status
```

Of controleer alle providers in één keer:

```bash
gac auth
```

## Hoe het werkt

De Copilot-authenticatieflow verschilt van ChatGPT en Claude Code OAuth:

1. **Device Flow** — GAC vraagt een apparaatcode aan bij GitHub en toont deze
2. **Browser-autorisatie** — U bezoekt de URL en voert de code in
3. **Token-polling** — GAC pollt GitHub totdat u autorisatie voltooit
4. **Sessietoken-uitwisseling** — De GitHub OAuth-token wordt ingewisseld voor een kortlevende Copilot-sessietoken
5. **Automatische vernieuwing** — Sessietokens (~30 min) worden automatisch vernieuwd vanuit de gecachte OAuth-token

In tegenstelling tot PKCE-gebaseerde OAuth (ChatGPT/Claude Code), vereist de Device Flow geen lokale callback-server of poortbeheer.

## Problemen oplossen

### «Copilot-authenticatie niet gevonden»

Voer het inlogcommando uit om te authentiseren:

```bash
gac auth copilot login
```

### «Kon Copilot-sessietoken niet verkrijgen»

Dit betekent dat GAC een GitHub OAuth-token kreeg, maar deze niet kon inwisselen voor een Copilot-sessietoken. Meestal betekent dit:

1. **Geen Copilot-abonnement** — Uw GitHub-account heeft geen actief Copilot-abonnement
2. **Token ingetrokken** — De OAuth-token is ingetrokken; herauthenticeer met `gac auth copilot login`

### Sessietoken verlopen

Sessietokens verlopen na ~30 minuten. GAC vernieuwt ze automatisch vanuit de gecachte OAuth-token, dus u hoeft niet vaak te herauthentiseren. Als automatische vernieuwing mislukt:

```bash
gac auth copilot login
```

### «Ongeldige of onveilige hostnaam»

De `--host` vlag valideert hostnamen strikt om SSRF-aanvallen te voorkomen. Als u deze fout ziet:

- Zorg ervoor dat de hostnaam geen poorten bevat (bijv. gebruik `ghe.company.com` niet `ghe.company.com:8080`)
- Voeg geen protocollen of paden toe (bijv. gebruik `ghe.company.com` niet `https://ghe.company.com/api`)
- Privé-IP-adressen en `localhost` zijn geblokkeerd om veiligheidsredenen

### GitHub Enterprise-problemen

Als GHE-authenticatie mislukt:

1. Controleer of uw GHE-instantie Copilot heeft ingeschakeld
2. Controleer of uw GHE-hostnaam bereikbaar is vanaf uw machine
3. Zorg ervoor dat uw GHE-account een Copilot-licentie heeft
4. Probeer met de `--host` vlag expliciet: `gac auth copilot login --host ghe.mycompany.com`

## Verschillen met andere OAuth-providers

| Functie           | ChatGPT OAuth                | Claude Code                  | Copilot                                      |
| ----------------- | ---------------------------- | ---------------------------- | -------------------------------------------- |
| Auth-methode      | PKCE (browser-callback)      | PKCE (browser-callback)      | Device Flow (eenmalige code)                 |
| Callback-server   | Poorten 1455-1465            | Poorten 8765-8795            | Niet nodig                                   |
| Token-levensduur  | Langlevend (auto-vernieuwd)  | Verlopend (herauthenticatie) | Sessie ~30 min (auto-vernieuwd)              |
| Modellen          | Codex-geoptimaliseerd OpenAI | Claude-familie               | Multi-provider (OpenAI + Anthropic + Google) |
| GHE-ondersteuning | Nee                          | Nee                          | Ja (`--host` vlag)                           |

## Veiligheidsopmerkingen

- **Commit nooit uw OAuth-token** naar versiebeheer
- GAC slaat OAuth-tokens op in `~/.gac/oauth/copilot.json` (buiten uw projectmap)
- Sessietokens worden gecached in `~/.gac/oauth/copilot_session.json` met `0o600`-rechten
- Hostnamen worden strikt gevalideerd om SSRF- en URL-injectieaanvallen te voorkomen
- Privé-IP-adressen, loopback-adressen en `localhost` zijn geblokkeerd als hostnamen
- De Device Flow stelt geen lokale poorten bloot, waardoor het aanvalsoppervlak wordt verkleind

## Zie ook

- [Hoofddocumentatie](USAGE.md)
- [Probleemoplossingsgids](TROUBLESHOOTING.md)
- [ChatGPT OAuth-handleiding](CHATGPT_OAUTH.md)
- [Claude Code-handleiding](CLAUDE_CODE.md)
- [GitHub Copilot-documentatie](https://docs.github.com/en/copilot)
