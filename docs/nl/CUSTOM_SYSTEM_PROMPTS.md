# Custom System Prompts

[English](../en/CUSTOM_SYSTEM_PROMPTS.md) | [简体中文](../zh-CN/CUSTOM_SYSTEM_PROMPTS.md) | [繁體中文](../zh-TW/CUSTOM_SYSTEM_PROMPTS.md) | [日本語](../ja/CUSTOM_SYSTEM_PROMPTS.md) | [한국어](../ko/CUSTOM_SYSTEM_PROMPTS.md) | [हिन्दी](../hi/CUSTOM_SYSTEM_PROMPTS.md) | [Français](../fr/CUSTOM_SYSTEM_PROMPTS.md) | [Русский](../ru/CUSTOM_SYSTEM_PROMPTS.md) | [Español](../es/CUSTOM_SYSTEM_PROMPTS.md) | [Português](../pt/CUSTOM_SYSTEM_PROMPTS.md) | [Deutsch](../de/CUSTOM_SYSTEM_PROMPTS.md) | **Nederlands**

Deze gids legt uit hoe u de systeemprompt kunt aanpassen die GAC gebruikt om commitberichten te genereren, waardoor u uw eigen commitberichtstijl en conventies kunt definiëren.

## Inhoudsopgave

- [Custom System Prompts](#custom-system-prompts)
  - [Inhoudsopgave](#inhoudsopgave)
  - [Wat Zijn System Prompts?](#wat-zijn-system-prompts)
  - [Waarom Custom System Prompts Gebruiken?](#waarom-custom-system-prompts-gebruiken)
  - [Snelle Start](#snelle-start)
  - [Uw Custom System Prompt Schrijven](#uw-custom-system-prompt-schrijven)
  - [Voorbeelden](#voorbeelden)
    - [Emoji-gebaseerde Commit Stijl](#emoji-gebaseerde-commit-stijl)
    - [Team-specifieke Conventies](#team-specifieke-conventies)
    - [Gedetailleerde Technische Stijl](#gedetailleerde-technische-stijl)
  - [Best Practices](#best-practices)
    - [Doe:](#doe)
    - [Doe Niet:](#doe-niet)
    - [Tips:](#tips)
  - [Probleemoplossing](#probleemoplossing)
    - [Berichten hebben nog steeds "chore:" prefix](#berichten-hebben-nog-steeds-chore-prefix)
    - [AI negeert mijn instructies](#ai-negeert-mijn-instructies)
    - [Berichten zijn te lang/kort](#berichten-zijn-te-langkort)
    - [Custom prompt wordt niet gebruikt](#custom-prompt-wordt-niet-gebruikt)
    - [Wil terugkeren naar standaard](#wil-terugkeren-naar-standaard)
  - [Gerelateerde Documentatie](#gerelateerde-documentatie)
  - [Hulp Nodig?](#hulp-nodig)

## Wat Zijn System Prompts?

GAC gebruikt twee prompts bij het genereren van commitberichten:

1. **System Prompt** (aanpasbaar): Instructies die de rol, stijl en conventies voor commitberichten definiëren
2. **User Prompt** (automatisch): De git diff data die laat zien wat er gewijzigd is

De systeemprompt vertelt de AI _hoe_ commitberichten te schrijven, terwijl de gebruikersprompt het _wat_ levert (de daadwerkelijke codewijzigingen).

## Waarom Custom System Prompts Gebruiken?

U wilt misschien een custom systeemprompt als:

- Uw team een andere commitberichtstijl gebruikt dan conventionele commits
- U emojis, prefixen of andere custom formaten prefereert
- U meer of minder detail in commitberichten wilt
- U company-specifieke richtlijnen of sjablonen heeft
- U de stem en toon van uw team wilt matchen
- U commitberichten in een andere taal wilt (zie Taalconfiguratie hieronder)

## Snelle Start

1. **Creëer uw custom systeemprompt bestand:**

   ```bash
   # Kopieer het voorbeeld als startpunt
   cp custom_system_prompt.example.txt ~/.config/gac/my_system_prompt.txt

   # Of creëer uw eigen vanaf nul
   vim ~/.config/gac/my_system_prompt.txt
   ```

2. **Voeg toe aan uw `.gac.env` bestand:**

   ```bash
   # In ~/.gac.env of project-niveau .gac.env
   GAC_SYSTEM_PROMPT_PATH=/pad/naar/uw/custom_system_prompt.txt
   ```

3. **Test het:**

   ```bash
   gac --dry-run
   ```

Dat is alles! GAC zal nu uw custom instructies gebruiken in plaats van de standaard.

## Uw Custom System Prompt Schrijven

Uw custom systeempunt kan platte tekst zijn - geen speciaal formaat of XML tags vereist. Schrijf gewoon duidelijke instructies voor hoe de AI commitberichten moet genereren.

**Belangrijke dingen om op te nemen:**

1. **Rol definitie** - Wat de AI moet zijn
2. **Formaat vereisten** - Structuur, lengte, stijl
3. **Voorbeelden** - Toon wat goede commitberichten lijken
4. **Beperkingen** - Wat te vermijden of vereisten om te voldoen

**Voorbeeldstructuur:**

```text
U bent een commitberichtschrijver voor [uw/project/team].

Bij het analyseren van codewijzigingen, creëer een commitbericht dat:

1. [Eerste vereiste]
2. [Tweede vereiste]
3. [Derde vereiste]

Voorbeeldformaat:
[Toon een voorbeeld commitbericht]

Uw gehele respons zal direct worden gebruikt als het commitbericht.
```

## Voorbeelden

### Emoji-gebaseerde Commit Stijl

Zie [`custom_system_prompt.example.txt`](../custom_system_prompt.example.txt) voor een compleet emoji-gebaseerd voorbeeld.

**Quick snippet:**

```text
U bent een commitberichtschrijver die emojis en een vriendelijke toon gebruikt.

Start elk bericht met een emoji:
- 🎉 voor nieuwe features
- 🐛 voor bug fixes
- 📝 voor documentatie
- ♻️ voor refactoring

Houd de eerste regel onder 72 tekens en leg uit WAAROM de wijziging belangrijk is.
```

### Team-specifieke Conventies

```text
U schrijft commitberichten voor een enterprise bank-applicatie.

Vereisten:
1. Start met een JIRA ticketnummer in brackets (bv., [BANK-1234])
2. Gebruik formele, professionele toon
3. Inclusief security implicaties indien relevant
4. Referentie compliance vereisten (PCI-DSS, SOC2, etc.)
5. Houd berichten beknopt maar compleet

Formaat:
[TICKET-123] Korte samenvatting van wijziging

Gedetailleerde uitleg van wat er veranderd is en waarom. Inclusief:
- Bedrijfsrechtvaardiging
- Technische aanpak
- Risico beoordeling (indien van toepassing)

Voorbeeld:
[BANK-1234] Implementeer rate limiting voor login endpoints

Redis-gebaseerde rate limiting toegevoegd om brute force aanvallen te voorkomen.
Limiteert login pogingen tot 5 per IP per 15 minuten.
Voldoet aan SOC2 security vereisten voor toegangscontrole.
```

### Gedetailleerde Technische Stijl

```text
U bent een technische commitberichtschrijver die uitgebreide documentatie creëert.

Voor elke commit, lever:

1. Een duidelijke, beschrijvende titel (onder 72 tekens)
2. Een lege regel
3. WAT: Wat er veranderd is (2-3 zinnen)
4. WAAROM: Waarom de wijziging noodzakelijk was (2-3 zinnen)
5. HOE: Technische aanpak of sleutel implementatiedetails
6. IMPACT: Bestanden/componenten beïnvloed en potentiële bijeffecten

Gebruik technische precisie. Referentie specifieke functies, klassen en modules.
Gebruik tegenwoordige tijd en actieve stem.

Voorbeeld:
Refactor authenticatie middleware om dependency injection te gebruiken

WAT: Vervangen van globale auth state met injectable AuthService. Bijgewerkt
alle route handlers om AuthService te accepteren via constructor injection.

WAAROM: Global state maakte testen moeilijk en creëerde verborgen afhankelijkheden.
Dependency injection verbetert testbaarheid en maakt afhankelijkheden expliciet.

HOE: AuthService interface gecreëerd, JWTAuthService en
MockAuthService geïmplementeerd. Route handler constructors gewijzigd om AuthService te vereisen.
Dependency injection container configuratie bijgewerkt.

IMPACT: Beïnvloedt alle geauthenticeerde routes. Geen gedragswijzigingen voor gebruikers.
Tests draaien nu 3x sneller met MockAuthService. Migratie vereist voor
routes/auth.ts, routes/api.ts en routes/admin.ts.
```

## Best Practices

### Doe

- ✅ **Wees specifiek** - Duidelijke instructies produceren betere resultaten
- ✅ **Inclusief voorbeelden** - Toon de AI wat goed is
- ✅ **Test iteratief** - Probeer uw prompt, verfijn op basis van resultaten
- ✅ **Houd het gefocust** - Te veel regels kunnen de AI verwarren
- ✅ **Gebruik consistente terminologie** - Houd u aan dezelfde termen throughout
- ✅ **Eindig met een herinnering** - Versterk dat de response als-is zal worden gebruikt

### Doe Niet

- ❌ **Gebruik XML tags** - Platte tekst werkt het best (tenzij u specifiek die structuur wilt)
- ❌ **Maak het te lang** - Streef naar 200-500 woorden instructies
- ❌ **Tegenstrijd uzelf** - Wees consistent in uw vereisten
- ❌ **Vergeet het einde niet** - Herinner altijd: "Uw gehele respons zal direct worden gebruikt als het commitbericht"

### Tips

- **Start met het voorbeeld** - Kopieer `custom_system_prompt.example.txt` en pas het aan
- **Test met `--dry-run`** - Zie het resultaat zonder een commit te maken
- **Gebruik `--show-prompt`** - Zie wat er naar de AI wordt gestuurd
- **Iteer op basis van resultaten** - Als berichten niet helemaal goed zijn, pas uw instructies aan
- **Version control uw prompt** - Houd uw custom prompt in de repository van uw team
- **Project-specifieke prompts** - Gebruik project-niveau `.gac.env` voor project-specifieke stijlen

## Probleemoplossing

### Berichten hebben nog steeds "chore:" prefix

**Probleem:** Uw custom emoji berichten krijgen "chore:" toegevoegd.

**Oplossing:** Dit zou niet moeten gebeuren - GAC schakelt automatisch conventionele commit afdwinging uit bij gebruik van custom system prompts. Als u dit ziet, dien dan een [issue in](https://github.com/cellwebb/gac/issues).

### AI negeert mijn instructies

**Probleem:** Gegenereerde berichten volgen uw custom formaat niet.

**Oplossing:**

1. Maak uw instructies explicieter en specifieker
2. Voeg duidelijke voorbeelden toe van het gewenste formaat
3. Eindig met: "Uw gehele respons zal direct worden gebruikt als het commitbericht"
4. Verminder het aantal vereisten - te veel kunnen de AI verwarren
5. Probeer een ander model te gebruiken (sommige volgen instructies beter dan anderen)

### Berichten zijn te lang/kort

**Probleem:** Gegenereerde berichten komen niet overeen met uw lengtevereisten.

**Oplossing:**

- Wees expliciet over lengte (bv., "Houd berichten onder 50 tekens")
- Toon voorbeelden van de exacte lengte die u wilt
- Overweeg om `--one-liner` vlag te gebruiken voor korte berichten

### Custom prompt wordt niet gebruikt

**Probleem:** GAC gebruikt nog steeds standaard commit formaat.

**Oplossing:**

1. Controleer dat `GAC_SYSTEM_PROMPT_PATH` correct is ingesteld:

   ```bash
   gac config get GAC_SYSTEM_PROMPT_PATH
   ```

2. Verifieer dat het bestandspad bestaat en leesbaar is:

   ```bash
   cat "$GAC_SYSTEM_PROMPT_PATH"
   ```

3. Controleer `.gac.env` bestanden in deze volgorde:
   - Project niveau: `./.gac.env`
   - Gebruiker niveau: `~/.gac.env`
4. Probeer een absoluut pad in plaats van relatief pad

### Taalconfiguratie

**Let op:** U heeft geen custom systeemprompt nodig om de taal van commitberichten te wijzigen!

Als u alleen de taal van uw commitberichten wilt wijzigen (terwijl u het standaard conventionele commit formaat behoudt), gebruik de interactieve taalkiezer:

```bash
gac language
```

Dit presenteert een interactief menu met 25+ talen in hun native scripts (Español, Français, 日本語, etc.). Selecteer uw voorkeurstaal, en het zal automatisch `GAC_LANGUAGE` instellen in uw `~/.gac.env` bestand.

Alternatief kunt u de taal handmatig instellen:

```bash
# In ~/.gac.env of project-niveau .gac.env
GAC_LANGUAGE=Spanish
```

Standaard blijven conventionele commit prefixen (feat:, fix:, etc.) in Engels voor compatibiliteit met changelog tools en CI/CD pipelines, terwijl alle andere tekst in uw gespecificeerde taal is.

**Wilt u prefixen ook vertalen?** Stel `GAC_TRANSLATE_PREFIXES=true` in uw `.gac.env` voor volledige lokalisatie:

```bash
GAC_LANGUAGE=Spanish
GAC_TRANSLATE_PREFIXES=true
```

Dit zal alles vertalen, inclusief prefixen (bv., `corrección:` in plaats van `fix:`).

Dit is eenvoudiger dan het creëren van een custom systeemprompt als taal uw enige aanpassingsbehoefte is.

### Wil terugkeren naar standaard

**Probleem:** Wil tijdelijk standaard prompts gebruiken.

**Oplossing:**

```bash
# Optie 1: Unset de omgevingsvariabele
gac config unset GAC_SYSTEM_PROMPT_PATH

# Optie 2: Commenteer het uit in .gac.env
# GAC_SYSTEM_PROMPT_PATH=/pad/naar/custom_prompt.txt

# Optie 3: Gebruik een ander .gac.env voor specifieke projecten
```

---

## Gerelateerde Documentatie

- [USAGE.md](USAGE.md) - Command-line vlaggen en opties
- [README.md](../../README.md) - Installatie en basis setup
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Algemene probleemoplossing

## Hulp Nodig?

- Rapporteer issues: [GitHub Issues](https://github.com/cellwebb/gac/issues)
- Deel uw custom prompts: Bijdragen welkom!
