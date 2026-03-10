# Bruke GAC som MCP-server

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | **Norsk** | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC kan kjores som en [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)-server, som lar AI-agenter og editorer generere commits gjennom strukturerte verktoyskall i stedet for shell-kommandoer.

## Innholdsfortegnelse

- [Bruke GAC som MCP-server](#bruke-gac-som-mcp-server)
  - [Innholdsfortegnelse](#innholdsfortegnelse)
  - [Hva er MCP?](#hva-er-mcp)
  - [Fordeler](#fordeler)
  - [Oppsett](#oppsett)
    - [Claude Code](#claude-code)
    - [Claude Desktop](#claude-desktop)
    - [Cursor](#cursor)
    - [Andre MCP-klienter](#andre-mcp-klienter)
  - [Tilgjengelige verktoy](#tilgjengelige-verktoy)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Arbeidsflyter](#arbeidsflyter)
    - [Enkel commit](#enkel-commit)
    - [Forhandsvisning for commit](#forhandsvisning-for-commit)
    - [Grupperte commits](#grupperte-commits)
    - [Commit med kontekst](#commit-med-kontekst)
  - [Konfigurasjon](#konfigurasjon)
  - [Feilsoking](#feilsoking)
  - [Se ogsa](#se-ogsa)

## Hva er MCP?

Model Context Protocol er en apen standard som lar AI-applikasjoner kalle eksterne verktoy gjennom et strukturert grensesnitt. Ved a kjore GAC som MCP-server kan enhver MCP-kompatibel klient inspisere repository-status og opprette AI-drevne commits uten a kjore shell-kommandoer direkte.

## Fordeler

- **Strukturert interaksjon**: Agenter kaller typede verktoy med validerte parametere i stedet for a tolke shell-utdata
- **To-verktoys arbeidsflyt**: `gac_status` for a inspisere, `gac_commit` for a handle - en naturlig tilpasning for agentresonnering
- **Fulle GAC-funksjoner**: AI-commit-meldinger, grupperte commits, hemmelighetsscanning og push - alt tilgjengelig via MCP
- **Ingen ekstra konfigurasjon**: Serveren bruker din eksisterende GAC-konfigurasjon (`~/.gac.env`, leverandorinnstillinger osv.)

## Oppsett

MCP-serveren startes med `gac serve` og kommuniserer over stdio, standard MCP-transport.

### Claude Code

Legg til i prosjektets `.mcp.json` eller globale `~/.claude/claude_code_config.json`:

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

Eller hvis du har GAC installert globalt:

```json
{
  "mcpServers": {
    "gac": {
      "command": "gac",
      "args": ["serve"]
    }
  }
}
```

### Claude Desktop

Legg til i Claude Desktop-konfigurasjonsfilen din (`~/Library/Application Support/Claude/claude_desktop_config.json` pa macOS, `%APPDATA%\Claude\claude_desktop_config.json` pa Windows):

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### Cursor

Legg til i Cursor MCP-innstillingene dine (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### Andre MCP-klienter

Enhver MCP-kompatibel klient kan bruke GAC. Serverens inngangspunkt er:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

Hvis du har GAC installert (via `uv tool install gac`), kan du bruke `gac` direkte i stedet for `uvx gac`.

## Tilgjengelige verktoy

Serveren eksponerer to verktoy:

### gac_status

Inspiser repository-statusen. Bruk dette for commit for a forsta hva som vil bli committet.

**Parametere:**

| Parameter           | Type                                    | Default     | Beskrivelse                            |
| ------------------- | --------------------------------------- | ----------- | -------------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Utdataformat                           |
| `include_diff`      | bool                                    | `false`     | Inkluder fullt diff-innhold            |
| `include_stats`     | bool                                    | `true`      | Inkluder statistikk for linjeendringer |
| `include_history`   | int                                     | `0`         | Antall nylige commits a inkludere      |
| `staged_only`       | bool                                    | `false`     | Vis bare stagede endringer             |
| `include_untracked` | bool                                    | `true`      | Inkluder usporede filer                |
| `max_diff_lines`    | int                                     | `500`       | Begrens diff-utdata (0 = ubegrenset)   |

**Returnerer:** Branch-navn, filstatus (staget/ustaget/usporet/konflikter), valgfritt diff-innhold, valgfri statistikk og valgfri commit-historikk.

### gac_commit

Generer en AI-drevet commit-melding og utfor eventuelt committen.

**Parametere:**

| Parameter          | Type           | Default | Beskrivelse                                                 |
| ------------------ | -------------- | ------- | ----------------------------------------------------------- |
| `stage_all`        | bool           | `false` | Stage alle endringer for commit (`git add -A`)              |
| `files`            | list[str]      | `[]`    | Spesifikke filer a stage                                    |
| `dry_run`          | bool           | `false` | Forhandsvisning uten utforelse                              |
| `message_only`     | bool           | `false` | Generer melding uten a committe                             |
| `push`             | bool           | `false` | Push til remote etter commit                                |
| `group`            | bool           | `false` | Del endringer inn i flere logiske commits                   |
| `one_liner`        | bool           | `false` | Enlinjers commit-melding                                    |
| `scope`            | string \| null | `null`  | Conventional commit scope (auto-detektert hvis ikke angitt) |
| `hint`             | string         | `""`    | Ekstra kontekst for bedre meldinger                         |
| `model`            | string \| null | `null`  | Overstyr AI-modell (`provider:model_name`)                  |
| `language`         | string \| null | `null`  | Overstyr sprak for commit-melding                           |
| `skip_secret_scan` | bool           | `false` | Hopp over sikkerhetsscanning                                |
| `no_verify`        | bool           | `false` | Hopp over pre-commit hooks                                  |
| `auto_confirm`     | bool           | `false` | Hopp over bekreftelsesprompts (pakrevd for agenter)         |

**Returnerer:** Suksessstatus, generert commit-melding, commit-hash (hvis committet), liste over endrede filer og eventuelle advarsler.

## Arbeidsflyter

### Enkel commit

```text
1. gac_status()                              → Se hva som har endret seg
2. gac_commit(stage_all=true, auto_confirm=true)  → Stage, generer melding og commit
```

### Forhandsvisning for commit

```text
1. gac_status(include_diff=true, include_stats=true)  → Gjennomga endringer i detalj
2. gac_commit(stage_all=true, dry_run=true)            → Forhandsvis commit-meldingen
3. gac_commit(stage_all=true, auto_confirm=true)       → Utfor committen
```

### Grupperte commits

```text
1. gac_status()                                           → Se alle endringer
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Forhandsvis logiske grupperinger
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Utfor grupperte commits
```

### Commit med kontekst

```text
1. gac_status(include_history=5)  → Se nylige commits som stilreferanse
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Konfigurasjon

MCP-serveren bruker din eksisterende GAC-konfigurasjon. Ingen ekstra oppsett er nodvendig utover:

1. **Leverandor og modell**: Kjor `gac init` eller `gac model` for a konfigurere AI-leverandoren din
2. **API-nokler**: Lagret i `~/.gac.env` (satt opp under `gac init`)
3. **Valgfrie innstillinger**: Alle GAC-miljovariabler gjelder (`GAC_LANGUAGE`, `GAC_VERBOSE` osv.)

Se [hoveddokumentasjonen](USAGE.md#konfigurasjonsnotater) for alle konfigurasjonsalternativer.

## Feilsoking

### "No model configured"

Kjor `gac init` for a sette opp AI-leverandoren og modellen din for du bruker MCP-serveren.

### "No staged changes found"

Stage filer manuelt (`git add`) eller bruk `stage_all=true` i `gac_commit`-kallet.

### Serveren starter ikke

Verifiser at GAC er installert og tilgjengelig:

```bash
uvx gac --version
# eller
gac --version
```

Hvis du bruker `uvx`, sjekk at `uv` er installert og i din PATH.

### Agenten finner ikke serveren

Sjekk at MCP-konfigurasjonsfilen er pa riktig sted for klienten din og at `command`-stien er tilgjengelig fra shell-miljoet ditt.

### Rich-utdatakorrupsjon

MCP-serveren omdirigerer automatisk all Rich-konsollutdata til stderr for a forhindre stdio-protokollkorrupsjon. Hvis du ser forvrengd utdata, sjekk at du kjorer `gac serve` (ikke `gac` direkte) nar du bruker MCP.

## Se ogsa

- [Hoveddokumentasjon](USAGE.md)
- [Claude Code OAuth-oppsett](CLAUDE_CODE.md)
- [Qwen.ai OAuth-oppsett](QWEN.md)
- [Feilsokingsguide](TROUBLESHOOTING.md)
- [MCP-spesifikasjon](https://modelcontextprotocol.io/)
