# Anpassade System Prompter

[Svenska](docs/sv/CUSTOM_SYSTEM_PROMPTS.md) | **English** | [简体中文](../zh-CN/CUSTOM_SYSTEM_PROMPTS.md) | [繁體中文](../zh-TW/CUSTOM_SYSTEM_PROMPTS.md) | [日本語](../ja/CUSTOM_SYSTEM_PROMPTS.md) | [한국어](../ko/CUSTOM_SYSTEM_PROMPTS.md) | [हिन्दी](../hi/CUSTOM_SYSTEM_PROMPTS.md) | [Tiếng Việt](../vi/CUSTOM_SYSTEM_PROMPTS.md) | [Français](../fr/CUSTOM_SYSTEM_PROMPTS.md) | [Русский](../ru/CUSTOM_SYSTEM_PROMPTS.md) | [Español](../es/CUSTOM_SYSTEM_PROMPTS.md) | [Português](../pt/CUSTOM_SYSTEM_PROMPTS.md) | [Deutsch](../de/CUSTOM_SYSTEM_PROMPTS.md) | [Nederlands](../nl/CUSTOM_SYSTEM_PROMPTS.md)

Denna guide förklarar hur du anpassar system prompten som GAC använder för att generera commit-meddelanden, vilket gör att du kan definiera din egen commit-meddelandestil och konventioner.

## Innehållsförteckning

