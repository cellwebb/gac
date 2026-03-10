# Usar GAC como Servidor MCP

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | **Español** | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC puede ejecutarse como un servidor del [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), permitiendo que agentes de IA y editores generen commits a través de llamadas de herramientas estructuradas en lugar de comandos de shell.

## Tabla de Contenidos

- [Usar GAC como Servidor MCP](#usar-gac-como-servidor-mcp)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [¿Qué es MCP?](#qué-es-mcp)
  - [Beneficios](#beneficios)
  - [Configuración](#configuración)
    - [Claude Code](#claude-code)
    - [Cursor](#cursor)
    - [Otros Clientes MCP](#otros-clientes-mcp)
  - [Herramientas Disponibles](#herramientas-disponibles)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Flujos de Trabajo](#flujos-de-trabajo)
    - [Commit Básico](#commit-básico)
    - [Vista Previa Antes de Hacer Commit](#vista-previa-antes-de-hacer-commit)
    - [Commits Agrupados](#commits-agrupados)
    - [Commit con Contexto](#commit-con-contexto)
  - [Configuración del Servidor](#configuración-del-servidor)
  - [Solución de Problemas](#solución-de-problemas)
  - [Ver También](#ver-también)

## ¿Qué es MCP?

El Model Context Protocol es un estándar abierto que permite a las aplicaciones de IA llamar a herramientas externas a través de una interfaz estructurada. Al ejecutar GAC como un servidor MCP, cualquier cliente compatible con MCP puede inspeccionar el estado del repositorio y crear commits impulsados por IA sin invocar comandos de shell directamente.

## Beneficios

- **Interacción estructurada**: Los agentes llaman a herramientas tipadas con parámetros validados en lugar de analizar la salida del shell
- **Flujo de trabajo de dos herramientas**: `gac_status` para inspeccionar, `gac_commit` para actuar — un ajuste natural para el razonamiento de agentes
- **Capacidades completas de GAC**: Mensajes de commit con IA, commits agrupados, escaneo de secretos y push — todo disponible a través de MCP
- **Sin configuración adicional**: El servidor usa tu configuración existente de GAC (`~/.gac.env`, configuración de proveedores, etc.)

## Configuración

El servidor MCP se inicia con `gac serve` y se comunica a través de stdio, el transporte estándar de MCP.

### Claude Code

Añade a tu `.mcp.json` del proyecto o al `~/.claude/claude_code_config.json` global:

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

O si tienes GAC instalado globalmente:

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

Añade a la configuración MCP de Cursor (`.cursor/mcp.json`):

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

### Otros Clientes MCP

Cualquier cliente compatible con MCP puede usar GAC. El punto de entrada del servidor es:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

Si tienes GAC instalado (via `uv tool install gac`), puedes usar `gac` directamente en lugar de `uvx gac`.

## Herramientas Disponibles

El servidor expone dos herramientas:

### gac_status

Inspecciona el estado del repositorio. Úsalo antes de hacer commit para entender qué se va a commitear.

**Parámetros:**

| Parameter           | Type                                    | Default     | Descripción                                       |
| ------------------- | --------------------------------------- | ----------- | ------------------------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Formato de salida                                 |
| `include_diff`      | bool                                    | `false`     | Incluir contenido completo del diff               |
| `include_stats`     | bool                                    | `true`      | Incluir estadísticas de cambios de líneas         |
| `include_history`   | int                                     | `0`         | Número de commits recientes a incluir             |
| `staged_only`       | bool                                    | `false`     | Mostrar solo cambios preparados                   |
| `include_untracked` | bool                                    | `true`      | Incluir archivos sin seguimiento                  |
| `max_diff_lines`    | int                                     | `500`       | Limitar tamaño de salida del diff (0 = ilimitado) |

**Retorna:** Nombre de rama, estado de archivos (preparados/no preparados/sin seguimiento/conflictos), contenido opcional del diff, estadísticas opcionales e historial opcional de commits.

### gac_commit

Genera un mensaje de commit impulsado por IA y opcionalmente ejecuta el commit.

**Parámetros:**

| Parameter          | Type           | Default | Descripción                                                        |
| ------------------ | -------------- | ------- | ------------------------------------------------------------------ |
| `stage_all`        | bool           | `false` | Preparar todos los cambios antes de commitear (`git add -A`)       |
| `files`            | list[str]      | `[]`    | Archivos específicos a preparar                                    |
| `dry_run`          | bool           | `false` | Vista previa sin ejecutar                                          |
| `message_only`     | bool           | `false` | Generar mensaje sin hacer commit                                   |
| `push`             | bool           | `false` | Hacer push al remoto después del commit                            |
| `group`            | bool           | `false` | Dividir cambios en múltiples commits lógicos                       |
| `one_liner`        | bool           | `false` | Mensaje de commit de una sola línea                                |
| `scope`            | string \| null | `null`  | Scope de commit convencional (auto-detectado si no se proporciona) |
| `hint`             | string         | `""`    | Contexto adicional para mejores mensajes                           |
| `model`            | string \| null | `null`  | Sobrescribir modelo de IA (`provider:model_name`)                  |
| `language`         | string \| null | `null`  | Sobrescribir idioma del mensaje de commit                          |
| `skip_secret_scan` | bool           | `false` | Omitir escaneo de seguridad                                        |
| `no_verify`        | bool           | `false` | Omitir hooks de pre-commit                                         |
| `auto_confirm`     | bool           | `false` | Omitir confirmaciones (requerido para agentes)                     |

**Retorna:** Estado de éxito, mensaje de commit generado, hash del commit (si se commiteó), lista de archivos modificados y cualquier advertencia.

## Flujos de Trabajo

### Commit Básico

```text
1. gac_status()                              → Ver qué ha cambiado
2. gac_commit(stage_all=true, auto_confirm=true)  → Preparar, generar mensaje y commitear
```

### Vista Previa Antes de Hacer Commit

```text
1. gac_status(include_diff=true, include_stats=true)  → Revisar cambios en detalle
2. gac_commit(stage_all=true, dry_run=true)            → Vista previa del mensaje de commit
3. gac_commit(stage_all=true, auto_confirm=true)       → Ejecutar el commit
```

### Commits Agrupados

```text
1. gac_status()                                           → Ver todos los cambios
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Vista previa de agrupaciones lógicas
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Ejecutar commits agrupados
```

### Commit con Contexto

```text
1. gac_status(include_history=5)  → Ver commits recientes como referencia de estilo
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Configuración del Servidor

El servidor MCP usa tu configuración existente de GAC. No se necesita configuración adicional más allá de:

1. **Proveedor y modelo**: Ejecuta `gac init` o `gac model` para configurar tu proveedor de IA
2. **Claves API**: Almacenadas en `~/.gac.env` (configuradas durante `gac init`)
3. **Ajustes opcionales**: Todas las variables de entorno de GAC aplican (`GAC_LANGUAGE`, `GAC_VERBOSE`, etc.)

Consulta la [documentación principal](USAGE.md#notas-de-configuración) para todas las opciones de configuración.

## Solución de Problemas

### "No model configured"

Ejecuta `gac init` para configurar tu proveedor de IA y modelo antes de usar el servidor MCP.

### "No staged changes found"

Prepara archivos manualmente (`git add`) o usa `stage_all=true` en la llamada a `gac_commit`.

### El servidor no inicia

Verifica que GAC esté instalado y accesible:

```bash
uvx gac --version
# o
gac --version
```

Si usas `uvx`, asegúrate de que `uv` esté instalado y en tu PATH.

### El agente no encuentra el servidor

Asegúrate de que el archivo de configuración MCP esté en la ubicación correcta para tu cliente y que la ruta del `command` sea accesible desde tu entorno de shell.

### Corrupción de salida Rich

El servidor MCP redirige automáticamente toda la salida de la consola Rich a stderr para prevenir la corrupción del protocolo stdio. Si ves salida ilegible, asegúrate de estar ejecutando `gac serve` (no `gac` directamente) al usar MCP.

## Ver También

- [Documentación Principal](USAGE.md)
- [Configuración OAuth de Claude Code](CLAUDE_CODE.md)
- [Configuración OAuth de Qwen.ai](QWEN.md)
- [Guía de Solución de Problemas](TROUBLESHOOTING.md)
- [Especificación MCP](https://modelcontextprotocol.io/)
