# Anvanda GAC som MCP-server

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | **Svenska** | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC kan koras som en [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)-server, vilket gor det mojligt for AI-agenter och editorer att generera commits genom strukturerade verktygsanrop istallet for shell-kommandon.

## Innehallsforteckning

- [Anvanda GAC som MCP-server](#anvanda-gac-som-mcp-server)
  - [Innehallsforteckning](#innehallsforteckning)
  - [Vad ar MCP?](#vad-ar-mcp)
  - [Fordelar](#fordelar)
  - [Installation](#installation)
    - [Claude Code](#claude-code)
    - [Claude Desktop](#claude-desktop)
    - [Cursor](#cursor)
    - [Andra MCP-klienter](#andra-mcp-klienter)
  - [Tillgangliga verktyg](#tillgangliga-verktyg)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Arbetsfloden](#arbetsfloden)
    - [Enkel commit](#enkel-commit)
    - [Forhandsgranska innan commit](#forhandsgranska-innan-commit)
    - [Grupperade commits](#grupperade-commits)
    - [Commit med kontext](#commit-med-kontext)
  - [Konfiguration](#konfiguration)
  - [Felsokning](#felsokning)
  - [Se aven](#se-aven)

## Vad ar MCP?

Model Context Protocol ar en oppen standard som later AI-applikationer anropa externa verktyg genom ett strukturerat granssnitt. Genom att kora GAC som MCP-server kan vilken MCP-kompatibel klient som helst inspektera repository-status och skapa AI-drivna commits utan att anropa shell-kommandon direkt.

## Fordelar

- **Strukturerad interaktion**: Agenter anropar typade verktyg med validerade parametrar istallet for att tolka shell-utdata
- **Tva-verktygs arbetsflode**: `gac_status` for att inspektera, `gac_commit` for att agera - en naturlig passform for agentresonemang
- **Fulla GAC-funktioner**: AI-commit-meddelanden, grupperade commits, hemlighetsskanning och push - allt tillgangligt via MCP
- **Ingen extra konfiguration**: Servern anvander din befintliga GAC-konfiguration (`~/.gac.env`, leverantorsinstellningar osv.)

## Installation

MCP-servern startas med `gac serve` och kommunicerar over stdio, standard MCP-transport.

### Claude Code

Lagg till i ditt projekts `.mcp.json` eller globala `~/.claude/claude_code_config.json`:

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

Eller om du har GAC installerat globalt:

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

Lagg till i din Claude Desktop-konfigurationsfil (`~/Library/Application Support/Claude/claude_desktop_config.json` pa macOS, `%APPDATA%\Claude\claude_desktop_config.json` pa Windows):

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

Lagg till i dina Cursor MCP-installningar (`.cursor/mcp.json`):

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

### Andra MCP-klienter

Vilken MCP-kompatibel klient som helst kan anvanda GAC. Serverns ingangspunkt ar:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

Om du har GAC installerat (via `uv tool install gac`) kan du anvanda `gac` direkt istallet for `uvx gac`.

## Tillgangliga verktyg

Servern exponerar tva verktyg:

### gac_status

Inspektera repository-status. Anvand detta innan commit for att forsta vad som kommer att committas.

**Parametrar:**

| Parameter           | Type                                    | Default     | Beskrivning                            |
| ------------------- | --------------------------------------- | ----------- | -------------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Utdataformat                           |
| `include_diff`      | bool                                    | `false`     | Inkludera fullstandigt diff-innehall   |
| `include_stats`     | bool                                    | `true`      | Inkludera statistik for radandringar   |
| `include_history`   | int                                     | `0`         | Antal senaste commits att inkludera    |
| `staged_only`       | bool                                    | `false`     | Visa bara stagade andringar            |
| `include_untracked` | bool                                    | `true`      | Inkludera osperade filer               |
| `max_diff_lines`    | int                                     | `500`       | Begransia diff-utdata (0 = obegransat) |

**Returnerar:** Branch-namn, filstatus (stagad/ostagad/osparad/konflikter), valfritt diff-innehall, valfri statistik och valfri commit-historik.

### gac_commit

Generera ett AI-drivet commit-meddelande och utfor valfritt committen.

**Parametrar:**

| Parameter          | Type           | Default | Beskrivning                                               |
| ------------------ | -------------- | ------- | --------------------------------------------------------- |
| `stage_all`        | bool           | `false` | Staga alla andringar innan commit (`git add -A`)          |
| `files`            | list[str]      | `[]`    | Specifika filer att staga                                 |
| `dry_run`          | bool           | `false` | Forhandsgranska utan att utfora                           |
| `message_only`     | bool           | `false` | Generera meddelande utan att committa                     |
| `push`             | bool           | `false` | Pusha till remote efter commit                            |
| `group`            | bool           | `false` | Dela upp andringar i flera logiska commits                |
| `one_liner`        | bool           | `false` | Enrads commit-meddelande                                  |
| `scope`            | string \| null | `null`  | Conventional commit scope (auto-detekteras om ej angivet) |
| `hint`             | string         | `""`    | Ytterligare kontext for battre meddelanden                |
| `model`            | string \| null | `null`  | Overstyr AI-modell (`provider:model_name`)                |
| `language`         | string \| null | `null`  | Overstyr sprak for commit-meddelande                      |
| `skip_secret_scan` | bool           | `false` | Hoppa over sakerhetsskanning                              |
| `no_verify`        | bool           | `false` | Hoppa over pre-commit hooks                               |
| `auto_confirm`     | bool           | `false` | Hoppa over bekraftelsepromptar (kravs for agenter)        |

**Returnerar:** Framgangsstatus, genererat commit-meddelande, commit-hash (om committat), lista over andrade filer och eventuella varningar.

## Arbetsfloden

### Enkel commit

```text
1. gac_status()                              → Se vad som har andrats
2. gac_commit(stage_all=true, auto_confirm=true)  → Staga, generera meddelande och committa
```

### Forhandsgranska innan commit

```text
1. gac_status(include_diff=true, include_stats=true)  → Granska andringar i detalj
2. gac_commit(stage_all=true, dry_run=true)            → Forhandsgranska commit-meddelandet
3. gac_commit(stage_all=true, auto_confirm=true)       → Utfor committen
```

### Grupperade commits

```text
1. gac_status()                                           → Se alla andringar
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Forhandsgranska logiska grupperingar
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Utfor grupperade commits
```

### Commit med kontext

```text
1. gac_status(include_history=5)  → Se senaste commits som stilreferens
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Konfiguration

MCP-servern anvander din befintliga GAC-konfiguration. Ingen ytterligare installation behovs utover:

1. **Leverantor och modell**: Kor `gac init` eller `gac model` for att konfigurera din AI-leverantor
2. **API-nycklar**: Lagrade i `~/.gac.env` (installda under `gac init`)
3. **Valfria installningar**: Alla GAC-miljovariabler galler (`GAC_LANGUAGE`, `GAC_VERBOSE` osv.)

Se [huvuddokumentationen](USAGE.md#konfigurationsanteckningar) for alla konfigurationsalternativ.

## Felsokning

### "No model configured"

Kor `gac init` for att stalla in din AI-leverantor och modell innan du anvander MCP-servern.

### "No staged changes found"

Staga filer manuellt (`git add`) eller anvand `stage_all=true` i `gac_commit`-anropet.

### Servern startar inte

Verifiera att GAC ar installerat och tillgangligt:

```bash
uvx gac --version
# eller
gac --version
```

Om du anvander `uvx`, se till att `uv` ar installerat och finns i din PATH.

### Agenten kan inte hitta servern

Se till att MCP-konfigurationsfilen ar pa ratt plats for din klient och att `command`-sokvagen ar tillganglig fran din shell-miljo.

### Rich-utdatakorruption

MCP-servern omdirigerar automatiskt alla Rich-konsolutdata till stderr for att forhindra stdio-protokollkorruption. Om du ser forvrängd utdata, se till att du kor `gac serve` (inte `gac` direkt) nar du anvander MCP.

## Se aven

- [Huvuddokumentation](USAGE.md)
- [Claude Code OAuth-installation](CLAUDE_CODE.md)
- [Qwen.ai OAuth-installation](QWEN.md)
- [Felsokningsguide](TROUBLESHOOTING.md)
- [MCP-specifikation](https://modelcontextprotocol.io/)
