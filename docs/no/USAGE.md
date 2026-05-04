# gac kommandolinje bruk

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | **Norsk** | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

Dette dokumentet beskriver alle tilgjengelige flagg og alternativer for `gac` CLI-verktøyet.

## Innholdsfortegnelse

- [gac kommandolinje bruk](#gac-kommandolinje-bruk)
  - [Innholdsfortegnelse](#innholdsfortegnelse)
  - [Grunnleggende Bruk](#grunnleggende-bruk)
  - [Kjerne-workflow-flagg](#kjerne-workflow-flagg)
  - [Meldingstilpasning](#meldingstilpasning)
  - [Output og detaljnivå](#output-og-detaljnivå)
  - [Hjelp og versjon](#hjelp-og-versjon)
  - [Eksempel-workflows](#eksempel-workflows)
  - [Avansert](#avansert)
    - [Hoppe over Pre-commit og Lefthook Hooks](#hoppe-over-pre-commit-og-lefthook-hooks)
    - [Sikkerhetsskanning](#sikkerhetsskanning)
    - [SSL-sertifikatverifisering](#ssl-sertifikatverifisering)
  - [Konfigurasjonsnotater](#konfigurasjonsnotater)
    - [Avanserte Konfigurasjonsalternativer](#avanserte-konfigurasjonsalternativer)
    - [Konfigurasjons-underkommandoer](#konfigurasjons-underkommandoer)
  - [Interaktiv Modus](#interaktiv-modus)
    - [Hvordan det fungerer](#hvordan-det-fungerer)
    - [Når du skal bruke interaktiv modus](#når-du-skal-bruke-interaktiv-modus)
    - [Brukseksempler](#brukseksempler)
    - [Spørsmål-Svar Workflow](#spørsmål-svar-workflow)
    - [Kombinasjon med andre flagg](#kombinasjon-med-andre-flagg)
    - [Beste Praksis](#beste-praksis)
  - [Bruksstatistikk](#bruksstatistikk)
  - [Få Hjelp](#få-hjelp)

## Grunnleggende Bruk

```sh
gac init
# Følg deretter instruksjonene for å konfigurere din provider, modell og API-nøkler interaktivt
gac
```

Genererer en LLM-drevet commit-melding for staged endringer og ber om bekreftelse. Bekreftelsesprompten aksepterer:

- `y` eller `yes` - Fortsett med commit
- `n` eller `no` - Avbryt commit
- `r` eller `reroll` - Regenerer commit-meldingen med samme kontekst
- `e` eller `edit` - Rediger commit-meldingen. Som standard åpnes en innebygd TUI med vi/emacs-tastebindinger. Sett `GAC_EDITOR` for å åpne din foretrukne editor i stedet (f.eks. `GAC_EDITOR=code gac` for VS Code, `GAC_EDITOR=vim gac` for vim)
- Alt annen tekst - Regenerer med den teksten som feedback (f.eks. `gjør det kortere`, `fokuser på ytelse`)
- Tom input (bare Enter) - Vis prompten igjen

---

## Kjerne-workflow-flagg

| Flagg / Alternativ   | Kort | Beskrivelse                                                       |
| -------------------- | ---- | ----------------------------------------------------------------- |
| `--add-all`          | `-a` | Stage alle endringer før committing                               |
| `--group`            | `-g` | Grupperte staged endringer i flere logiske commits                |
| `--push`             | `-p` | Push endringer til remote etter committing                        |
| `--yes`              | `-y` | Bekreft commit automatisk uten prompting                          |
| `--dry-run`          |      | Vis hva som ville skjedd uten å gjøre endringer                   |
| `--message-only`     |      | Output kun den genererte commit-meldingen uten committing         |
| `--no-verify`        |      | Hopp over pre-commit og lefthook hooks ved committing             |
| `--skip-secret-scan` |      | Hopp over sikkerhetsskanning for hemmeligheter i staged endringer |
| `--no-verify-ssl`    |      | Hopp over SSL-sertifikatverifisering (nyttig for bedriftsproxyer) |
| `--signoff`          |      | Legg til Signed-off-by-linje i commit-meldingen (DCO-samsvar)     |
| `--interactive`      | `-i` | Still spørsmål om endringer for bedre commits                     |

**Merknad:** Kombiner `-a` og `-g` (dvs. `-ag`) for å stage ALLE endringer først, deretter gruppere dem i commits.

**Merknad:** Når du bruker `--group`, blir maks output tokens grense automatisk skalert basert på antall filer som committes (2x for 1-9 filer, 3x for 10-19 filer, 4x for 20-29 filer, 5x for 30+ filer). Dette sikrer at LLM har nok tokens til å generere alle grupperte commits uten trunkering, selv for store endringssett.

**Merknad:** `--message-only` og `--group` er gjensidig eksklusive. Bruk `--message-only` når du vil få commit-meldingen for ekstern behandling, og `--group` når du vil organisere flere commits i den nåværende git-workflowen.

**Note:** `--interactive` flag gir LLM ekstra kontekst ved å stille spørsmål om endringene dine, noe som fører til mer nøyaktige og detaljerte commit-meldinger. Dette er spesielt nyttig for komplekse endringer eller når du vil sørge for at commit-meldingen fanger hele konteksten av arbeidet ditt.

## Meldingstilpasning

| Flagg / Alternativ   | Kort | Beskrivelse                                                                 |
| -------------------- | ---- | --------------------------------------------------------------------------- |
| `--one-liner`        | `-o` | Generer en enkeltlinjes commit-melding                                      |
| `--verbose`          | `-v` | Generer detaljerte commit-meldinger med motivasjon, arkitektur & påvirkning |
| `--hint <tekst>`     | `-h` | Legg til et hint for å guide LLM-en                                         |
| `--model <modell>`   | `-m` | Spesifiser modellen som skal brukes for denne commit                        |
| `--language <språk>` | `-l` | Overstyr språket (navn eller kode: 'Norsk', 'nb', 'sv', 'da')               |
| `--scope`            | `-s` | Utled et passende scope for commiten                                        |
| `--50-72`            |      | Anvende 50/72-regelen for commit-meldingformatering                         |

**Merknad:** `--50-72` flagget anvender [50/72-regelen](https://www.conventionalcommits.org/en/v1.0.0/#summary) hvor:

- Emnelinje: maksimum 50 tegn
- Brødtekstlinjer: maksimum 72 tegn per linje
- Dette holder commit-meldinger lesbare i `git log --oneline` og GitHub's UI

Du kan også sette `GAC_USE_50_72_RULE=true` i `.gac.env` filen din for å alltid anvende denne regelen.

**Merknad:** Du kan gi feedback interaktivt ved å skrive det direkte i bekreftelsesprompten - ingen 'r'-prefiks nødvendig. Skriv `r` for en enkel reroll, `e` for å redigere meldingen (innebygd TUI som standard, eller din `$GAC_EDITOR` hvis satt), eller skriv feedbacken din direkte som `gjør det kortere`.

## Output og detaljnivå

| Flagg / Alternativ    | Kort | Beskrivelse                                               |
| --------------------- | ---- | --------------------------------------------------------- |
| `--quiet`             | `-q` | Undertrykk all output unntatt feil                        |
| `--log-level <level>` |      | Sett loggnivå (debug, info, warning, error)               |
| `--show-prompt`       |      | Skriv ut LLM-prompten brukt for commit-meldingsgenerering |

## Hjelp og versjon

| Flagg / Alternativ | Kort | Beskrivelse                  |
| ------------------ | ---- | ---------------------------- |
| `--version`        |      | Vis gac-versjon og avslutt   |
| `--help`           |      | Vis hjelpemelding og avslutt |

---

## Eksempel-workflows

- **Stage alle endringer og commit:**

  ```sh
  gac -a
  ```

- **Commit og push i ett steg:**

  ```sh
  gac -ap
  ```

- **Generer en enkeltlinjes commit-melding:**

  ```sh
  gac -o
  ```

- **Generer en detaljert commit-melding med strukturerte seksjoner:**

  ```sh
  gac -v
  ```

- **Legg til et hint for LLM-en:**

  ```sh
  gac -h "Refaktorer autentiseringslogikk"
  ```

- **Utled scope for commitet:**

  ```sh
  gac -s
  ```

- **Grupperte staged endringer i logiske commits:**

  ```sh
  gac -g
  # Grupperer kun filene du allerede har staged
  ```

- **Grupper alle endringer (staged + unstaged) og auto-bekreft:**

  ```sh
  gac -agy
  # Stager alt, grupperer det og bekrefter automatisk
  ```

- **Bruk en spesifikk modell kun for denne commit:**

  ```sh
  gac -m anthropic:claude-haiku-4-5
  ```

- **Generer commit-melding på et spesifikt språk:**

  ```sh
  # Bruker språkkoder (kortere)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # Bruker fulle navn
  gac -l "Forenklet Kinesisk"
  gac -l Japansk
  gac -l Spansk
  ```

- **Tørrkjøring (se hva som ville skjedd):**

  ```sh
  gac --dry-run
  ```

- **Få kun commit-meldingen (for skript-integrasjon):**

  ```sh
  gac --message-only
  # Output: feat: legg til brukerautentiseringssystem
  ```

- **Få commit-melding i enkeltlinjeformat:**

  ```sh
  gac --message-only --one-liner
  # Output: feat: legg til brukerautentiseringssystem
  ```

- **Bruk interaktiv modus for å gi kontekst:**

  ```sh
  gac -i
  # Hva er hovedformålet med disse endringene?
  # Hvilket problem løser du?
  # Er det implementeringsdetaljer verdt å nevne?
  ```

- **Interaktiv modus med detaljert output:**

  ```sh
  gac -i -v
  # Still spørsmål og generer detaljert commit-melding
  ```

## Avansert

- Kombiner flagg for mer kraftfulle workflows (f.eks. `gac -ayp` for å stage, auto-bekrefte og pushe)
- Bruk `--show-prompt` for å debugge eller gjennomgå prompten sendt til LLM-en
- Juster detaljnivå med `--log-level` eller `--quiet`

### Hoppe over Pre-commit og Lefthook Hooks

`--no-verify`-flagget lar deg hoppe over alle pre-commit eller lefthook hooks konfigurert i prosjektet ditt:

```sh
gac --no-verify  # Hopp over alle pre-commit og lefthook hooks
```

**Bruk `--no-verify` når:**

- Pre-commit eller lefthook hooks feiler midlertidig
- Du jobber med tidkrevende hooks
- Du committer arbeid-på-gang-kode som ikke består alle sjekker ennå

**Merknad:** Bruk med forsiktighet da disse hooks vedlikeholder kodekvalitetsstandarder.

### Sikkerhetsskanning

gac inkluderer innebygd sikkerhetsskanning som automatisk oppdager potensielle hemmeligheter og API-nøkler i dine staged endringer før commit. Dette hjelper med å forhindre utilsiktet commit av sensitiv informasjon.

**Hoppe over sikkerhetsskanninger:**

```sh
gac --skip-secret-scan  # Hopp over sikkerhetsskanning for denne commit
```

**For å deaktivere permanent:** Sett `GAC_SKIP_SECRET_SCAN=true` i din `.gac.env`-fil.

**Når du skal hoppe over:**

- Committe av eksempelkode med plassholdernøkler
- Arbeide med test fixtures som inneholder dummy-credentials
- Når du har verifisert at endringene er trygge

**Merknad:** Skanneren bruker pattern matching for å oppdage vanlige hemmelighetsformater. Gjennomgå alltid dine staged endringer før commit.

### SSL-sertifikatverifisering

`--no-verify-ssl`-flagget lar deg hoppe over SSL-sertifikatverifisering for API-kall:

```sh
gac --no-verify-ssl  # Hopp over SSL-verifisering for denne commit
```

**For å sette permanent:** Sett `GAC_NO_VERIFY_SSL=true` i din `.gac.env`-fil.

**Bruk `--no-verify-ssl` når:**

- Bedriftsproxyer avlytter SSL-trafikk (MITM-proxyer)
- Utviklingsmiljøer bruker selv-signerte sertifikater
- Du møter SSL-sertifikatfeil på grunn av nettverkssikkerhetsinnstillinger

**Merknad:** Bruk kun dette alternativet i pålitelige nettverksmiljøer. Deaktivering av SSL-verifisering reduserer sikkerheten og kan gjøre API-forespørslene dine sårbare for man-in-the-middle-angrep.

### Signed-off-by-linje (DCO-samsvar)

gac støtter å legge til en `Signed-off-by`-linje i commit-meldinger, som er påkrevd for [Developer Certificate of Origin (DCO)](https://developercertificate.org/)-samsvar i mange open source-prosjekter.

**Legg til signoff :**

```sh
gac --signoff  # Legg til Signed-off-by-linje i commit-meldingen (DCO-samsvar)
```

**For å aktivere permanent :** Sett `GAC_SIGNOFF=true` i `.gac.env`-filen din, eller legg til `signoff=true` i konfigurasjonen din.

**Hva den gjør :**

- Legger til `Signed-off-by: Ditt Navn <din.email@example.com>` i commit-meldingen
- Bruker git-konfigurasjonen din (`user.name` og `user.email`) til linjen
- Påkrevd for prosjekter som Cherry Studio, Linux-kjernen og andre som bruker DCO

**Git-identitetsoppsett :**

Sørg for at git-konfigurasjonen din har riktig navn og e-post :

```sh
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"
```

**Merknad :** Signed-off-by-linjen legges til av git under commit, ikke av AI under meldingsgenerering. Du vil ikke se den i forhåndsvisningen, men den vil være i den endelige commiten (sjekk med `git log -1`).

## Konfigurasjonsnotater

- Den anbefalte måten å sette opp gac er å kjøre `gac init` og følge de interaktive promptene.
- Allerede konfigurert språk og trenger bare å bytte provider eller modeller? Kjør `gac model` for å gjenta oppsettet uten språkspørsmål.
- **Bruker Claude Code?** Se [Claude Code oppsettguide](CLAUDE_CODE.md) for OAuth-autentiseringsinstruksjoner.
- gac laster konfigurasjon i følgende prioriteringsrekkefølge:
  1. CLI-flagg
  2. Miljøvariabler
  3. Prosjektnivå `.gac.env`
  4. Brukernivå `~/.gac.env`

### Avanserte Konfigurasjonsalternativer

Du kan tilpasse gac sitt oppførsel med disse valgfrie miljøvariablene:

- `GAC_EDITOR=code --wait` - Overstyr editoren som brukes når du trykker `e` i bekreftelsesprompten. Som standard åpner `e` en innebygd TUI; ved å sette `GAC_EDITOR` bytter du til en ekstern editor. Støtter enhver editorkommando med argumenter. Venteflagg (`--wait`/`-w`) settes automatisk inn for kjente GUI-editorer (VS Code, Cursor, Zed, Sublime Text) slik at prosessen blokkeres til du lukker filen
- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Utled automatisk og inkluder scope i commit-meldinger (f.eks. `feat(auth):` vs `feat:)
- `GAC_VERBOSE=true` - Generer detaljerte commit-meldinger med motivasjon, arkitektur og påvirkningseksjoner
- `GAC_USE_50_72_RULE=true` - Alltid anvende 50/72-regelen for commit-meldinger (emne ≤50 tegn, brødtekstlinjer ≤72 tegn)
- `GAC_SIGNOFF=true` - Alltid legg til Signed-off-by-linje i commits (for DCO-samsvar)
- `GAC_TEMPERATURE=0.7` - Kontroller LLM-kreativitet (0.0-1.0, lavere = mer fokusert)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Maksimum tokens for genererte meldinger (automatisk skalert 2-5x når du bruker `--group` basert på filantall; overstyr for å gå høyere eller lavere)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Varsel når prompter overstiger dette tokenantallet
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Bruk et egendefinert systemprompt for commit-meldingsgenerering
- `GAC_LANGUAGE=Norwegian` - Generer commit-meldinger på et spesifikt språk (f.eks. Norwegian, French, Japanese, German). Støtter fulle navn eller ISO-koder (nb, fr, ja, de, zh-CN). Bruk `gac language` for interaktivt valg
- `GAC_TRANSLATE_PREFIXES=true` - Oversett konvensjonelle commit-prefikser (feat, fix, etc.) til målspråket (default: false, beholder prefikser på engelsk)
- `GAC_SKIP_SECRET_SCAN=true` - Deaktiver automatisk sikkerhetsskanning for hemmeligheter i staged endringer (bruk med forsiktighet)
- `GAC_NO_VERIFY_SSL=true` - Hopp over SSL-sertifikatverifisering for API-kall (nyttig for bedriftsproxyer som avlytter SSL-trafikk)
- `GAC_DISABLE_STATS=true` - Deaktiver sporing av bruksstatistikk (ingen lesing eller skriving av statistikkfil; eksisterende data bevares). Bare truthy-verdier deaktiverer statistikk; å sette den til `false`/`0`/`no`/`off` holder statistikk aktivert, det samme som å la variabelen være udefinert

Se `.gac.env.example` for en komplett konfigurasjonsmal.

For detaljert veiledning for å lage egendefinerte systemprompts, se [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md).

### Konfigurasjons-underkommandoer

Følgende underkommandoer er tilgjengelige:

- `gac init` — Interaktiv oppsettsguide for provider, modell og språkkonfigurasjon
- `gac model` — Provider/modell/API-nøkkel oppsett uten språkprompts (ideelt for raske bytter)
- `gac auth` — Vis OAuth-autentiseringsstatus for alle leverandører
- `gac auth claude-code login` — Logg inn på Claude Code med OAuth (åpner nettleser)
- `gac auth claude-code logout` — Logg ut av Claude Code og fjern lagret token
- `gac auth claude-code status` — Sjekk Claude Code-autentiseringsstatus
- `gac config show` — Vis nåværende konfigurasjon
- `gac config set KEY VALUE` — Sett en konfigurasjonsnøkkel i `$HOME/.gac.env`
- `gac config get KEY` — Hent en konfigurasjonsverdi
- `gac config unset KEY` — Fjern en konfigurasjonsnøkkel fra `$HOME/.gac.env`
- `gac language` (eller `gac lang`) — Interaktivt språkvalg for commit-meldinger (setter GAC_LANGUAGE)
- `gac diff` — Vis filtrert git diff med alternativer for staged/unstaged endringer, farge og trunkering
- `gac serve` — Start GAC som [MCP-server](MCP.md) for AI-agent integrasjon (stdio transport)
- `gac stats show` — Vis din gac-bruksstatistikk (totaler, streaks, daglig & ukentlig aktivitet, tokenbruk, topprosjekter, toppmodeller)
- `gac stats project` — Vis statistikk kun for det nåværende git-prosjektet
- `gac stats reset` — Tilbakestill all statistikk til null (ber om bekreftelse)

## Interaktiv Modus

`--interactive` (`-i`) flagget forbedrer gac's commit-meldinggenerering ved å stille målrettede spørsmål om endringene dine. Denne ekstra konteksten hjelper LLM med å lage mer nøyaktige, detaljerte og kontekstilpassede commit-meldinger.

### Hvordan det fungerer

Når du bruker `--interactive`, vil gac stille spørsmål som:

- **Hva er hovedformålet med disse endringene?** - Hjelper med å forstå høynivåmålet
- **Hvilket problem løser du?** - Gir kontekst om motivasjonen
- **Er det implementasjonsdetaljer å nevne?** - Fanger tekniske spesifikasjoner
- **Er det breaking changes?** - Identifiserer potensielle impact-problemer
- **Er dette relatert til en issue eller ticket?** - Kobler til prosjektstyring

### Når du skal bruke interaktiv modus

Interaktiv modus er spesielt nyttig for:

- **Komplekse endringer** hvor konteksten ikke er klar fra diff-en alene
- **Refactoring-arbeid** som spenner over flere filer og konsepter
- **Nye funksjoner** som krever forklaring av overall formål
- **Bug fixes** hvor rotårsaken ikke er umiddelbart synlig
- **Ytelsesoptimalisering** hvor logikken ikke er åpenbar
- **Code review-forberedelse** - spørsmål hjelper deg å tenke over endringene dine

### Brukseksempler

**Basis interaktiv modus:**

```sh
gac -i
```

Dette vil:

1. Vise en oppsummering av staged endringer
2. Stille spørsmål om endringene
3. Generere en commit-melding med svarene dine
4. Be om bekreftelse (eller automatisk bekrefte når kombinert med `-y`)

**Interaktiv modus med staged endringer:**

```sh
gac -ai
# Stage alle endringer, still spørsmål for bedre kontekst
```

**Interaktiv modus med spesifikke hints:**

```sh
gac -i -h "Databasemigrering for brukerprofiler"
# Still spørsmål mens du gir et spesifikt hint for å fokusere LLM
```

**Interaktiv modus med detaljert output:**

```sh
gac -i -v
# Still spørsmål og generer en detaljert, strukturert commit-melding
```

**Automatisk bekreftet interaktiv modus:**

```sh
gac -i -y
# Still spørsmål men bekrefter resulterende commit automatisk
```

### Spørsmål-Svar Workflow

Den interaktive workflown følger dette mønsteret:

1. **Endringsgjennomgang** - gac viser en oppsummering av hva du committer
2. **Svar på spørsmål** - svar på hver prompt med relevante detaljer
3. **Kontekstforbedring** - svarene dine legges til LLM-prompten
4. **Meldingsgenerering** - LLM lager en commit-melding med full kontekst
5. **Bekreftelse** - gjennomgå og bekreft commit (eller automatisk med `-y`)

**Tips for nyttige svar:**

- **Konsis men komplett** - gi viktige detaljer uten å være overlydende verbose
- **Fokuser på "hvorfor"** - forklar resonnementet bak endringene dine
- **Nevn begrensninger** - noter begrensninger eller spesielle hensyn
- **Lenk til ekstern kontekst** - referer til issues, dokumentasjon, eller designdokumenter
- **Tomme svar er ok** - hvis et spørsmål ikke gjelder, bare trykk Enter

### Kombinasjon med andre flagg

Interaktiv modus fungerer godt med de fleste andre flagg:

```sh
# Stage alle endringer og still spørsmål
gac -ai

# Still spørsmål med detaljert output
gac -i -v
```

### Beste Praksis

- **Bruk for komplekse PR-er** - spesielt nyttig for pull requests som trenger detaljerte forklaringer
- **Teamsamarbeid** - spørsmål hjelper deg å tenke over endringer andre skal gjennomgå
- **Dokumentasjonsforberedelse** - svarene dine kan hjelpe med å danne grunnlag for release notes
- **Læringsverktøy** - spørsmål forsterker gode praksiser for commit-meldinger
- **Hopp over for enkle endringer** - for trivielle fixes kan basismodus være raskere

## Bruksstatistikk

gac sporer lettvektig bruksstatistikk slik at du kan se din commit-aktivitet, streaks, tokenbruk og mest aktive prosjekter og modeller. Statistikk lagres lokalt i `~/.gac_stats.json` og sendes aldri noe sted — det er ingen telemetri.

**Hva spores:** totalt antall gac-kjøringer, totalt antall committer, totale prompt- og completion-tokens, første/siste bruk-datoer, daglige og ukentlige tellinger (gacs, committer, tokens), nåværende og lengste streak, aktivitet per prosjekt (gacs, committer, prompt + completion-tokens) og aktivitet per modell (gacs, prompt + completion-tokens).

**Hva IKKE spores:** commit-meldinger, kodeinnhold, filstier, personlig informasjon eller noe utover tellinger, datoer, prosjektnavn (avledet fra git remote eller mappenavn) og modellnavn.

### Opt-in eller Opt-out

`gac init` spør om du vil aktivere statistikk og forklarer nøyaktig hva som lagres. Du kan når som helst ombestemme deg:

- **Aktiver statistikk:** fjern `GAC_DISABLE_STATS` eller sett den til `false`/`0`/`no`/`off`/tom.
- **Deaktiver statistikk:** sett `GAC_DISABLE_STATS` til en truthy-verdi (`true`, `1`, `yes`, `on`).

Når du avslår statistikk under `gac init` og en eksisterende `~/.gac_stats.json` oppdages, blir du tilbudt muligheten til å slette den.

### Statistikk-underkommandoer

| Kommando            | Beskrivelse                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `gac stats`         | Vis din statistikk (samme som `gac stats show`)                                                                   |
| `gac stats show`    | Vis fullstendig statistikk: totaler, streaks, daglig & ukentlig aktivitet, tokenbruk, topprosjekter, toppmodeller |
| `gac stats project` | Vis statistikk kun for det nåværende git-prosjektet                                                               |
| `gac stats reset`   | Tilbakestill all statistikk til null (ber om bekreftelse)                                                         |

### Eksempler

```sh
# Vis din totale statistikk
gac stats

# Statistikk kun for nåværende prosjekt
gac stats project

# Tilbakestill all statistikk (med bekreftelsesprompt)
gac stats reset
```

### Hva du vil se

Å kjøre `gac stats` viser:

- **Totalt antall gacs og committer** — hvor mange ganger du har brukt gac og hvor mange committer det har opprettet
- **Nåværende og lengste streak** — etterfølgende dager med gac-aktivitet (🔥 ved 5+ dager)
- **Aktivitetssammendrag** — dagens og denne ukens gacs, committer og tokens sammenlignet med din toppedag og toppeuke
- **Topprosjekter** — dine 5 mest aktive repos etter gac- + commit-antall, med tokenbruk per prosjekt
- **Toppmodeller** — dine 5 mest brukte modeller med prompt-, completion- og totale tokens forbruk
- **Highscore-feiringer** — 🏆 trofeer når du setter nye daglige, ukentlige, token- eller streak-rekorder; 🥈 for å tangere dem
- **Oppmuntringsmeldinger** — kontekstuelle oppmuntringer basert på din aktivitet

### Deaktivere statistikk

Sett miljøvariabelen `GAC_DISABLE_STATS` til en truthy-verdi:

```sh
# Deaktiver statistikksporing
export GAC_DISABLE_STATS=true

# Eller i .gac.env
GAC_DISABLE_STATS=true
```

Falsy-verdier (`false`, `0`, `no`, `off`, tom) holder statistikk aktivert — det samme som å la variabelen være udefinert.

Når deaktivert, hopper gac over all statistikkregistrering — ingen fillesing eller skriving skjer. Eksisterende data bevares men oppdateres ikke før du reaktiverer dem.

---

## Få Hjelp

- For MCP-server oppsett (AI-agent integrasjon), se [docs/MCP.md](MCP.md)
- For egendefinerte systemprompts, se [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- For feilsøking og avanserte tips, se [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- For installasjon og konfigurasjon, se [README.md#installation-and-configuration](README.md#installation-and-configuration)
- For å bidra, se [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Lisensinformasjon: [LICENSE](LICENSE)