- [Anpassade System Prompter](#anpassade-system-prompter)
  - [Innehållsförteckning](#innehållsförteckning)
  - [Vad är System Prompter?](#vad-är-system-prompter)
  - [Varför Använda Anpassade System Prompter?](#varför-använda-anpassade-system-prompter)
  - [Snabbstart](#snabbstart)
  - [Skriva Din Anpassade System Prompt](#skriva-din-anpassade-system-prompt)
  - [Exempel](#exempel)
    - [Emoji-baserad Commit-stil](#emoji-baserad-commit-stil)
    - [Teamspecifika Konventioner](#teamspecifika-konventioner)
    - [Detaljerad Teknisk Stil](#detaljerad-teknisk-stil)
  - [Bästa Praxis](#bästa-praxis)
    - [Gör:](#gör)
    - [Gör inte:](#gör-inte)
    - [Tips:](#tips)
  - [Felsökning](#felsökning)
    - [Meddelanden har fortfarande "chore:"-prefix](#meddelanden-har-fortfarande-chore-prefix)
    - [AI ignorerar mina instruktioner](#ai-ignorerar-mina-instruktioner)
    - [Meddelanden är för långa/korta](#meddelanden-är-för-långakorta)
    - [Anpassad prompt används inte](#anpassad-prompt-används-inte)
    - [Vill byta tillbaka till standard](#vill-byta-tillbaka-till-standard)
  - [Relaterad Dokumentation](#relaterad-dokumentation)
  - [Behöver Hjälp?](#behöver-hjälp)

## Vad är system prompter?

GAC använder två prompter när det genererar commit-meddelanden:

1. **System Prompt** (anpassningsbar): Instruktioner som definierar rollen, stilen och konventionerna för commit-meddelanden
2. **User Prompt** (automatisk): Git diff datan som visar vad som har ändrats

System prompten berättar för AI:n _hur_ man ska skriva commit-meddelanden, medan user prompten tillhandahåller _vad_ (de faktiska kodändringarna).

## Varför använda anpassade system prompter?

Du kanske vill ha en anpassad system prompt om:

- Ditt team använder en annan commit-meddelandestil än konventionella commits
- Du föredrar emojis, prefix eller andra anpassade format
- Du vill ha mer eller mindre detalj i commit-meddelanden
- Du har företagsspecifika riktlinjer eller mallar
- Du vill matcha ditt teams röst och ton
- Du vill ha commit-meddelanden på ett annat språk (se Språkkonfiguration nedan)

## Snabbstart

1. **Skapa din anpassade system prompt-fil:**

   ```bash
   # Kopiera exempelfilen som utgångspunkt
   cp custom_system_prompt.example.txt ~/.config/gac/min_system_prompt.txt

   # Eller skapa din egen från grunden
   vim ~/.config/gac/min_system_prompt.txt
   ```

2. **Lägg till i din `.gac.env` fil:**

   ```bash
   # I ~/.gac.env eller projekt-nivå .gac.env
   GAC_SYSTEM_PROMPT_PATH=/path/to/din/anpassade_system_prompt.txt
   ```

3. **Testa den:**

   ```bash
   gac --dry-run
   ```

Det var allt! GAC kommer nu att använda dina anpassade instruktioner istället för standardinställningarna.

## Skriva din anpassade system prompt

Din anpassade system prompt kan vara vanlig text - inget specialformat eller XML-taggar behövs. Skriv bara tydliga instruktioner för hur AI:n ska generera commit-meddelanden.

**Viktiga saker att inkludera:**

1. **Rolldefinition** - Vad AI:n ska agera som
2. **Formatkrav** - Struktur, längd, stil
3. **Exempel** - Visa vad bra commit-meddelanden ser ut som
4. **Begränsningar** - Vad man ska undvika eller krav att uppfylla

**Exempelstruktur:**

```text
Du är en commit-meddelandeskrivare för [ditt projekt/team].

När du analyserar kodändringar, skapa ett commit-meddelande som:

1. [Första kravet]
2. [Andra kravet]
3. [Tredje kravet]

Exempelformat:
[Visa ett exempel på commit-meddelande]

Hela ditt svar kommer att användas direkt som commit-meddelandet.
```

## Exempel

### Emoji-baserad commit-stil

Se [`custom_system_prompt.example.txt`](../../examples/custom_system_prompt.example.txt) för ett komplett emoji-baserat exempel.

**Snabbt utdrag:**

```text
Du är en commit-meddelandeskrivare som använder emojis och en vänlig ton.

Börja varje meddelande med en emoji:
- 🎉 för nya funktioner
- 🐛 för buggfixar
- 📝 för dokumentation
- ♻️ för refaktorisering

Håll första raden under 72 tecken och förklara VARFÖR ändringen är viktig.
```

### Teamspecifika konventioner

```text
Du skriver commit-meddelanden för en företagsbankapplikation.

Krav:
1. Börja med ett JIRA ticketnummer inom hakparenteser (t.ex. [BANK-1234])
2. Använd formellt, professionellt tonfall
3. Inkludera säkerhetsimplikationer om relevanta
4. Referera till eventuella efterlevnadskrav (PCI-DSS, SOC2, etc.)
5. Håll meddelanden koncisa men kompletta

Format:
[TICKET-123] Kort sammanfattning av ändring

Detaljerad förklaring av vad som ändrats och varför. Inkludera:
- Affärsmotivering
- Teknisk approach
- Riskbedömning (om tillämpligt)

Exempel:
[BANK-1234] Implementera hastighetsbegränsning för inloggningsendpoints

Lade till Redis-baserad hastighetsbegränsning för att förhindra brute force-attacker.
Begränsar inloggningsförsök till 5 per IP per 15 minuter.
Uppfyller SOC2 säkerhetskrav för åtkomstkontroll.
```

### Detaljerad teknisk stil

```text
Du är en teknisk commit-meddelandeskrivare som skapar omfattande dokumentation.

För varje commit, tillhandahåll:

1. En tydlig, beskrivande titel (under 72 tecken)
2. En tom rad
3. VAD: Vad som ändrades (2-3 meningar)
4. VARFÖR: Varför ändringen var nödvändig (2-3 meningar)
5. HUR: Teknisk approach eller viktiga implementeringsdetaljer
6. PÅVERKAN: Filer/komponenter som påverkades och potentiella biverkningar

Använd teknisk precision. Referera till specifika funktioner, klasser och moduler.
Använd nutid och aktiv form.

Exempel:
Refaktorisera autentiseringsmiddleware för att använda dependency injection

VAD: Ersatte globalt auth-tillstånd med injicerbar AuthService. Uppdaterade
alla route handlers att acceptera AuthService genom konstruktorinjicering.

VARFÖR: Globalt tillstånd gjorde testning svår och skapade dolda beroenden.
Dependency injection förbättrar testbarhet och gör beroenden explicita.

HUR: Skapade AuthService-interface, implementerade JWTAuthService och
MockAuthService. Modifierade route handler konstruktörer att kräva AuthService.
Uppdaterade konfigurationen för dependency injection container.

PÅVERKAN: Påverkar alla autentiserade routes. Inga beteendeändringar för användare.
Tester kör nu 3x snabbare med MockAuthService. Migration krävdes för
routes/auth.ts, routes/api.ts och routes/admin.ts.
```

## Bästa praxis

### Gör

- ✅ **Var specifik** - Tydliga instruktioner ger bättre resultat
- ✅ **Inkludera exempel** - Visa AI:n vad som är bra
- ✅ **Testa iterativt** - Prova din prompt, förfina baserat på resultat
- ✅ **Håll det fokuserat** - För många regler kan förvirra AI:n
- ✅ **Använd konsekvent terminologi** - Håll samma termer genomgående
- ✅ **Avsluta med en påminnelse** - Förstärk att svaret kommer användas som det är

### Gör inte

- ❌ **Använd XML-taggar** - Vanlig text fungerar bäst (om du inte specifikt vill ha den strukturen)
- ❌ **Gör det för långt** - Sikta på 200-500 ord av instruktioner
- ❌ **Motsäg dig själv** - Var konsekvent i dina krav
- ❌ **Glöm avslutningen** - Påminn alltid: "Hela ditt svar kommer att användas direkt som commit-meddelandet"

### Tips

- **Börja med exemplet** - Kopiera `../../examples/custom_system_prompt.example.txt` och modifiera det
- **Testa med `--dry-run`** - Se resultatet utan att göra en commit
- **Använd `--show-prompt`** - Se vad som skickas till AI:n
- **Iterera baserat på resultat** - Om meddelanden inte är rätt, justera dina instruktioner
- **Versionshantera din prompt** - Håll din anpassade prompt i ditt teams repo
- **Projektspecifika prompter** - Använd projekt-nivå `.gac.env` för projektspecifika stilar

## Felsökning

### Meddelanden har fortfarande "chore:"-prefix

**Problem:** Dina anpassade emoji-meddelanden får "chore:"-tillägg.

**Lösning:** Detta bör inte hända - GAC inaktiverar automatiskt konventionell commit-tillämpning när anpassade system prompter används. Om du ser detta, vänligen [lämna in ett ärende](https://github.com/cellwebb/gac/issues).

### AI ignorerar mina instruktioner

**Problem:** Genererade meddelanden följer inte ditt anpassade format.

**Lösning:**

1. Gör dina instruktioner mer explicita och specifika
2. Lägg till tydliga exempel på önskat format
3. Avsluta med: "Hela ditt svar kommer att användas direkt som commit-meddelandet"
4. Reducera antalet krav - för många kan förvirra AI:n
5. Försök använda en annan modell (vissa följer instruktioner bättre än andra)

### Meddelanden är för långa/korta

**Problem:** Genererade meddelanden matchar inte dina längdkrav.

**Lösning:**

- Var explicit om längd (t.ex. "Håll meddelanden under 50 tecken")
- Visa exempel på exakt längd du vill ha
- Överväg att använda `--one-liner` flaggan också för korta meddelanden

### Anpassad prompt används inte

**Problem:** GAC använder fortfarande standardformat.

**Lösning:**

1. Kontrollera att `GAC_SYSTEM_PROMPT_PATH` är korrekt inställd:

   ```bash
   gac config get GAC_SYSTEM_PROMPT_PATH
   ```

2. Verifiera att filsökvägen existerar och är läsbar:

   ```bash
   cat "$GAC_SYSTEM_PROMPT_PATH"
   ```

3. Kontrollera `.gac.env` filer i denna ordning:
   - Projekt-nivå: `./.gac.env`
   - Användar-nivå: `~/.gac.env`
4. Försök med en absolut sökväg istället för relativ sökväg

### Språkkonfiguration

**Observera:** Du behöver inte en anpassad system prompt för att ändra commit-meddelandespråket!

Om du bara vill ändra språket på dina commit-meddelanden (medan du behåller standardformatet för konventionella commits), använd den interaktiva språkväljaren:

```bash
gac language
```

Detta kommer att presentera en interaktiv meny med 25+ språk i deras ursprungliga skript (Español, Français, 日本語, etc.). Välj ditt föredragna språk, så sätts `GAC_LANGUAGE` automatiskt i din `~/.gac.env` fil.

Alternativt kan du manuellt ställa in språket:

```bash
# I ~/.gac.env eller projekt-nivå .gac.env
GAC_LANGUAGE=Spanish
```

Som standard förblir konventionella commit-prefix (feat:, fix:, etc.) på engelska för kompatibilitet med changelog-verktyg och CI/CD pipelines, medan all annan text är på ditt specificerade språk.

**Vill du översätta prefixen också?** Ställ in `GAC_TRANSLATE_PREFIXES=true` i din `.gac.env` för fullständig lokalanpassning:

```bash
GAC_LANGUAGE=Spanish
GAC_TRANSLATE_PREFIXES=true
```

Detta kommer att översätta allt, inklusive prefix (t.ex. `corrección:` istället för `fix:`).

Detta är enklare än att skapa en anpassad system prompt om språk är din enda anpassningsbehov.

### Vill byta tillbaka till standard

**Problem:** Vill tillfälligt använda standard prompter.

**Lösning:**

```bash
# Alternativ 1: Avinstallera miljövariabeln
gac config unset GAC_SYSTEM_PROMPT_PATH

# Alternativ 2: Kommentera ut den i .gac.env
# GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt

# Alternativ 3: Använd en annan .gac.env för specifika projekt
```

---

## Relaterad dokumentation

- [USAGE.md](USAGE.md) - Kommandoradsflaggor och alternativ
- [README.md](../../README.md) - Installation och grundläggande installation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Allmän felsökning

## Behöver hjälp?

- Rapportera ärenden: [GitHub Issues](https://github.com/cellwebb/gac/issues)
- Dela dina anpassade prompter: Bidrag välkomna!
