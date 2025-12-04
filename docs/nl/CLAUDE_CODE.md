# Claude Code gebruiken met GAC

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | **Nederlands** | [Italiano](../it/CLAUDE_CODE.md)

GAC ondersteunt authenticatie via Claude Code-abonnementen, waardoor u uw Claude Code-abonnement kunt gebruiken in plaats van te betalen voor de dure Anthropic API. Dit is perfect voor gebruikers die al toegang hebben tot Claude Code via hun abonnement.

## Wat is Claude Code?

Claude Code is de abonnementsdienst van Anthropic die OAuth-gebaseerde toegang tot Claude-modellen biedt. In plaats van API-sleutels (die per token worden gefactureerd) te gebruiken, gebruikt Claude Code OAuth-tokens van uw abonnement.

## Voordelen

- **Kosteneffectief**: Gebruik uw bestaande Claude Code-abonnement in plaats van apart te betalen voor API-toegang
- **Zelfde modellen**: Toegang tot dezelfde Claude-modellen (bv. `claude-sonnet-4-5`)
- **Aparte facturering**: Claude Code-gebruik is gescheiden van Anthropic API-facturering

## Instellingen

GAC bevat ingebouwde OAuth-authenticatie voor Claude Code. Het installatieproces is volledig geautomatiseerd en opent uw browser voor authenticatie.

### Optie 1: Tijdens de initiële installatie (Aanbevolen)

Voer `gac init` uit en selecteer eenvoudig "Claude Code" als uw provider:

```bash
gac init
```

De wizard zal:

1. U vragen om "Claude Code" te selecteren uit de providerlijst
2. Automatisch uw browser openen voor OAuth-authenticatie
3. Uw toegangstoken opslaan in `~/.gac.env`
4. Het standaardmodel instellen

### Optie 2: Later overschakelen naar Claude Code

Als u al GAC geconfigureerd heeft met een andere provider en wilt overschakelen naar Claude Code:

```bash
gac model
```

Dan:

1. Selecteer "Claude Code" uit de providerlijst
2. Uw browser opent automatisch voor OAuth-authenticatie
3. Token opgeslagen in `~/.gac.env`
4. Model automatisch geconfigureerd

### GAC normaal gebruiken

Eenmaal geverifieerd, gebruikt u GAC zoals u gewend bent:

```bash
# Stage uw wijzigingen
git add .

# Genereer en commit met Claude Code
gac

# Of overschrijf het model voor een enkele commit
gac -m claude-code:claude-sonnet-4-5
```

## Beschikbare modellen

Claude Code biedt toegang tot dezelfde modellen als de Anthropic API. Huidige Claude 4.5-familiemodellen omvatten:

- `claude-sonnet-4-5` - Nieuwste en meest intelligente Sonnet-model, beste voor codering
- `claude-haiku-4-5` - Snel en efficiënt
- `claude-opus-4-5` - Meest capabele model voor complex redeneren

Bekijk de [Claude-documentatie](https://docs.claude.com/en/docs/about-claude/models/overview) voor de volledige lijst van beschikbare modellen.

## Probleemoplossing

### Token verlopen

Als u authenticatiefouten ziet, is uw token mogelijk verlopen. Authenticeer opnieuw door uit te voeren:

```bash
gac auth claude-code login
```

Uw browser opent automatisch voor een nieuwe OAuth-authenticatie. Alternatief kunt u `gac model` uitvoeren, "Claude Code (OAuth)" selecteren en "Opnieuw authenticeren (nieuwe token krijgen)" kiezen.

### Authenticatiestatus controleren

Om te controleren of u momenteel geauthenticeerd bent:

```bash
gac auth claude-code status
```

Of controleer alle providers tegelijk:

```bash
gac auth
```

### Uitloggen

Om uw opgeslagen token te verwijderen:

```bash
gac auth claude-code logout
```

### "CLAUDE_CODE_ACCESS_TOKEN niet gevonden"

Dit betekent dat GAC uw toegangstoken niet kan vinden. Authenticeer door uit te voeren:

```bash
gac model
```

Selecteer dan "Claude Code" uit de providerlijst. De OAuth-flow start automatisch.

### "Authenticatie mislukt"

Als OAuth-authenticatie mislukt:

1. Zorg ervoor dat u een actief Claude Code-abonnement heeft
2. Controleer of uw browser correct opent
3. Probeer een andere browser als problemen aanhouden
4. Verifieer de netwerkconnectiviteit naar `claude.ai`
5. Controleer of poorten 8765-8795 beschikbaar zijn voor de lokale callback-server

## Verschillen met Anthropic provider

| Functie       | Anthropic (`anthropic:`)          | Claude Code (`claude-code:`)                                            |
| ------------- | --------------------------------- | ----------------------------------------------------------------------- |
| Authenticatie | API-sleutel (`ANTHROPIC_API_KEY`) | OAuth (automatische browser-flow)                                       |
| Facturering   | Per-token API-facturering         | Abonnement-gebaseerd                                                    |
| Instellingen  | Handmatige API-sleutel-invoer     | Automatische OAuth via `gac init` of `gac model`                        |
| Token-beheer  | Lange-termijn API-sleutels        | OAuth-tokens (kunnen verlopen, eenvoudige herauthenticatie via `model`) |
| Modellen      | Zelfde modellen                   | Zelfde modellen                                                         |

## Beveiligingsopmerkingen

- **Commit nooit uw toegangstoken** naar versiebeheer
- GAC slaat tokens automatisch op in `~/.gac.env` (buiten uw projectmap)
- Tokens kunnen verlopen en vereisen herauthenticatie via `gac model`
- De OAuth-flow gebruikt PKCE (Proof Key for Code Exchange) voor verbeterde beveiliging
- De lokale callback-server draait alleen op localhost (poorten 8765-8795)

## Zie ook

- [Hoofddocumentatie](USAGE.md)
- [Qwen.ai-installatie en authenticatie](QWEN.md)
- [Probleemoplossingsgids](TROUBLESHOOTING.md)
- [Claude Code-documentatie](https://claude.ai/code)
