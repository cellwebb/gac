# Felsökning av gac

[English](../en/TROUBLESHOOTING.md) | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | [한국어](../ko/TROUBLESHOOTING.md) | [हिन्दी](../hi/TROUBLESHOOTING.md) | [Tiếng Việt](../vi/TROUBLESHOOTING.md) | [Français](../fr/TROUBLESHOOTING.md) | [Русский](../ru/TROUBLESHOOTING.md) | [Español](../es/TROUBLESHOOTING.md) | [Português](../pt/TROUBLESHOOTING.md) | [Norsk](../no/TROUBLESHOOTING.md) | **Svenska** | [Deutsch](../de/TROUBLESHOOTING.md) | [Nederlands](../nl/TROUBLESHOOTING.md) | [Italiano](../it/TROUBLESHOOTING.md)

Denna guide täcker vanliga problem och lösningar för installation, konfiguration och körning av gac.

## Innehållsförteckning

- [Felsökning av gac](#felsökning-av-gac)
  - [Innehållsförteckning](#innehållsförteckning)
  - [1. Installationsproblem](#1-installationsproblem)
  - [2. Konfigurationsproblem](#2-konfigurationsproblem)
  - [3. Leverantör/API fel](#3-leverantörapi-fel)
  - [4. Problem med commitgruppering](#4-problem-med-commitgruppering)
  - [5. Säkerhet och hemlighetdetektering](#5-säkerhet-och-hemlighetdetektering)
  - [6. Pre-commit och Lefthook hook-problem](#6-pre-commit-och-lefthook-hook-problem)
  - [7. Vanliga arbetsflödesproblem](#7-vanliga-arbetsflödesproblem)
  - [8. Allmän felsökning](#8-allmän-felsökning)
  - [Fortfarande fast?](#fortfarande-fast)
  - [Var får man ytterligare hjälp](#var-får-man-ytterligare-hjälp)

## 1. Installationsproblem

**Problem:** `gac` kommandot hittas inte efter installation

- Säkerställ att du installerade med `uv tool install gac` eller `uvx gac`
- Om du använde `uv tool install`, verifiera installationen med `uv tool list`
- Säkerställ att `uv` är installerat och i din `$PATH`
- Starta om din terminal efter installation

**Problem:** Åtkomst nekad eller kan inte skriva filer

- Kontrollera katalogbehörigheter
- Försök köra med lämpliga privilegier eller ändra katalogägandeskap

## 2. Konfigurationsproblem

**Problem:** gac kan inte hitta din API-nyckel eller modell

- Om du är ny, kör `gac init` för att interaktivt konfigurera din leverantör, modell och API-nycklar
- Säkerställ att dina `.gac.env` eller miljövariabler är korrekt inställda
- Kör `gac --log-level=debug` för att se vilka konfigurationsfiler som laddas och felsöka konfigurationsproblem
- Kontrollera stavfel i variabelnamn (t.ex. `GAC_GROQ_API_KEY`)

**Problem:** Användarnivå `$HOME/.gac.env` ändringar läses inte in

- Säkerställ att du redigerar rätt fil för ditt operativsystem:
  - På macOS/Linux: `$HOME/.gac.env` (vanligtvis `/Users/<ditt-användarnamn>/.gac.env` eller `/home/<ditt-användarnamn>/.gac.env`)
  - På Windows: `$HOME/.gac.env` (vanligtvis `C:\Users\<ditt-användarnamn>\.gac.env` eller använd `%USERPROFILE%`)
- Kör `gac --log-level=debug` för att bekräfta att användarnivåns konfiguration läses in
- Starta om din terminal eller kör ditt skal igen för att ladda om miljövariabler
- Om det fortfarande inte fungerar, kontrollera stavfel och filbehörigheter

**Problem:** Projekt-nivå `.gac.env` ändringar läses inte in

- Säkerställ att ditt projekt innehåller en `.gac.env` fil i rotkatalogen (bredvid din `.git` mapp)
- Kör `gac --log-level=debug` för att bekräfta att projekt-nivå konfigurationen läses in
- Om du redigerar `.gac.env`, starta om din terminal eller kör ditt skal igen för att ladda om miljövariabler
- Om det fortfarande inte fungerar, kontrollera stavfel och filbehörigheter

**Problem:** Kan inte ställa in eller ändra språk för commit-meddelanden

- Kör `gac language` (eller `gac lang`) för att interaktivt välja bland 25+ stödda språk
- Använd `-l <språk>` flaggan för att åsidosätta språk för en enskild commit (t.ex. `gac -l sv`, `gac -l Spanish`)
- Kontrollera din konfiguration med `gac config show` för att se nuvarande språkinställning
- Språkinställningen lagras i `GAC_LANGUAGE` i din `.gac.env` fil

## 3. Leverantör/API fel

**Problem:** Autentisering eller API-fel

- Säkerställ att du har ställt in rätt API-nycklar för din valda modell (t.ex. `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- Dubbelkolla din API-nyckel och leverantörskontostatus
- För Ollama och LM Studio, bekräfta att API-URL:en matchar din lokala instans. API-nycklar behövs endast om du aktiverat autentisering.

**Problem:** Modellen är inte tillgänglig eller stöds inte

- Streamlake använder inference endpoint ID:n istället för modellnamn. Säkerställ att du anger endpoint ID:t från deras konsol.
- Verifiera att modellnamnet är korrekt och stöds av din leverantör
- Kontrollera leverantörens dokumentation för tillgängliga modeller

## 4. Problem med commitgruppering

**Problem:** `--group` flaggan fungerar inte som förväntat

- Flaggan `--group` analyserar automatiskt stageade ändringar och kan skapa flera logiska commits
- LLM:n kan avgöra att en enda commit är meningsfull för din uppsättning stageade ändringar, även med `--group`
- Detta är avsiktligt beteende - LLM:n grupperar ändringar baserat på logiska relationer, inte bara kvantitet
- Säkerställ att du har flera orelaterade ändringar stageade (t.ex. buggfix + ny funktion) för bästa resultat
- Använd `gac --show-prompt` för att felsöka vad LLM:n ser

**Problem:** Commits grupperas felaktigt eller inte grupperas när det förväntas

- Grupperingen bestäms av LLM:ns analys av dina ändringar
- LLM:n kan skapa en enda commit om den avgör att ändringarna är logiskt relaterade
- Försök lägga till ledtrådar med `-h "ledtråd"` för att guida grupperingslogiken (t.ex. `-h "separera buggfix från refaktorisering"`)
- Granska de genererade grupperna innan du bekräftar
- Om gruppering inte fungerar bra för ditt användningsfall, committa ändringar separat istället

## 5. Säkerhet och hemlighetdetektering

**Problem:** Falskt positivt: hemlighetsskanningen upptäcker icke-hemligheter

- Säkerhetsscanner söker efter mönster som liknar API-nycklar, tokens och lösenord
- Om du committar exempelkod, testfixtures eller dokumentation med platshållarnycklar, kan du se falska positiva resultat
- Använd `--skip-secret-scan` för att förbigå skanningen om du är säker på att ändringarna är säkra
- Överväg att exkludera test-/exempelfiler från commits, eller använd tydligt markerade platshållare

**Problem:** Hemlighetsskanning upptäcker inte faktiska hemligheter

- Scannern använder mönstermatching och kanske inte fångar alla hemlighetstyper
- Granska alltid dina stageade ändringar med `git diff --staged` innan du committar
- Överväg att använda ytterligare säkerhetsverktyg som `git-secrets` eller `gitleaks` för omfattande skydd
- Rapportera saknade mönster som ärenden för att hjälpa till att förbättra upptäckt

**Problem:** Behöver inaktivera hemlighetsskanning permanent

- Ställ in `GAC_SKIP_SECRET_SCAN=true` i din `.gac.env` fil
- Använd `gac config set GAC_SKIP_SECRET_SCAN true`
- Obs: Inaktivera endast om du har andra säkerhetsåtgärder på plats

## 6. Pre-commit och Lefthook hook-problem

**Problem:** Pre-commit eller lefthook hooks misslyckas och blockerar commits

- Använd `gac --no-verify` för att hoppa över alla pre-commit och lefthook hooks tillfälligt
- Åtgärda de underliggande problemen som orsakar att hooks misslyckas
- Överväg att justera din pre-commit eller lefthook konfiguration om hooks är för strikta

**Problem:** Pre-commit eller lefthook hooks tar för lång tid eller stör arbetsflödet

- Använd `gac --no-verify` för att hoppa över alla pre-commit och lefthook hooks tillfälligt
- Överväg att konfigurera pre-commit hooks i `.pre-commit-config.yaml` eller lefthook hooks i `.lefthook.yml` för att vara mindre aggressiva för ditt arbetsflöde
- Granska din hook-konfiguration för att optimera prestanda

## 7. Vanliga arbetsflödesproblem

**Problem:** Inga ändringar att committa / inget är staged

- gac kräver stageade ändringar för att generera ett commit-meddelande
- Använd `git add <filer>` för att stage ändringar, eller använd `gac -a` för att automatiskt stagea alla ändringar
- Kontrollera `git status` för att se vilka filer som har ändrats
- Använd `gac diff` för att se en filtrerad vy av dina ändringar

**Problem:** Commit-meddelandet är inte som jag förväntade mig

- Använd det interaktiva feedbacksystemet: skriv `r` för att regenerera, `e` för att redigera, eller ge feedback i naturligt språk
- Lägg till kontext med `-h "din ledtråd"` för att guida LLM:n
- Använd `-o` för enklare enradsmeddelanden eller `-v` för mer detaljerade meddelanden
- Använd `--show-prompt` för att se vilken information LLM:n får

**Problem:** gac är för långsamt

- Använd `gac -y` för att hoppa över bekräftelseprompten
- Använd `gac -q` för tyst läge med mindre output
- Överväg att använda snabbare/billigare modeller för rutinmässiga commits
- Använd `gac --no-verify` för att hoppa över hooks om de saktar ner dig

**Problem:** Kan inte redigera eller ge feedback efter meddelandegenerering

- Vid prompten, skriv `e` för att gå in i redigeringsläge (stöder vi/emacs tangentbindningar)
- Skriv `r` för att regenerera utan feedback
- Eller skriv helt enkelt din feedback direkt (t.ex. "gör det kortare", "fokusera på buggfixen")
- Tryck Enter vid tom input för att se prompten igen

## 8. Allmän felsökning

- Använd `gac init` för att återställa eller uppdatera din konfiguration interaktivt
- Använd `gac --log-level=debug` för detaljerad debugoutput och loggning
- Använd `gac --show-prompt` för att se vilken prompt som skickas till LLM:n
- Använd `gac --help` för att se alla tillgängliga kommandoradsflaggor
- Använd `gac config show` för att se alla nuvarande konfigurationsvärden
- Kontrollera loggar för felmeddelanden och stacktraces
- Kontrollera huvud [README.md](../README.md) för funktioner, exempel och snabbstartsinstruktioner

## Fortfarande fast?

- Sök efter befintliga ärenden eller öppna ett nytt på [GitHub-repositoriet](https://github.com/cellwebb/gac)
- Inkludera detaljer om ditt operativsystem, Python-version, gac-version, leverantör och feloutput
- Ju mer detalj du tillhandahåller, desto snabbare kan ditt ärende lösas

## Var får man ytterligare hjälp

- För funktioner och användningsexempel, se huvud [README.md](../README.md)
- För anpassade systemprompter, se [CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)
- För riktlinjer för bidrag, se [CONTRIBUTING.md](../CONTRIBUTING.md)
- För licensinformation, se [../LICENSE](../LICENSE)
