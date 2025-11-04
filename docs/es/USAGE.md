# Uso de Línea de Comandos de gac

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | **Español** | [Português](../pt/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md)

Este documento describe todas las banderas y opciones disponibles para la herramienta CLI de `gac`.

## Tabla de Contenidos

- [Uso de Línea de Comandos de gac](#uso-de-línea-de-comandos-de-gac)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Uso Básico](#uso-básico)
  - [Banderas del Flujo de Trabajo Principal](#banderas-del-flujo-de-trabajo-principal)
  - [Personalización de Mensajes](#personalización-de-mensajes)
  - [Salida y Verbosidad](#salida-y-verbosidad)
  - [Ayuda y Versión](#ayuda-y-versión)
  - [Flujos de Trabajo de Ejemplo](#flujos-de-trabajo-de-ejemplo)
  - [Avanzado](#avanzado)
    - [Omitir Hooks Pre-commit y Lefthook](#omitir-hooks-pre-commit-y-lefthook)
    - [Escaneo de Seguridad](#escaneo-de-seguridad)
  - [Notas de Configuración](#notas-de-configuración)
    - [Opciones de Configuración Avanzadas](#opciones-de-configuración-avanzadas)
    - [Subcomandos de Configuración](#subcomandos-de-configuración)
  - [Obtención de Ayuda](#obtención-de-ayuda)

## Uso Básico

```sh
gac init
# Luego sigue las instrucciones para configurar tu proveedor, modelo y claves API interactivamente
gac
```

Genera un mensaje de commit impulsado por LLM para los cambios staged y solicita confirmación. La confirmación acepta:

- `y` o `yes` - Proceder con el commit
- `n` o `no` - Cancelar el commit
- `r` o `reroll` - Regenerar el mensaje de commit con el mismo contexto
- `e` o `edit` - Editar el mensaje de commit en el lugar con edición de terminal rica (vi/emacs keybindings)
- Cualquier otro texto - Regenerar con ese texto como retroalimentación (ej., `make it shorter`, `focus on performance`)
- Entrada vacía (solo Enter) - Mostrar el prompt nuevamente

---

## Banderas del Flujo de Trabajo Principal

| Bandera / Opción     | Corta | Descripción                                               |
| -------------------- | ----- | --------------------------------------------------------- |
| `--add-all`          | `-a`  | Staging de todos los cambios antes de hacer commit        |
| `--group`            | `-g`  | Agrupar cambios staged en múltiples commits lógicos       |
| `--push`             | `-p`  | Hacer push de cambios al remoto después del commit        |
| `--yes`              | `-y`  | Confirmar automáticamente el commit sin preguntar         |
| `--dry-run`          |       | Mostrar qué pasaría sin hacer cambios                     |
| `--no-verify`        |       | Omitir hooks pre-commit y lefthook al hacer commit        |
| `--skip-secret-scan` |       | Omitir escaneo de seguridad de secretos en cambios staged |

**Nota:** Combina `-a` y `-g` (ej., `-ag`) para hacer staging de TODOS los cambios primero, luego agruparlos en commits.

**Nota:** Cuando usas `--group`, el límite máximo de tokens de salida se escala automáticamente basado en el número de archivos siendo commiteados (2x para 1-9 archivos, 3x para 10-19 archivos, 4x para 20-29 archivos, 5x para 30+ archivos). Esto asegura que el LLM tenga suficientes tokens para generar todos los commits agrupados sin truncamiento, incluso para cambios grandes.

## Personalización de Mensajes

| Bandera / Opción    | Corta | Descripción                                                                  |
| ------------------- | ----- | ---------------------------------------------------------------------------- |
| `--one-liner`       | `-o`  | Generar un mensaje de commit de una sola línea                               |
| `--verbose`         | `-v`  | Generar mensajes de commit detallados con motivación, arquitectura e impacto |
| `--hint <text>`     | `-h`  | Añadir una pista para guiar al LLM                                           |
| `--model <model>`   | `-m`  | Especificar el modelo a usar para este commit                                |
| `--language <lang>` | `-l`  | Anular el idioma (nombre o código: 'Spanish', 'es', 'zh-CN', 'ja')           |
| `--scope`           | `-s`  | Inferir un scope apropiado para el commit                                    |

**Nota:** Puedes proporcionar retroalimentación interactivamente simplemente escribiéndola en el prompt de confirmación - no necesitas prefijar con 'r'. Escribe `r` para un reroll simple, `e` para editar en el lugar con vi/emacs keybindings, o escribe tu retroalimentación directamente como `make it shorter`.

## Salida y Verbosidad

| Bandera / Opción      | Corta | Descripción                                                       |
| --------------------- | ----- | ----------------------------------------------------------------- |
| `--quiet`             | `-q`  | Suprimir toda la salida excepto errores                           |
| `--log-level <level>` |       | Establecer nivel de log (debug, info, warning, error)             |
| `--show-prompt`       |       | Imprimir el prompt LLM usado para generación de mensaje de commit |

## Ayuda y Versión

| Bandera / Opción | Corta | Descripción                      |
| ---------------- | ----- | -------------------------------- |
| `--version`      |       | Mostrar versión de gac y salir   |
| `--help`         |       | Mostrar mensaje de ayuda y salir |

---

## Flujos de Trabajo de Ejemplo

- **Staging de todos los cambios y commit:**

  ```sh
  gac -a
  ```

- **Commit y push en un paso:**

  ```sh
  gac -ap
  ```

- **Generar un mensaje de commit de una línea:**

  ```sh
  gac -o
  ```

- **Generar un mensaje de commit detallado con secciones estructuradas:**

  ```sh
  gac -v
  ```

- **Añadir una pista para el LLM:**

  ```sh
  gac -h "Refactor authentication logic"
  ```

- **Inferir scope para el commit:**

  ```sh
  gac -s
  ```

- **Agrupar cambios staged en commits lógicos:**

  ```sh
  gac -g
  # Agrupa solo los files que ya tienes en staging
  ```

- **Agrupar todos los cambios (staged + unstaged) y auto-confirmar:**

  ```sh
  gac -agy
  # Hace staging de todo, lo agrupa, y auto-confirma
  ```

- **Usar un modelo específico solo para este commit:**

  ```sh
  gac -m anthropic:claude-3-5-haiku-latest
  ```

- **Generar mensaje de commit en un idioma específico:**

  ```sh
  # Usando códigos de idioma (más corto)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # Usando nombres completos
  gac -l "Simplified Chinese"
  gac -l Japanese
  gac -l Spanish
  ```

- **Dry run (ver qué pasaría):**

  ```sh
  gac --dry-run
  ```

## Avanzado

- Combina banderas para flujos de trabajo más potentes (ej., `gac -ayp` para staging, auto-confirmar y hacer push)
- Usa `--show-prompt` para depurar o revisar el prompt enviado al LLM
- Ajusta la verbosidad con `--log-level` o `--quiet`

### Omitir Hooks Pre-commit y Lefthook

La bandera `--no-verify` te permite omitir cualquier hook pre-commit o lefthook configurado en tu proyecto:

```sh
gac --no-verify  # Omitir todos los hooks pre-commit y lefthook
```

**Usa `--no-verify` cuando:**

- Los hooks pre-commit o lefthook están fallando temporalmente
- Trabajas con hooks que consumen mucho tiempo
- Haciendo commit de código en progreso que aún no pasa todas las verificaciones

**Nota:** Usa con precaución ya que estos hooks mantienen los estándares de calidad del código.

### Escaneo de Seguridad

gac incluye escaneo de seguridad incorporado que detecta automáticamente posibles secretos y claves API en tus cambios staged antes de hacer commit. Esto ayuda a prevenir accidentalmente comprometer información sensible.

**Omitir escaneos de seguridad:**

```sh
gac --skip-secret-scan  # Omitir escaneo de seguridad para este commit
```

**Para deshabilitar permanentemente:** Establece `GAC_SKIP_SECRET_SCAN=true` en tu archivo `.gac.env`.

**Cuándo omitir:**

- Haciendo commit de código de ejemplo con claves placeholder
- Trabajando con fixtures de prueba que contienen credenciales dummy
- Cuando has verificado que los cambios son seguros

**Nota:** El escáner usa coincidencia de patrones para detectar formatos comunes de secretos. Siempre revisa tus cambios staged antes de hacer commit.

## Notas de Configuración

- La forma recomendada de configurar gac es ejecutar `gac init` y seguir las instrucciones interactivas.
- ¿Ya tienes el idioma configurado y solo necesitas cambiar proveedores o modelos? Ejecuta `gac model` para repetir la configuración sin preguntas de idioma.
- gac carga configuración en el siguiente orden de precedencia:
  1. Banderas CLI
  2. Variables de entorno
  3. Nivel de proyecto `.gac.env`
  4. Nivel de usuario `~/.gac.env`

### Opciones de Configuración Avanzadas

Puedes personalizar el comportamiento de gac con estas variables de entorno opcionales:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Inferir automáticamente e incluir scope en mensajes de commit (ej., `feat(auth):` vs `feat:`)
- `GAC_VERBOSE=true` - Generar mensajes de commit detallados con secciones de motivación, arquitectura e impacto
- `GAC_TEMPERATURE=0.7` - Controlar la creatividad del LLM (0.0-1.0, más bajo = más enfocado)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Tokens máximos para mensajes generados (escalado automáticamente 2-5x cuando usas `--group` basado en el conteo de archivos; anula para ir más alto o más bajo)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Advertir cuando los prompts excedan este conteo de tokens
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Usar un prompt de sistema personalizado para generación de mensajes de commit
- `GAC_LANGUAGE=Spanish` - Generar mensajes de commit en un idioma específico (ej., Spanish, French, Japanese, German). Soporta nombres completos o códigos ISO (es, fr, ja, de, zh-CN). Usa `gac language` para selección interactiva
- `GAC_TRANSLATE_PREFIXES=true` - Traducir prefijos de commit convencionales (feat, fix, etc.) al idioma de destino (default: false, mantiene prefijos en inglés)
- `GAC_SKIP_SECRET_SCAN=true` - Deshabilitar escaneo de seguridad automático para secretos en cambios staged (usa con precaución)

Consulta `.gac.env.example` para una plantilla de configuración completa.

Para guía detallada sobre creating prompts de sistema personalizados, consulta [docs/CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md).

### Subcomandos de Configuración

Los siguientes subcomandos están disponibles:

- `gac init` — Asistente de configuración interactivo para proveedor, modelo y configuración de idioma
- `gac model` — Configuración de proveedor/modelo/clave API sin prompts de idioma (ideal para cambios rápidos)
- `gac config show` — Mostrar configuración actual
- `gac config set KEY VALUE` — Establecer una clave de configuración en `$HOME/.gac.env`
- `gac config get KEY` — Obtener un valor de configuración
- `gac config unset KEY` — Eliminar una clave de configuración de `$HOME/.gac.env`
- `gac language` (o `gac lang`) — Selector interactivo de idioma para mensajes de commit (establece GAC_LANGUAGE)
- `gac diff` — Mostrar git diff filtrado con opciones para cambios staged/unstaged, color y truncación

## Obtención de Ayuda

- Para prompts de sistema personalizados, consulta [docs/CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)
- Para solución de problemas y consejos avanzados, consulta [docs/TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- Para instalación y configuración, consulta [README.md#configuración](../README.es.md#configuración)
- Para contribuir, consulta [docs/CONTRIBUTING.md](../CONTRIBUTING.md)
- Información de licencia: [LICENSE](../LICENSE)
