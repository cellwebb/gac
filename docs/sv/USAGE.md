# gac Kommandoradsanvändning

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | **Svenska** | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

Det här dokumentet beskriver alla tillgängliga flaggor och alternativ för `gac` CLI-verktyget.

## Innehållsförteckning

- [gac Kommandoradsanvändning](#gac-kommandoradsanvändning)
  - [Innehållsförteckning](#innehållsförteckning)
  - [Grundläggande användning](#grundläggande-användning)
  - [Kärnarbetsflödesflaggor](#kärnarbetsflödesflaggor)
  - [Meddelandeanpassning](#meddelandeanpassning)
  - [Output och detaljnivå](#output-och-detaljnivå)
  - [Hjälp och version](#hjälp-och-version)
  - [Exempelarbetsflöden](#exempelarbetsflöden)
  - [Avancerat](#avancerat)
    - [Hoppa över Pre-commit och Lefthook Hooks](#hoppa-över-pre-commit-och-lefthook-hooks)
  - [Konfigurationsanteckningar](#konfigurationsanteckningar)
    - [Avancerade konfigurationsalternativ](#avancerade-konfigurationsalternativ)
    - [Konfigurationsunderkommandon](#konfigurationsunderkommandon)
  - [Få hjälp](#få-hjälp)

## Grundläggande användning

```sh
gac init
# Följ sedan prompterna för att konfigurera din leverantör, modell och API-nycklar interaktivt
gac
```

Genererar ett LLM-driven commit-meddelande för stageade ändringar och frågar efter bekräftelse. Bekräftelseprompten accepterar:

- `y` eller `yes` - Fortsätt med commiten
- `n` eller `no` - Avbryt commiten
- `r` eller `reroll` - Regenerera commit-meddelandet med samma kontext
- `e` eller `edit` - Redigera commit-meddelandet på plats med rich terminalredigering (vi/emacs tangentbindningar)
- Valfri annan text - Regenerera med den texten som feedback (t.ex. `gör det kortare`, `fokusera på prestanda`)
- Tom input (bara Enter) - Visa prompten igen

---

## Kärnarbetsflödesflaggor

| Flagga / Alternativ  | Kort | Beskrivning                                                                |
| -------------------- | ---- | -------------------------------------------------------------------------- |
| `--add-all`          | `-a` | Stagea alla ändringar innan commit                                         |
| `--group`            | `-g` | Gruppera stageade ändringar i flera logiska commits                        |
| `--push`             | `-p` | Pusha ändringar till remote efter commit                                   |
| `--yes`              | `-y` | Automatiskt bekräfta commit utan prompt                                    |
| `--dry-run`          |      | Visa vad som skulle hända utan att göra några ändringar                    |
| `--message-only`     |      | Skriv bara ut det genererade commit-meddelandet utan att faktiskt committa |
| `--no-verify`        |      | Hoppa över pre-commit och lefthook hooks vid commit                        |
| `--skip-secret-scan` |      | Hoppa över säkerhetsskanning för hemligheter i stageade ändringar          |

**Obs:** Kombinera `-a` och `-g` (dvs. `-ag`) för att stagea ALLA ändringar först, sedan gruppera dem i commits.

**Obs:** När du använder `--group`, skalas max output tokens-gränsen automatiskt baserat på antalet filer som committas (2x för 1-9 filer, 3x för 10-19 filer, 4x för 20-29 filer, 5x för 30+ filer). Detta säkerställer att LLM:n har tillräckligt med tokens för att generera alla grupperade commits utan trunkering, även för stora ändringsuppsättningar.

**Obs:** `--message-only` och `--group` är ömsesidigt uteslutande. Använd `--message-only` när du vill hämta commit-meddelandet för extern bearbetning, och `--group` när du vill organisera flera commits inom det aktuella git‑arbetsflödet.

## Meddelandeanpassning

| Flagga / Alternativ  | Kort | Beskrivning                                                                   |
| -------------------- | ---- | ----------------------------------------------------------------------------- |
| `--one-liner`        | `-o` | Generera ett enrads commit-meddelande                                         |
| `--verbose`          | `-v` | Generera detaljerade commit-meddelanden med motivation, arkitektur & påverkan |
| `--hint <text>`      | `-h` | Lägg till en ledtråd för att guida LLM:n                                      |
| `--model <modell>`   | `-m` | Specificera modellen att använda för denna commit                             |
| `--language <språk>` | `-l` | Åsidosätt språket (namn eller kod: 'Spanish', 'es', 'sv', 'ja')               |
| `--scope`            | `-s` | Härled ett lämpligt scope för commiten                                        |

**Obs:** Du kan ge feedback interaktivt genom att helt enkelt skriva den vid bekräftelseprompten - inget behov att prefixa med 'r'. Skriv `r` för en enkel regenerering, `e` för att redigera på plats med vi/emacs tangentbindningar, eller skriv din feedback direkt som `gör det kortare`.

## Output och detaljnivå

| Flagga / Alternativ  | Kort | Beskrivning                                                       |
| -------------------- | ---- | ----------------------------------------------------------------- |
| `--quiet`            | `-q` | Dämpa all output utom fel                                         |
| `--log-level <nivå>` |      | Ställ in loggnivå (debug, info, warning, error)                   |
| `--show-prompt`      |      | Skriv ut LLM-prompten som används för commit-meddelandegenerering |

## Hjälp och version

| Flagga / Alternativ | Kort | Beskrivning                      |
| ------------------- | ---- | -------------------------------- |
| `--version`         |      | Visa gac version och avsluta     |
| `--help`            |      | Visa hjälpmeddelande och avsluta |

---

## Exempelarbetsflöden

- **Stagea alla ändringar och commit:**

  ```sh
  gac -a
  ```

- **Commit och push i ett steg:**

  ```sh
  gac -ap
  ```

- **Generera ett enrads commit-meddelande:**

  ```sh
  gac -o
  ```

- **Generera ett detaljerat commit-meddelande med strukturerade sektioner:**

  ```sh
  gac -v
  ```

- **Lägg till en ledtråd för LLM:n:**

  ```sh
  gac -h "Refaktorisera autentiseringslogik"
  ```

- **Härled scope för commiten:**

  ```sh
  gac -s
  ```

- **Gruppera stageade ändringar i logiska commits:**

  ```sh
  gac -g
  # Grupperar endast de filer du redan har stageade
  ```

- **Gruppera alla ändringar (stageade + unstageda) och auto-bekräfta:**

  ```sh
  gac -agy
  # Stagear allt, grupperar det och auto-bekräftar
  ```

- **Använd en specifik modell för denna commit:**

  ```sh
  gac -m anthropic:claude-haiku-4-5
  ```

- **Generera commit-meddelande på ett specifikt språk:**

  ```sh
  # Använda språkkoder (kortare)
  gac -l sv
  gac -l ja
  gac -l es

  # Använda fullständiga namn
  gac -l "Svenska"
  gac -l Japanese
  gac -l Spanish
  ```

- **Testkörning (se vad som skulle hända):**

  ```sh
  gac --dry-run
  ```

- **Hämta endast commit-meddelandet (för skriptintegration):**

  ```sh
  gac --message-only
  # Exempelutdata: feat: add user authentication system
  ```

- **Hämta commit-meddelandet i enradsformat:**

  ```sh
  gac --message-only --one-liner
  # Exempelutdata: feat: add user authentication system
  ```

## Avancerat

- Kombinera flaggor för mer kraftfulla arbetsflöden (t.ex. `gac -ayp` för att stagea, auto-bekräfta och pusha)
- Använd `--show-prompt` för att felsöka eller granska prompten som skickas till LLM:n
- Justera detaljnivån med `--log-level` eller `--quiet`

### Hoppa över Pre-commit och Lefthook Hooks

Flaggan `--no-verify` gör att du kan hoppa över alla pre-commit eller lefthook hooks som är konfigurerade i ditt projekt:

```sh
gac --no-verify  # Hoppa över alla pre-commit och lefthook hooks
```

**Använd `--no-verify` när:**

- Pre-commit eller lefthook hooks misslyckas tillfälligt
- Arbeta med tidskrävande hooks
- Committa pågående arbete som inte klarar alla kontroller ännu

**Obs:** Använd med försiktighet eftersom dessa hooks upprätthåller kodkvalitetsstandarder.

### Säkerhetsskanning

gac inkluderar inbyggd säkerhetsskanning som automatiskt upptäcker potentiella hemligheter och API-nycklar i dina stageade ändringar innan commit. Detta hjälper till att förhindra att du oavsiktligt committar känslig information.

**Hoppa över säkerhetsskanningar:**

```sh
gac --skip-secret-scan  # Hoppa över säkerhetsskanning för denna commit
```

**För att inaktivera permanent:** Ställ in `GAC_SKIP_SECRET_SCAN=true` i din `.gac.env` fil.

**När man ska hoppa över:**

- Committa exempelkod med platshållarnycklar
- Arbeta med testfixtures som innehåller dummy-inloggningsuppgifter
- När du har verifierat att ändringarna är säkra

**Obs:** Scannern använder mönstermatching för att upptäcka vanliga hemlighetsformat. Granska alltid dina stageade ändringar innan du committar.

## Konfigurationsanteckningar

- Det rekommenderade sättet att konfigurera gac är att köra `gac init` och följa de interaktiva prompterna.
- Redan konfigurerat språk och bara behöver byta leverantör eller modell? Kör `gac model` för att upprepa installationen utan språkfrågor.
- **Använder Claude Code?** Se [Claude Code installationsguide](CLAUDE_CODE.md) för OAuth-autentiseringsinstruktioner.
- gac laddar konfigurationen i följande prioritetsordning:
  1. CLI-flaggor
  2. Miljövariabler
  3. Projekt-nivå `.gac.env`
  4. Användar-nivå `~/.gac.env`

### Avancerade konfigurationsalternativ

Du kan anpassa gacs beteende med dessa valfria miljövariabler:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Härled automatiskt och inkludera scope i commit-meddelanden (t.ex. `feat(auth):` vs `feat:`)
- `GAC_VERBOSE=true` - Generera detaljerade commit-meddelanden med motivation, arkitektur och påverkanssektioner
- `GAC_TEMPERATURE=0.7` - Kontrollera LLM:s kreativitet (0.0-1.0, lägre = mer fokuserad)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Maximalt antal tokens för genererade meddelanden (automatiskt skalat 2-5x vid användning av `--group` baserat på filantal; åsidosätt för att gå högre eller lägre)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Varna när prompter överskrider denna tokenräkning
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Använd en anpassad systemprompt för commit-meddelande generation
- `GAC_LANGUAGE=Swedish` - Generera commit-meddelanden på ett specifikt språk (t.ex. Spanish, French, Japanese, German). Stöder fullständiga namn eller ISO-koder (es, fr, ja, de, sv, zh-CN). Använd `gac language` för interaktivt val
- `GAC_TRANSLATE_PREFIXES=true` - Översätt konventionella commit-prefix (feat, fix, etc.) till målspråket (standard: false, behåller prefix på engelska)
- `GAC_SKIP_SECRET_SCAN=true` - Inaktivera automatisk säkerhetsskanning för hemligheter i stageade ändringar (använd med försiktighet)
- `GAC_NO_TIKTOKEN=true` - Håll dig helt offline genom att hoppa över `tiktoken`-nedladdningssteget och använda den inbyggda grova token-uppskattningen

Se `.gac.env.example` för en komplett konfigurationsmall.

För detaljerad vägledning om hur man skapar anpassade systemprompter, se [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md).

### Konfigurationsunderkommandon

Följande underkommandon är tillgängliga:

- `gac init` — Interaktiv installationsguide för leverantör, modell och språk
- `gac model` — Leverantör/modell/API-nyckel konfiguration utan språkprompter (idealiskt för snabba byten)
- `gac auth` — Autentisera eller återautentisera Claude Code OAuth-token (användbart när token löper ut)
- `gac config show` — Visa nuvarande konfiguration
- `gac config set KEY VALUE` — Ställ in konfigurationsnyckel i `$HOME/.gac.env`
- `gac config get KEY` — Hämta konfigurationsvärde
- `gac config unset KEY` — Ta bort konfigurationsnyckel från `$HOME/.gac.env`
- `gac language` (eller `gac lang`) — Interaktiv språkväljare för commit-meddelanden (ställer in GAC_LANGUAGE)
- `gac diff` — Visa filtrerad git diff med alternativ för staged/unstaged ändringar, färg och trunkering

## Få hjälp

- För anpassade systemprompter, se [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- För felsökning och avancerade tips, se [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- För installation och konfiguration, se [README.md#installation-and-configuration](README.md#installation-and-configuration)
- För att bidra, se [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Licensinformation: [LICENSE](LICENSE)
