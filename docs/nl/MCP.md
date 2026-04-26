# GAC als MCP-server gebruiken

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | **Nederlands** | [Italiano](../it/MCP.md)

GAC kan draaien als een [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)-server, waardoor AI-agents en editors commits kunnen genereren via gestructureerde tool-aanroepen in plaats van shell-commando's.

## Inhoudsopgave

- [GAC als MCP-server gebruiken](#gac-als-mcp-server-gebruiken)
  - [Inhoudsopgave](#inhoudsopgave)
  - [Wat is MCP?](#wat-is-mcp)
  - [Voordelen](#voordelen)
  - [Installatie](#installatie)
    - [Claude Code](#claude-code)
    - [Cursor](#cursor)
    - [Andere MCP-clients](#andere-mcp-clients)
  - [Beschikbare tools](#beschikbare-tools)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Workflows](#workflows)
    - [Basis commit](#basis-commit)
    - [Voorvertoning voor het committen](#voorvertoning-voor-het-committen)
    - [Gegroepeerde commits](#gegroepeerde-commits)
    - [Commit met context](#commit-met-context)
  - [Configuratie](#configuratie)
  - [Probleemoplossing](#probleemoplossing)
  - [Zie ook](#zie-ook)

## Wat is MCP?

Het Model Context Protocol is een open standaard die AI-applicaties in staat stelt externe tools aan te roepen via een gestructureerde interface. Door GAC als MCP-server te draaien, kan elke MCP-compatibele client de repository-status inspecteren en AI-gestuurde commits maken zonder direct shell-commando's uit te voeren.

## Voordelen

- **Gestructureerde interactie**: Agents roepen getypeerde tools aan met gevalideerde parameters in plaats van shell-uitvoer te parsen
- **Twee-tool workflow**: `gac_status` om te inspecteren, `gac_commit` om te handelen - een natuurlijke match voor agent-redenering
- **Volledige GAC-mogelijkheden**: AI-commitberichten, gegroepeerde commits, secret scanning en push - allemaal beschikbaar via MCP
- **Geen extra configuratie**: De server gebruikt uw bestaande GAC-configuratie (`~/.gac.env`, provider-instellingen, enz.)

## Installatie

De MCP-server wordt gestart met `gac serve` en communiceert via stdio, het standaard MCP-transport.

### Claude Code

Voeg toe aan uw project `.mcp.json` of globale `~/.claude/claude_code_config.json`:

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

Of als u GAC globaal geinstalleerd heeft:

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

### Cursor

Voeg toe aan uw Cursor MCP-instellingen (`.cursor/mcp.json`):

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

### Andere MCP-clients

Elke MCP-compatibele client kan GAC gebruiken. Het server-ingangspunt is:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

Als u GAC geinstalleerd heeft (via `uv tool install gac`), kunt u `gac` direct gebruiken in plaats van `uvx gac`.

## Beschikbare tools

De server biedt twee tools:

### gac_status

Inspecteer de repository-status. Gebruik dit voor het committen om te begrijpen wat er gecommit zal worden.

**Parameters:**

| Parameter           | Type                                    | Default     | Beschrijving                               |
| ------------------- | --------------------------------------- | ----------- | ------------------------------------------ |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Uitvoerformaat                             |
| `include_diff`      | bool                                    | `false`     | Volledige diff-inhoud meenemen             |
| `include_stats`     | bool                                    | `true`      | Statistieken van regelwijzigingen meenemen |
| `include_history`   | int                                     | `0`         | Aantal recente commits om mee te nemen     |
| `staged_only`       | bool                                    | `false`     | Alleen gestagede wijzigingen tonen         |
| `include_untracked` | bool                                    | `true`      | Niet-gevolgde bestanden meenemen           |
| `max_diff_lines`    | int                                     | `500`       | Diff-uitvoer beperken (0 = onbeperkt)      |

**Retourneert:** Branch-naam, bestandsstatus (gestaged/niet-gestaged/niet-gevolgd/conflicten), optionele diff-inhoud, optionele statistieken en optionele commit-geschiedenis.

### gac_commit

Genereer een AI-gestuurd commitbericht en voer optioneel de commit uit.

**Parameters:**

| Parameter          | Type           | Default | Beschrijving                                                               |
| ------------------ | -------------- | ------- | -------------------------------------------------------------------------- |
| `stage_all`        | bool           | `false` | Alle wijzigingen stagen voor het committen (`git add -A`)                  |
| `files`            | list[str]      | `[]`    | Specifieke bestanden om te stagen                                          |
| `dry_run`          | bool           | `false` | Voorvertoning zonder uitvoering                                            |
| `message_only`     | bool           | `false` | Bericht genereren zonder te committen                                      |
| `push`             | bool           | `false` | Na de commit naar remote pushen                                            |
| `group`            | bool           | `false` | Wijzigingen opsplitsen in meerdere logische commits                        |
| `one_liner`        | bool           | `false` | Eenregelig commitbericht                                                   |
| `scope`            | string \| null | `null`  | Conventional commit scope (automatisch gedetecteerd indien niet opgegeven) |
| `hint`             | string         | `""`    | Extra context voor betere berichten                                        |
| `model`            | string \| null | `null`  | AI-model overschrijven (`provider:model_name`)                             |
| `language`         | string \| null | `null`  | Taal van commitbericht overschrijven                                       |
| `skip_secret_scan` | bool           | `false` | Beveiligingsscan overslaan                                                 |
| `no_verify`        | bool           | `false` | Pre-commit hooks overslaan                                                 |
| `auto_confirm`     | bool           | `false` | Bevestigingsprompts overslaan (vereist voor agents)                        |

**Retourneert:** Successtatus, gegenereerd commitbericht, commit-hash (indien gecommit), lijst van gewijzigde bestanden en eventuele waarschuwingen.

## Workflows

### Basis commit

```text
1. gac_status()                              → Bekijk wat er is veranderd
2. gac_commit(stage_all=true, auto_confirm=true)  → Stage, genereer bericht en commit
```

### Voorvertoning voor het committen

```text
1. gac_status(include_diff=true, include_stats=true)  → Wijzigingen in detail bekijken
2. gac_commit(stage_all=true, dry_run=true)            → Voorvertoning van het commitbericht
3. gac_commit(stage_all=true, auto_confirm=true)       → Commit uitvoeren
```

### Gegroepeerde commits

```text
1. gac_status()                                           → Alle wijzigingen bekijken
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Voorvertoning van logische groeperingen
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Gegroepeerde commits uitvoeren
```

### Commit met context

```text
1. gac_status(include_history=5)  → Recente commits bekijken als stijlreferentie
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Configuratie

De MCP-server gebruikt uw bestaande GAC-configuratie. Geen extra configuratie nodig naast:

1. **Provider en model**: Voer `gac init` of `gac model` uit om uw AI-provider te configureren
2. **API-sleutels**: Opgeslagen in `~/.gac.env` (ingesteld tijdens `gac init`)
3. **Optionele instellingen**: Alle GAC-omgevingsvariabelen zijn van toepassing (`GAC_LANGUAGE`, `GAC_VERBOSE`, enz.)

Zie de [hoofddocumentatie](USAGE.md#configuratie-notities) voor alle configuratieopties.

## Probleemoplossing

### "No model configured"

Voer `gac init` uit om uw AI-provider en model in te stellen voordat u de MCP-server gebruikt.

### "No staged changes found"

Stage bestanden handmatig (`git add`) of gebruik `stage_all=true` in de `gac_commit`-aanroep.

### Server start niet

Controleer of GAC geinstalleerd en toegankelijk is:

```bash
uvx gac --version
# of
gac --version
```

Als u `uvx` gebruikt, zorg ervoor dat `uv` geinstalleerd is en in uw PATH staat.

### Agent kan de server niet vinden

Zorg ervoor dat het MCP-configuratiebestand op de juiste locatie staat voor uw client en dat het `command`-pad toegankelijk is vanuit uw shell-omgeving.

### Rich-uitvoercorruptie

De MCP-server leidt alle Rich-console-uitvoer automatisch om naar stderr om stdio-protocolcorruptie te voorkomen. Als u onleesbare uitvoer ziet, zorg ervoor dat u `gac serve` gebruikt (niet `gac` direct) wanneer u MCP gebruikt.

## Zie ook

- [Hoofddocumentatie](USAGE.md)
- [Claude Code OAuth-installatie](CLAUDE_CODE.md)
- [Probleemoplossing](TROUBLESHOOTING.md)
- [MCP-specificatie](https://modelcontextprotocol.io/)
