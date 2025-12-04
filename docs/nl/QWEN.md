[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | **Nederlands** | [Italiano](../it/QWEN.md)

# Qwen.ai gebruiken met GAC

GAC ondersteunt authenticatie via Qwen.ai OAuth, zodat u uw Qwen.ai-account kunt gebruiken voor het genereren van commit-berichten. Dit maakt gebruik van OAuth-apparaatstroomauthenticatie voor een naadloze inlogervaring.

## Wat is Qwen.ai?

Qwen.ai is het AI-platform van Alibaba Cloud dat toegang biedt tot de Qwen-familie van grote taalmodellen. GAC ondersteunt op OAuth gebaseerde authenticatie, zodat u uw Qwen.ai-account kunt gebruiken zonder API-sleutels handmatig te hoeven beheren.

## Voordelen

- **Eenvoudige authenticatie**: OAuth-apparaatstroom - log gewoon in met uw browser
- **Geen API-sleutelbeheer**: Authenticatie wordt automatisch afgehandeld
- **Toegang tot Qwen-modellen**: Gebruik krachtige Qwen-modellen voor het genereren van commit-berichten

## Installatie

GAC bevat ingebouwde OAuth-authenticatie voor Qwen.ai met behulp van de apparaatstroom. Het installatieproces toont een code en opent uw browser voor authenticatie.

### Optie 1: Tijdens de eerste installatie (Aanbevolen)

Selecteer bij het uitvoeren van `gac init` eenvoudig "Qwen.ai (OAuth)" als uw provider:

```bash
gac init
```

De wizard zal:

1. U vragen om "Qwen.ai (OAuth)" te selecteren uit de lijst met providers
2. Een apparaatcode weergeven en uw browser openen
3. U authenticeert op Qwen.ai en voert de code in
4. Sla uw toegangstoken veilig op
5. Stel het standaardmodel in

### Optie 2: Later overschakelen naar Qwen.ai

Als u GAC al hebt geconfigureerd met een andere provider en wilt overschakelen naar Qwen.ai:

```bash
gac model
```

Vervolgens:

1. Selecteer "Qwen.ai (OAuth)" uit de lijst met providers
2. Volg de authenticatiestroom voor apparaatcode
3. Token veilig opgeslagen in `~/.gac/oauth/qwen.json`
4. Model automatisch geconfigureerd

### Optie 3: Direct inloggen

U kunt ook direct authenticeren met:

```bash
gac auth qwen login
```

Dit zal:

1. Een apparaatcode weergeven
2. Uw browser openen naar de Qwen.ai-authenticatiepagina
3. Nadat u bent geauthenticeerd, wordt het token automatisch opgeslagen

### GAC normaal gebruiken

Eenmaal geauthenticeerd, gebruikt u GAC zoals gewoonlijk:

```bash
# Stage uw wijzigingen
git add .

# Genereer en commit met Qwen.ai
gac

# Of overschrijf het model voor een enkele commit
gac -m qwen:qwen3-coder-plus
```

## Beschikbare modellen

De Qwen.ai OAuth-integratie gebruikt:

- `qwen3-coder-plus` - Geoptimaliseerd voor codeertaken (standaard)

Dit is het model dat beschikbaar is via het portal.qwen.ai OAuth-eindpunt. Overweeg voor andere Qwen-modellen de OpenRouter-provider te gebruiken die extra Qwen-modelopties biedt.

## Authenticatiecommando's

GAC biedt verschillende commando's voor het beheren van Qwen.ai-authenticatie:

```bash
# Inloggen bij Qwen.ai
gac auth qwen login

# Authenticatiestatus controleren
gac auth qwen status

# Uitloggen en opgeslagen token verwijderen
gac auth qwen logout

# Status van alle OAuth-providers controleren
gac auth
```

### Inlogopties

```bash
# Standaard inloggen (opent browser automatisch)
gac auth qwen login

# Inloggen zonder browser te openen (toont URL om handmatig te bezoeken)
gac auth qwen login --no-browser

# Stille modus (minimale uitvoer)
gac auth qwen login --quiet
```

## Probleemoplossing

### Token verlopen

Als u authenticatiefouten ziet, is uw token mogelijk verlopen. Authenticeer opnieuw door het volgende uit te voeren:

```bash
gac auth qwen login
```

De apparaatcodestroom start en uw browser wordt geopend voor herauthenticatie.

### Authenticatiestatus controleren

Om te controleren of u momenteel geauthenticeerd bent:

```bash
gac auth qwen status
```

Of controleer alle providers tegelijk:

```bash
gac auth
```

### Uitloggen

Om uw opgeslagen token te verwijderen:

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (Qwen-authenticatie niet gevonden)

Dit betekent dat GAC uw toegangstoken niet kan vinden. Authenticeer door het volgende uit te voeren:

```bash
gac auth qwen login
```

Of voer `gac model` uit en selecteer "Qwen.ai (OAuth)" uit de lijst met providers.

### "Authentication failed" (Authenticatie mislukt)

Als OAuth-authenticatie mislukt:

1. Zorg ervoor dat u een Qwen.ai-account hebt
2. Controleer of uw browser correct opent
3. Controleer of u de apparaatcode correct hebt ingevoerd
4. Probeer een andere browser als de problemen aanhouden
5. Controleer de netwerkverbinding met `qwen.ai`

### Apparaatcode werkt niet

Als authenticatie met apparaatcode niet werkt:

1. Zorg ervoor dat de code niet is verlopen (codes zijn beperkte tijd geldig)
2. Probeer `gac auth qwen login` opnieuw uit te voeren voor een nieuwe code
3. Gebruik de vlag `--no-browser` en bezoek de URL handmatig als het openen van de browser mislukt

## Veiligheidsopmerkingen

- **Commit uw toegangstoken nooit** naar versiebeheer
- GAC slaat tokens automatisch op in `~/.gac/oauth/qwen.json` (buiten uw projectmap)
- Tokenbestanden hebben beperkte rechten (alleen leesbaar door eigenaar)
- Tokens kunnen verlopen en vereisen herauthenticatie
- De OAuth-apparaatstroom is ontworpen voor veilige authenticatie op headless-systemen

## Zie ook

- [Hoofddocumentatie](USAGE.md)
- [Claude Code-installatie](CLAUDE_CODE.md)
- [Gids voor probleemoplossing](TROUBLESHOOTING.md)
- [Qwen.ai-documentatie](https://qwen.ai)
