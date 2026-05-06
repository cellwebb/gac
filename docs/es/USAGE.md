# Uso de Línea de Comandos de gac

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | **Español** | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

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
    - [Integración con scripts y procesamiento externo](#integración-con-scripts-y-procesamiento-externo)
    - [Omitir Hooks Pre-commit y Lefthook](#omitir-hooks-pre-commit-y-lefthook)
    - [Escaneo de Seguridad](#escaneo-de-seguridad)
    - [Verificación de Certificado SSL](#verificación-de-certificado-ssl)
  - [Notas de Configuración](#notas-de-configuración)
    - [Opciones de Configuración Avanzadas](#opciones-de-configuración-avanzadas)
    - [Subcomandos de Configuración](#subcomandos-de-configuración)
  - [Modo Interactivo](#modo-interactivo)
    - [Cómo Funciona](#cómo-funciona)
    - [Cuándo Usar el Modo Interactivo](#cuándo-usar-el-modo-interactivo)
    - [Ejemplos de Uso](#ejemplos-de-uso)
    - [Flujo de Preguntas y Respuestas](#flujo-de-preguntas-y-respuestas)
    - [Combinación con otros Flags](#combinación-con-otros-flags)
    - [Mejores Prácticas](#mejores-prácticas)
  - [Estadísticas de Uso](#estadísticas-de-uso)
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
- `e` o `edit` - Editar el mensaje de commit. Por defecto, abre una TUI in-place con keybindings vi/emacs. Establece `GAC_EDITOR` para abrir tu editor preferido en su lugar (ej., `GAC_EDITOR=code gac` para VS Code, `GAC_EDITOR=vim gac` para vim)
- Cualquier otro texto - Regenerar con ese texto como retroalimentación (ej., `make it shorter`, `focus on performance`)
- Entrada vacía (solo Enter) - Mostrar el prompt nuevamente

---

## Banderas del Flujo de Trabajo Principal

| Bandera / Opción     | Corta | Descripción                                                             |
| -------------------- | ----- | ----------------------------------------------------------------------- |
| `--add-all`          | `-a`  | Staging de todos los cambios antes de hacer commit                      |
| `--stage`            | `-S`  | Seleccionar archivos interactivamente con TUI basado en árbol           |
| `--group`            | `-g`  | Agrupar cambios staged en múltiples commits lógicos                     |
| `--push`             | `-p`  | Hacer push de cambios al remoto después del commit                      |
| `--yes`              | `-y`  | Confirmar automáticamente el commit sin preguntar                       |
| `--dry-run`          |       | Mostrar qué pasaría sin hacer cambios                                   |
| `--message-only`     |       | Mostrar solo el mensaje de commit generado sin realizar el commit       |
| `--no-verify`        |       | Omitir hooks pre-commit y lefthook al hacer commit                      |
| `--skip-secret-scan` |       | Omitir escaneo de seguridad de secretos en cambios staged               |
| `--no-verify-ssl`    |       | Omitir verificación de certificado SSL (útil para proxies corporativos) |
| `--signoff`          |       | Agregar línea Signed-off-by al mensaje de commit (cumplimiento DCO)     |
| `--interactive`      | `-i`  | Hacer preguntas sobre los cambios para generar mejores commits          |

**Nota:** `--stage` y `--add-all` son mutuamente excluyentes. Usa `--stage` para seleccionar interactivamente qué archivos hacer staging, y `--add-all` para hacer staging de todos los cambios a la vez.

**Nota:** Combina `-a` y `-g` (ej., `-ag`) para hacer staging de TODOS los cambios primero, luego agruparlos en commits.

**Nota:** Cuando usas `--group`, el límite máximo de tokens de salida se escala automáticamente basado en el número de archivos siendo commiteados (2x para 1-9 archivos, 3x para 10-19 archivos, 4x para 20-29 archivos, 5x para 30+ archivos). Esto asegura que el LLM tenga suficientes tokens para generar todos los commits agrupados sin truncamiento, incluso para cambios grandes.

**Nota:** `--message-only` y `--group` son mutuamente excluyentes. Usa `--message-only` cuando quieras obtener el mensaje de commit para procesamiento externo, y `--group` cuando quieras organizar múltiples commits dentro del flujo de trabajo git actual.

**Nota:** El flag `--interactive` te hace preguntas sobre tus cambios para proporcionar contexto adicional al LLM, resultando en mensajes de commit más precisos y detallados. Esto es particularmente útil para cambios complejos o cuando quieres asegurar que el mensaje de commit capture el contexto completo de tu trabajo.

## Personalización de Mensajes

| Bandera / Opción    | Corta | Descripción                                                                  |
| ------------------- | ----- | ---------------------------------------------------------------------------- |
| `--one-liner`       | `-o`  | Generar un mensaje de commit de una sola línea                               |
| `--verbose`         | `-v`  | Generar mensajes de commit detallados con motivación, arquitectura e impacto |
| `--hint <text>`     | `-h`  | Añadir una pista para guiar al LLM                                           |
| `--model <model>`   | `-m`  | Especificar el modelo a usar para este commit                                |
| `--language <lang>` | `-l`  | Anular el idioma (nombre o código: 'Spanish', 'es', 'zh-CN', 'ja')           |
| `--scope`           | `-s`  | Inferir un scope apropiado para el commit                                    |
| `--50-72`           |       | Aplicar la regla 50/72 para el formato del mensaje de commit                 |

**Nota:** El flag `--50-72` aplica la [regla 50/72](https://www.conventionalcommits.org/en/v1.0.0/#summary) donde:

- Línea de asunto: máximo 50 caracteres
- Líneas del cuerpo: máximo 72 caracteres por línea
- Esto mantiene los mensajes de commit legibles en `git log --oneline` y la interfaz de GitHub

También puedes establecer `GAC_USE_50_72_RULE=true` en tu archivo `.gac.env` para aplicar esta regla siempre.

**Nota:** Puedes proporcionar retroalimentación interactivamente simplemente escribiéndola en el prompt de confirmación - no necesitas prefijar con 'r'. Escribe `r` para un reroll simple, `e` para editar el mensaje (TUI in-place por defecto, o tu `$GAC_EDITOR` si está configurado), o escribe tu retroalimentación directamente como `hazlo más corto`.

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
  gac -m anthropic:claude-haiku-4-5
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

- **Obtener solo el mensaje de commit (para integración con scripts):**

  ```sh
  gac --message-only
  # Salida: feat: add user authentication system
  ```

- **Obtener el mensaje de commit en formato de una sola línea:**

  ```sh
  gac --message-only --one-liner
  # Salida: feat: add user authentication system
  ```

- **Usar modo interactivo para proporcionar contexto:**

  ```sh
  gac -i
  # ¿Cuál es el propósito principal de estos cambios?
  # ¿Qué problema estás resolviendo?
  # ¿Hay algún detalle de implementación que valga la pena mencionar?
  ```

- **Modo interactivo con salida detallada:**

  ```sh
  gac -i -v
  # Hacer preguntas y generar mensaje de commit detallado
  ```

## Avanzado

- Combina banderas para flujos de trabajo más potentes (ej., `gac -ayp` para staging, auto-confirmar y hacer push)
- Usa `--show-prompt` para depurar o revisar el prompt enviado al LLM
- Ajusta la verbosidad con `--log-level` o `--quiet`
- Usa `--message-only` para integración con scripts y flujos de trabajo automatizados

### Integración con scripts y procesamiento externo

La bandera `--message-only` está diseñada para integración con scripts y flujos de trabajo de herramientas externas. Produce solo el mensaje de commit en bruto sin ningún formato adicional, spinners o elementos de UI.

**Casos de uso:**

- **Integración con agentes:** Permite que agentes de IA obtengan mensajes de commit y gestionen los commits por su cuenta
- **VCS alternativos:** Usar mensajes generados con otros sistemas de control de versiones (Mercurial, Jujutsu, etc.)
- **Workflows de commit personalizados:** Procesar o modificar el mensaje antes de hacer commit
- **Pipelines de CI/CD:** Extraer mensajes de commit para procesos automatizados

**Ejemplo de uso en script:**

```sh
#!/bin/bash
# Obtener el mensaje de commit y usarlo con una función de commit personalizada
MESSAGE=$(gac --message-only --add-all --yes)
git commit -m "$MESSAGE"
```

```python
# Ejemplo de integración en Python
import subprocess


def get_commit_message() -> str:
    result = subprocess.run(
        ["gac", "--message-only", "--yes"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


message = get_commit_message()
print(f"Generated message: {message}")
```

**Características clave para uso en scripts:**

- Salida limpia sin formato Rich ni spinners
- Omite automáticamente los prompts de confirmación
- No se realiza ningún commit real en git
- Funciona con `--one-liner` para una salida simplificada
- Se puede combinar con otras banderas como `--hint`, `--model`, etc.

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

### Verificación de Certificado SSL

La bandera `--no-verify-ssl` te permite omitir la verificación de certificado SSL para llamadas API:

```sh
gac --no-verify-ssl  # Omitir verificación SSL para este commit
```

**Para configurar permanentemente:** Establece `GAC_NO_VERIFY_SSL=true` en tu archivo `.gac.env`.

**Usa `--no-verify-ssl` cuando:**

- Los proxies corporativos interceptan tráfico SSL (proxies MITM)
- Los entornos de desarrollo usan certificados autofirmados
- Encuentras errores de certificado SSL debido a configuraciones de seguridad de red

**Nota:** Solo usa esta opción en entornos de red de confianza. Deshabilitar la verificación SSL reduce la seguridad y puede hacer que tus solicitudes API sean vulnerables a ataques man-in-the-middle.

### Línea Signed-off-by (Cumplimiento DCO)

gac admite agregar una línea `Signed-off-by` a los mensajes de commit, que se requiere para el cumplimiento del [Developer Certificate of Origin (DCO)](https://developercertificate.org/) en muchos proyectos de código abierto.

**Agregar signoff:**

```sh
gac --signoff  # Agregar línea Signed-off-by al commit
```

**Para habilitar permanentemente:** Establece `GAC_SIGNOFF=true` en tu archivo `.gac.env` o agrega `signoff=true` a tu configuración.

**Qué hace:**

- Agrega `Signed-off-by: Tu Nombre <tu.email@ejemplo.com>` al mensaje de commit
- Usa tu configuración de git (`user.name` y `user.email`) para completar la línea
- Requerido para proyectos como Cherry Studio, kernel de Linux y otros que usan DCO

**Configurar tu identidad de git:**

Asegúrate de que tu configuración de git tenga el nombre y correo correctos:

```sh
git config --global user.name "Tu Nombre Completo"
git config --global user.email "tu.email@ejemplo.com"
```

**Nota:** La línea Signed-off-by es agregada por git durante el commit, no por la IA durante la generación del mensaje. No la verás en la vista previa, pero estará en el commit final (verifica con `git log -1`).

## Notas de Configuración

- La forma recomendada de configurar gac es ejecutar `gac init` y seguir las instrucciones interactivas.
- ¿Ya tienes el idioma configurado y solo necesitas cambiar proveedores o modelos? Ejecuta `gac model` para repetir la configuración sin preguntas de idioma.
- **¿Usas Claude Code?** Consulta la [guía de configuración de Claude Code](CLAUDE_CODE.md) para instrucciones de autenticación OAuth.
- **¿Usas ChatGPT OAuth?** Consulta la [guía de configuración de ChatGPT OAuth](CHATGPT_OAUTH.md) para instrucciones de autenticación basada en navegador.
- **¿Usas GitHub Copilot?** Consulta la [guía de configuración de GitHub Copilot](GITHUB_COPILOT.md) para instrucciones de autenticación Device Flow.
- gac carga configuración en el siguiente orden de precedencia:
  1. Banderas CLI
  2. Variables de entorno
  3. Nivel de proyecto `.gac.env`
  4. Nivel de usuario `~/.gac.env`

### Opciones de Configuración Avanzadas

Puedes personalizar el comportamiento de gac con estas variables de entorno opcionales:

- `GAC_EDITOR=code --wait` - Sobrescribe el editor usado cuando presionas `e` en el prompt de confirmación. Por defecto, `e` abre una TUI in-place; establecer `GAC_EDITOR` cambia a un editor externo. Soporta cualquier comando de editor con argumentos. Los flags de espera (`--wait`/`-w`) se insertan automáticamente para editores GUI conocidos (VS Code, Cursor, Zed, Sublime Text) para que el proceso se bloquee hasta que cierres el archivo
- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Inferir automáticamente e incluir scope en mensajes de commit (ej., `feat(auth):` vs `feat:)
- `GAC_VERBOSE=true` - Generar mensajes de commit detallados con secciones de motivación, arquitectura e impacto
- `GAC_USE_50_72_RULE=true` - Aplicar siempre la regla 50/72 para los mensajes de commit (asunto ≤50 caracteres, líneas del cuerpo ≤72 caracteres)
- `GAC_SIGNOFF=true` - Agregar siempre línea Signed-off-by a los commits (para cumplimiento DCO)
- `GAC_TEMPERATURE=0.7` - Controlar la creatividad del LLM (0.0-1.0, más bajo = más enfocado)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Tokens máximos para mensajes generados (escalado automáticamente 2-5x cuando usas `--group` basado en el conteo de archivos; anula para ir más alto o más bajo)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Advertir cuando los prompts excedan este conteo de tokens
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Usar un prompt de sistema personalizado para generación de mensajes de commit
- `GAC_LANGUAGE=Spanish` - Generar mensajes de commit en un idioma específico (ej., Spanish, French, Japanese, German). Soporta nombres completos o códigos ISO (es, fr, ja, de, zh-CN). Usa `gac language` para selección interactiva
- `GAC_TRANSLATE_PREFIXES=true` - Traducir prefijos de commit convencionales (feat, fix, etc.) al idioma de destino (default: false, mantiene prefijos en inglés)
- `GAC_SKIP_SECRET_SCAN=true` - Deshabilitar escaneo de seguridad automático para secretos en cambios staged (usa con precaución)
- `GAC_NO_VERIFY_SSL=true` - Omitir verificación de certificado SSL para llamadas API (útil para proxies corporativos que interceptan tráfico SSL)
- `GAC_DISABLE_STATS=true` - Desactivar el seguimiento de estadísticas de uso (no se leen ni escriben archivos de estadísticas; los datos existentes se conservan). Solo los valores truthy desactivan las estadísticas; establecerlo en `false`/`0`/`no`/`off` mantiene las estadísticas activadas, igual que dejar la variable sin establecer

Consulta `.gac.env.example` para una plantilla de configuración completa.

Para guía detallada sobre creating prompts de sistema personalizados, consulta [docs/CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md).

### Subcomandos de Configuración

Los siguientes subcomandos están disponibles:

- `gac init` — Asistente de configuración interactivo para proveedor, modelo e idioma
- `gac model` — Configuración de proveedor/modelo/API clave sin indicaciones de idioma (ideal para cambios rápidos)
- `gac auth` — Mostrar estado de autenticación OAuth para todos los proveedores
- `gac auth claude-code login` — Iniciar sesión en Claude Code usando OAuth (abre navegador)
- `gac auth claude-code logout` — Cerrar sesión en Claude Code y eliminar token almacenado
- `gac auth claude-code status` — Comprobar estado de autenticación de Claude Code
- `gac auth chatgpt login` — Iniciar sesión en ChatGPT usando OAuth (abre navegador)
- `gac auth chatgpt logout` — Cerrar sesión en ChatGPT y eliminar token almacenado
- `gac auth chatgpt status` — Comprobar estado de autenticación de ChatGPT
- `gac auth copilot login` — Iniciar sesión en GitHub Copilot usando Device Flow
- `gac auth copilot login --host ghe.mycompany.com` — Iniciar sesión en Copilot en una instancia de GitHub Enterprise
- `gac auth copilot logout` — Cerrar sesión en Copilot y eliminar tokens almacenados
- `gac auth copilot status` — Comprobar estado de autenticación de Copilot
- `gac config show` — Mostrar configuración actual
- `gac config set KEY VALUE` — Establecer clave de configuración en `$HOME/.gac.env`
- `gac config get KEY` — Obtener valor de configuración
- `gac config unset KEY` — Eliminar clave de configuración de `$HOME/.gac.env`
- `gac language` (o `gac lang`) — Selector de idioma interactivo para mensajes de commit (establece GAC_LANGUAGE)
- `gac editor` (o `gac edit`) — Selector de editor interactivo para la tecla `e` en el prompt de confirmación (establece GAC_EDITOR)
- `gac diff` — Mostrar git diff filtrado con opciones para cambios preparados/no preparados, color y truncamiento
- `gac serve` — Iniciar GAC como [servidor MCP](MCP.md) para integración con agentes de IA (transporte stdio)
- `gac stats show` — Ver tus estadísticas de uso de gac (totales, rachas, actividad diaria y semanal, uso de tokens, proyectos principales, modelos principales)
- `gac stats models` — Ver estadísticas detalladas de todos los modelos con desglose de tokens y gráfico de comparación de velocidad
- `gac stats projects` — Ver estadísticas de todos los proyectos con desglose de tokens
- `gac stats reset` — Restablecer todas las estadísticas a cero (solicita confirmación)

## Modo Interactivo

El flag `--interactive` (`-i`) mejora la generación de mensajes de commit de gac al hacerte preguntas dirigidas sobre tus cambios. Este contexto adicional ayuda al LLM a crear mensajes de commit más precisos, detallados y contextualmente apropiados.

### Cómo Funciona

Cuando usas `--interactive`, gac te hará preguntas como:

- **¿Cuál es el propósito principal de estos cambios?** - Ayuda a entender el objetivo de alto nivel
- **¿Qué problema estás resolviendo?** - Proporciona contexto sobre la motivación
- **¿Hay algún detalle de implementación que valga la pena mencionar?** - Captura especificidades técnicas
- **¿Hay cambios breaking?** - Identifica problemas de impacto potencial
- **¿Esto está relacionado con algún issue o ticket?** - Vincula con la gestión de proyectos

### Cuándo Usar el Modo Interactivo

El modo interactivo es particularmente útil para:

- **Cambios complejos** donde el contexto no es obvio solo desde el diff
- **Trabajo de refactoring** que abarca múltiples archivos y conceptos
- **Nuevas características** que requieren explicación del propósito general
- **Correcciones de bugs** donde la causa raíz no es inmediatamente visible
- **Optimizaciones de rendimiento** donde el razonamiento no es obvio
- **Preparación de code review** - las preguntas te ayudan a pensar en tus cambios

### Ejemplos de Uso

**Modo interactivo básico:**

```sh
gac -i
```

Esto hará:

1. Mostrarte un resumen de los cambios staged
2. Hacerte preguntas sobre los cambios
3. Generar un mensaje de commit incorporando tus respuestas
4. Pedir confirmación (o auto-confirmar si se combina con `-y`)

**Modo interactivo con cambios staged:**

```sh
gac -ai
# Hace staging de todos los cambios, luego hace preguntas para mejor contexto
```

**Modo interactivo con pistas específicas:**

```sh
gac -i -h "Migración de base de datos para perfiles de usuario"
# Hacer preguntas mientras proporcionas una pista específica para enfocar el LLM
```

**Modo interactivo con salida detallada:**

```sh
gac -i -v
# Hacer preguntas y generar un mensaje de commit detallado y estructurado
```

**Modo interactivo auto-confirmado:**

```sh
gac -i -y
# Hacer preguntas pero auto-confirmar el commit resultante
```

### Flujo de Preguntas y Respuestas

El flujo de trabajo interactivo sigue este patrón:

1. **Revisar cambios** - gac muestra un resumen de lo que estás cometiendo
2. **Responder preguntas** - responde a cada prompt con detalles relevantes
3. **Mejora de contexto** - tus respuestas se agregan al prompt del LLM
4. **Generación de mensaje** - el LLM crea un mensaje de commit con contexto completo
5. **Confirmación** - revisa y confirma el commit (o auto-confirma con `-y`)

**Consejos para proporcionar respuestas útiles:**

- **Sé conciso pero completo** - proporciona los detalles clave sin ser demasiado verboso
- **Enfócate en el "por qué"** - explica el razonamiento detrás de tus cambios
- **Menciona restricciones** - nota cualquier limitación o consideración especial
- **Vincula con contexto externo** - referencia issues, documentación o documentos de diseño
- **Las respuestas vacías están bien** - si una pregunta no aplica, solo presiona Enter

### Combinación con otros Flags

El modo interactivo funciona bien con la mayoría de los otros flags:

```sh
# Hacer staging de todos los cambios y hacer preguntas
gac -ai

# Hacer preguntas con salida detallada
gac -i -v
```

### Mejores Prácticas

- **Usar para PRs complejas** - especialmente útil para pull requests que necesitan descripciones detalladas
- **Colaboración en equipo** - las preguntas te ayudan a pensar en los cambios que otros revisarán
- **Preparación de documentación** - tus respuestas pueden ayudar a formar la base de las release notes
- **Herramienta de aprendizaje** - las preguntas refuerzan buenas prácticas de mensajes de commit
- **Omitir al hacer cambios simples** - para correcciones triviales, el modo básico puede ser más rápido

## Estadísticas de Uso

gac rastrea estadísticas de uso ligeras para que puedas ver tu actividad de commits, rachas, uso de tokens, y proyectos y modelos más activos. Las estadísticas se almacenan localmente en `~/.gac_stats.json` y nunca se envían a ningún lugar — no hay telemetría.

**Qué se rastrea:** ejecuciones totales de gac, commits totales, tokens de prompt y completion totales, fechas de primer/último uso, conteos diarios y semanales (gacs, commits, tokens), racha actual y más larga, actividad por proyecto (gacs, commits, tokens de prompt + completion) y actividad por modelo (gacs, tokens de prompt + completion).

**Qué NO se rastrea:** mensajes de commit, contenido de código, rutas de archivos, información personal o cualquier cosa más allá de conteos, fechas, nombres de proyectos (derivados del remoto o directorio de git) y nombres de modelos.

### Opt-in u Opt-out

`gac init` pregunta si deseas activar las estadísticas y explica exactamente qué se almacena. Puedes cambiar de opinión en cualquier momento:

- **Activar estadísticas:** desactiva `GAC_DISABLE_STATS` o establace en `false`/`0`/`no`/`off`/vacío.
- **Desactivar estadísticas:** establece `GAC_DISABLE_STATS` a un valor truthy (`true`, `1`, `yes`, `on`).

Cuando rechazas las estadísticas durante `gac init` y se detecta un archivo `~/.gac_stats.json` existente, se te ofrecerá la opción de eliminarlo.

### Subcomandos de Estadísticas

| Comando              | Descripción                                                                                                                            |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `gac stats`          | Mostrar tus estadísticas (igual que `gac stats show`)                                                                                  |
| `gac stats show`     | Mostrar estadísticas completas: totales, rachas, actividad diaria y semanal, uso de tokens, proyectos principales, modelos principales |
| `gac stats models`   | Mostrar estadísticas detalladas de **todos** los modelos usados, con desglose de tokens y gráfico de comparación de velocidad          |
| `gac stats projects` | Mostrar estadísticas de **todos** los proyectos con desglose de tokens                                                                 |
| `gac stats reset`    | Restablecer todas las estadísticas a cero (solicita confirmación)                                                                      |

### Ejemplos

```sh
# Ver tus estadísticas generales
gac stats

# Desglose detallado de todos los modelos usados
gac stats models

# Estadísticas de todos los proyectos
gac stats projects

# Restablecer todas las estadísticas (con confirmación)
gac stats reset
```

### Lo que verás

Ejecutar `gac stats` muestra:

- **Gacs y commits totales** — cuántas veces has usado gac y cuántos commits ha creado
- **Racha actual y más larga** — días consecutivos con actividad de gac (🔥 a 5+ días)
- **Resumen de actividad** — gacs, commits y tokens de hoy y esta semana vs tu pico diario y semanal
- **Proyectos principales** — tus 5 repos más activos por conteo de gac + commits, con uso de tokens por proyecto

Running `gac stats projects` muestra **todos** los proyectos (no solo los 5 principales) con:

- **Tabla de todos los proyectos** — cada proyecto ordenado por actividad, con conteo de gac, conteo de commits, tokens de prompt, tokens de completion, tokens de razonamiento y tokens totales
- **Modelos principales** — tus 5 modelos más usados con tokens de prompt, completion y totales consumidos

Running `gac stats models` muestra **todos** los modelos (no solo los 5 principales) con:

- **Tabla de todos los modelos** — cada modelo usado ordenado por actividad, con conteo de gac, velocidad (tokens/seg), tokens de prompt, tokens de completion, tokens de razonamiento y tokens totales
- **Gráfico de comparación de velocidad** — un gráfico de barras horizontal de todos los modelos con velocidades conocidas, ordenados de más rápido a más lento, codificados por color según percentil de velocidad (🟡 rapidísimo, 🟢 rápido, 🔵 moderado, 🔘 lento)
- **Celebraciones de récord** — 🏆 trofeos cuando estableces nuevos récords diarios, semanales, de tokens o de racha; 🥈 por empatarlos
- **Mensajes de ánimo** — sugerencias contextuales basadas en tu actividad

### Desactivar estadísticas

Establece la variable de entorno `GAC_DISABLE_STATS` con un valor truthy:

```sh
# Desactivar seguimiento de estadísticas
export GAC_DISABLE_STATS=true

# O en .gac.env
GAC_DISABLE_STATS=true
```

Los valores falsy (`false`, `0`, `no`, `off`, vacío) mantienen las estadísticas activadas — igual que dejar la variable sin establecer.

Cuando está desactivado, gac omite todo el registro de estadísticas — no se realizan lecturas ni escrituras de archivos. Los datos existentes se conservan pero no se actualizarán hasta que las vuelvas a activar.

---

## Obtención de Ayuda

- Para configuración del servidor MCP (integración con agentes de IA), consulta [docs/MCP.md](MCP.md)
- Para prompts de sistema personalizados, consulta [docs/CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)
- Para configuración OAuth de Claude Code, consulta [CLAUDE_CODE.md](CLAUDE_CODE.md)
- Para configuración OAuth de ChatGPT, consulta [CHATGPT_OAUTH.md](CHATGPT_OAUTH.md)
- Para configuración de GitHub Copilot, consulta [GITHUB_COPILOT.md](GITHUB_COPILOT.md)
- Para solución de problemas y consejos avanzados, consulta [docs/TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- Para instalación y configuración, consulta [README.md#configuración](README.md#configuración)
- Para contribuir, consulta [docs/CONTRIBUTING.md](../CONTRIBUTING.md)
- Información de licencia: [LICENSE](../LICENSE)
