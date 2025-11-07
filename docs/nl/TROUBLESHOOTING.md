# Probleemoplossing voor gac

[English](../en/TROUBLESHOOTING.md) | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | [한국어](../ko/TROUBLESHOOTING.md) | [हिन्दी](../hi/TROUBLESHOOTING.md) | [Tiếng Việt](../vi/TROUBLESHOOTING.md) | [Français](../fr/TROUBLESHOOTING.md) | [Рус../](../ru/TROUBLESHOOTING.md) | [Español](../es/TROUBLESHOOTING.md) | [Português](../pt/TROUBLESHOOTING.md) | [Norsk](../no/TROUBLESHOOTING.md) | [Svenska](../sv/TROUBLESHOOTING.md) | [Deutsch](../de/TROUBLESHOOTING.md) | **Nederlands** | [Italiano](../it/TROUBLESHOOTING.md)

Deze gids behandelt veelvoorkomende problemen en oplossingen voor het installeren, configureren en uitvoeren van gac.

## Inhoudsopgave

- [Probleemoplossing voor gac](#probleemoplossing-voor-gac)
  - [Inhoudsopgave](#inhoudsopgave)
  - [1. Installatieproblemen](#1-installatieproblemen)
  - [2. Configuratieproblemen](#2-configuratieproblemen)
  - [3. Provider/API Fouten](#3-providerapi-fouten)
  - [4. Commit Groeperingsproblemen](#4-commit-groeperingsproblemen)
  - [5. Beveiliging en Geheim Detectie](#5-beveiliging-en-geheim-detectie)
  - [6. Pre-commit en Lefthook Hook Problemen](#6-pre-commit-en-lefthook-hook-problemen)
  - [7. Algemene Workflow Problemen](#7-algemene-workflow-problemen)
  - [8. Algemeen Debuggen](#8-algemeen-debuggen)
  - [Nog Steeds Vast?](#nog-steeds-vast)
  - [Waar Verder Hulp Krijgen](#waar-verder-hulp-krijgen)

## 1. Installatieproblemen

**Probleem:** `gac` commando niet gevonden na installatie

- Zorg ervoor dat u installeerde met `uv tool install gac` of `uvx gac`
- Als u `uv tool install` gebruikte, verifieer installatie met `uv tool list`
- Zorg ervoor dat `uv` geïnstalleerd is en in uw `$PATH` staat
- Herstart uw terminal na installatie

**Probleem:** Toestemming geweigerd of kan geen bestanden schrijven

- Controleer maprechten
- Probeer uit te voeren met passende privileges of verander mapeigendom

## 2. Configuratieproblemen

**Probleem:** gac kan uw API sleutel of model niet vinden

- Als u nieuw bent, voer `gac init` uit om uw provider, model en API sleutels interactief in te stellen
- Zorg ervoor dat uw `.gac.env` of omgevingsvariabelen correct ingesteld zijn
- Voer `gac --log-level=debug` uit om te zien welke config bestanden worden geladen en configuratieproblemen te debuggen
- Controleer op typefouten in variabele namen (bv., `GAC_GROQ_API_KEY`)

**Probleem:** Gebruiker-niveau `$HOME/.gac.env` wijzigingen worden niet opgepikt

- Zorg ervoor dat u het juiste bestand bewerkt voor uw OS:
  - Op macOS/Linux: `$HOME/.gac.env` (meestal `/Users/<uw-gebruikersnaam>/.gac.env` of `/home/<uw-gebruikersnaam>/.gac.env`)
  - Op Windows: `$HOME/.gac.env` (meestal `C:\Users\<uw-gebruikersnaam>\.gac.env` of gebruik `%USERPROFILE%`)
- Voer `gac --log-level=debug` uit om te bevestigen dat de gebruiker-niveau config wordt geladen
- Herstart uw terminal of voer uw shell opnieuw uit om omgevingsvariabelen te herladen
- Als het nog steeds niet werkt, controleer op typefouten en bestandsrechten

**Probleem:** Project-niveau `.gac.env` wijzigingen worden niet opgepikt

- Zorg ervoor dat uw project een `.gac.env` bestand bevat in de rootmap (naast uw `.git` map)
- Voer `gac --log-level=debug` uit om te bevestigen dat de project-niveau config wordt geladen
- Als u `.gac.env` bewerkt, herstart uw terminal of voer uw shell opnieuw uit om omgevingsvariabelen te herladen
- Als het nog steeds niet werkt, controleer op typefouten en bestandsrechten

**Probleem:** Kan taal voor commitberichten niet instellen of wijzigen

- Voer `gac language` (of `gac lang`) uit om interactief te kiezen uit 25+ ondersteunde talen
- Gebruik `-l <taal>` vlag om taal voor een enkele commit te overschrijven (bv., `gac -l zh-CN`, `gac -l Spanish`)
- Controleer uw config met `gac config show` om huidige taalinstelling te zien
- Taalinstelling wordt opgeslagen in `GAC_LANGUAGE` in uw `.gac.env` bestand

## 3. Provider/API Fouten

**Probleem:** Authenticatie of API fouten

- Zorg ervoor dat u de juiste API sleutels heeft ingesteld voor uw gekozen model (bv., `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- Controleer dubbel uw API sleutel en provider accountstatus
- Voor Ollama en LM Studio, bevestig dat de API URL overeenkomt met uw lokale instance. API sleutels zijn alleen nodig als u authenticatie heeft ingeschakeld.
- **Voor verlopen Claude Code token**: Voer `gac auth` uit om snel opnieuw in te loggen en uw token te vernieuwen. Uw browser opent automatisch voor OAuth.
- **Voor andere Claude Code OAuth-problemen**, zie de [Claude Code installatiehandleiding](CLAUDE_CODE.md) voor uitgebreide probleemoplossing.

**Probleem:** Model niet beschikbaar of niet ondersteund

- Streamlake gebruikt inference endpoint IDs in plaats van modelnamen. Zorg ervoor dat u de endpoint ID van hun console levert.
- Verifieer dat de modelnaam correct en ondersteund is door uw provider
- Controleer provider documentatie voor beschikbare modellen

## 4. Commit Groeperingsproblemen

**Probleem:** `--group` vlag werkt niet zoals verwacht

- De `--group` vlag analyseert automatisch staged wijzigingen en kan meerdere logische commits creëren
- De LLM kan besluiten dat een enkele commit logisch is voor uw set van staged wijzigingen, zelfs met `--group`
- Dit is opzettelijk gedrag - de LLM groepeert wijzigingen op basis van logische relaties, niet alleen kwantiteit
- Zorg ervoor dat u meerdere niet-gerelateerde wijzigingen gestaged heeft (bv., bug fix + feature toevoeging) voor beste resultaten
- Gebruik `gac --show-prompt` om te debuggen wat de LLM ziet

**Probleem:** Commits onjuist gegroepeerd of niet gegroepeerd wanneer verwacht

- De groepering wordt bepaald door de LLM's analyse van uw wijzigingen
- De LLM kan een enkele commit creëren als het bepaalt dat de wijzigingen logisch gerelateerd zijn
- Probeer hints toe te voegen met `-h "hint"` om de groeperingslogica te begeleiden (bv., `-h "scheid bug fix van refactoring"`)
- Bekijk de gegenereerde groepen voordat u bevestigt
- Als groepering niet goed werkt voor uw use case, commit wijzigingen afzonderlijk

## 5. Beveiliging en Geheim Detectie

**Probleem:** Valse positief: geheim scan detecteert niet-geheimen

- De security scanner zoekt naar patronen die lijken op API sleutels, tokens en wachtwoorden
- Als u voorbeeldcode, test fixtures of documentatie met placeholder sleutels commit, kunt u valse positieven zien
- Gebruik `--skip-secret-scan` om de scan te omzeilen als u zeker weet dat de wijzigingen veilig zijn
- Overweeg om test/voorbeeld bestanden uit te sluiten van commits, of gebruik duidelijk gemarkeerde placeholders

**Probleem:** Geheim scan detecteert geen daadwerkelijke geheimen

- De scanner gebruikt patroon matching en kan niet alle geheime typen vangen
- Bekijk altijd uw staged wijzigingen met `git diff --staged` voordat u commit
- Overweeg om extra beveiligingstools te gebruiken zoals `git-secrets` of `gitleaks` voor uitgebreide bescherming
- Rapporteer gemiste patronen als issues om detectie te helpen verbeteren

**Probleem:** Moet geheim scanning permanent uitschakelen

- Stel `GAC_SKIP_SECRET_SCAN=true` in uw `.gac.env` bestand
- Gebruik `gac config set GAC_SKIP_SECRET_SCAN true`
- Let op: Schakel alleen uit als u andere beveiligingsmaatregelen heeft

## 6. Pre-commit en Lefthook Hook Problemen

**Probleem:** Pre-commit of lefthook hooks falen en blokkeren commits

- Gebruik `gac --no-verify` om tijdelijk alle pre-commit en lefthook hooks over te slaan
- Fix de onderliggende problemen die de hooks laten falen
- Overweeg om uw pre-commit of lefthook configuratie aan te passen als hooks te streng zijn

**Probleem:** Pre-commit of lefthook hooks duren te lang of verstoren workflow

- Gebruik `gac --no-verify` om tijdelijk alle pre-commit en lefthook hooks over te slaan
- Overweeg om pre-commit hooks in `.pre-commit-config.yaml` of lefthook hooks in `.lefthook.yml` te configureren om minder agressief te zijn voor uw workflow
- Bekijk uw hook configuratie om prestaties te optimaliseren

## 7. Algemene Workflow Problemen

**Probleem:** Geen wijzigingen om te commit / niets gestaged

- gac vereist staged wijzigingen om een commitbericht te genereren
- Gebruik `git add <bestanden>` om wijzigingen te stage, of gebruik `gac -a` om automatisch alle wijzigingen te stage
- Controleer `git status` om te zien welke bestanden zijn gewijzigd
- Gebruik `gac diff` om een gefilterde weergave van uw wijzigingen te zien

**Probleem:** Commitbericht niet wat ik verwachtte

- Gebruik het interactieve feedbacksysteem: typ `r` om opnieuw te rollen, `e` om te bewerken, of geef natuurlijke taal feedback
- Voeg context toe met `-h "uw hint"` om de LLM te begeleiden
- Gebruik `-o` voor simpelere eenregelige berichten of `-v` voor meer gedetailleerde berichten
- Gebruik `--show-prompt` om te zien welke informatie de LLM ontvangt

**Probleem:** gac is te traag

- Gebruik `gac -y` om de bevestigingsprompt over te slaan
- Gebruik `gac -q` voor stille modus met minder output
- Overweeg om snellere/goedkopere modellen te gebruiken voor routine commits
- Gebruik `gac --no-verify` om hooks over te slaan als u vertragen

**Probleem:** Kan niet bewerken of feedback geven na berichtgeneratie

- Bij de prompt, typ `e` om bewerkmodus te betreden (ondersteunt vi/emacs keybindings)
- Typ `r` om opnieuw te genereren zonder feedback
- Of typ gewoon uw feedback direct (bv., "maak het korter", "focus op de bug fix")
- Druk op Enter op lege input om de prompt opnieuw te zien

## 8. Algemeen Debuggen

- Gebruik `gac init` om uw configuratie te resetten of bij te werken interactief
- Gebruik `gac --log-level=debug` voor gedetailleerde debug output en logging
- Gebruik `gac --show-prompt` om te zien welke prompt naar de LLM wordt gestuurd
- Gebruik `gac --help` om alle beschikbare command-line vlaggen te zien
- Gebruik `gac config show` om alle huidige configuratiewaarden te zien
- Controleer logs op foutmeldingen en stack traces
- Controleer de hoofd [README.md](../README.md) voor features, voorbeelden en snelle startinstructies

## Nog Steeds Vast?

- Zoek bestaande issues of open een nieuwe op de [GitHub repository](https://github.com/cellwebb/gac)
- Inclusief details over uw OS, Python versie, gac versie, provider en foutoutput
- Hoe meer detail u verstrekt, hoe sneller uw issue opgelost kan worden

## Waar Verder Hulp Krijgen

- Voor features en gebruikvoorbeelden, zie de hoofd [README.md](../README.md)
- Voor custom system prompts, zie [CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)
- Voor bijdragerichtlijnen, zie [CONTRIBUTING.md](../CONTRIBUTING.md)
- Voor licentie informatie, zie [../LICENSE](../LICENSE)
