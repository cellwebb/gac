# Solución de problemas de gac

[English](../en/TROUBLESHOOTING.md) | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | [한국어](../ko/TROUBLESHOOTING.md) | [हिन्दी](../hi/TROUBLESHOOTING.md) | [Tiếng Việt](../vi/TROUBLESHOOTING.md) | [Français](../fr/TROUBLESHOOTING.md) | [Русский](../ru/TROUBLESHOOTING.md) | **Español** | [Português](../pt/TROUBLESHOOTING.md) | [Norsk](../no/TROUBLESHOOTING.md) | [Svenska](../sv/TROUBLESHOOTING.md) | [Deutsch](../de/TROUBLESHOOTING.md) | [Nederlands](../nl/TROUBLESHOOTING.md) | [Italiano](../it/TROUBLESHOOTING.md)

Esta guía cubre problemas comunes y soluciones para instalar, configurar y ejecutar gac.

## Tabla de Contenidos

- [Solución de problemas de gac](#solución-de-problemas-de-gac)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [1. Problemas de Instalación](#1-problemas-de-instalación)
  - [2. Problemas de Configuración](#2-problemas-de-configuración)
  - [3. Errores de Proveedor/API](#3-errores-de-proveedorapi)
  - [4. Problemas de Agrupación de Commits](#4-problemas-de-agrupación-de-commits)
  - [5. Seguridad y Detección de Secretos](#5-seguridad-y-detección-de-secretos)
  - [6. Problemas con Hooks de Pre-commit y Lefthook](#6-problemas-con-hooks-de-pre-commit-y-lefthook)
  - [7. Problemas Comunes del Flujo de Trabajo](#7-problemas-comunes-del-flujo-de-trabajo)
  - [8. Depuración General](#8-depuración-general)
  - [¿Sigues Atascado?](#sigues-atascado)
    [Dónde Obtener Ayuda Adicional](#dónde-obtener-ayuda-adicional)

## 1. Problemas de Instalación

**Problema:** Comando `gac` no encontrado después de la instalación

- Asegúrate de instalar con `uv tool install gac` o `uvx gac`
- Si usaste `uv tool install`, verifica la instalación con `uv tool list`
- Asegúrate de que `uv` esté instalado y en tu `$PATH`
- Reinicia tu terminal después de la instalación

**Problema:** Permiso denegado o no puede escribir archivos

- Verifica los permisos del directorio
- Intenta ejecutar con privilegios apropiados o cambia la propiedad del directorio

## 2. Problemas de Configuración

**Problema:** gac no puede encontrar tu clave API o modelo

- Si eres nuevo, ejecuta `gac init` para configurar interactivamente tu proveedor, modelo y claves API
- Asegúrate de que tu `.gac.env` o variables de entorno estén configuradas correctamente
- Ejecuta `gac --log-level=debug` para ver qué archivos de configuración se cargan y depurar problemas de configuración
- Verifica si hay errores tipográficos en los nombres de las variables (ej. `GAC_GROQ_API_KEY`)

**Problema:** Los cambios en `$HOME/.gac.env` a nivel de usuario no se detectan

- Asegúrate de estar editando el archivo correcto para tu SO:
  - En macOS/Linux: `$HOME/.gac.env` (usualmente `/Users/<tu-usuario>/.gac.env` o `/home/<tu-usuario>/.gac.env`)
  - En Windows: `$HOME/.gac.env` (típicamente `C:\Users\<tu-usuario>\.gac.env` o usa `%USERPROFILE%`)
- Ejecuta `gac --log-level=debug` para confirmar que la configuración a nivel de usuario se carga
- Reinicia tu terminal o vuelve a ejecutar tu shell para recargar las variables de entorno
- Si aún no funciona, verifica si hay errores tipográficos y permisos de archivo

**Problema:** Los cambios en `.gac.env` a nivel de proyecto no se detectan

- Asegúrate de que tu proyecto contenga un archivo `.gac.env` en el directorio raíz (junto a tu carpeta `.git`)
- Ejecuta `gac --log-level=debug` para confirmar que la configuración a nivel de proyecto se carga
- Si editas `.gac.env`, reinicia tu terminal o vuelve a ejecutar tu shell para recargar las variables de entorno
- Si aún no funciona, verifica si hay errores tipográficos y permisos de archivo

**Problema:** No se puede establecer o cambiar el idioma para los mensajes de commit

- Ejecuta `gac language` (o `gac lang`) para seleccionar interactivamente entre más de 25 idiomas compatibles
- Usa la bandera `-l <idioma>` para anular el idioma para un solo commit (ej. `gac -l zh-CN`, `gac -l Spanish`)
- Verifica tu configuración con `gac config show` para ver el ajuste de idioma actual
- La configuración de idioma se almacena en `GAC_LANGUAGE` en tu archivo `.gac.env`

## 3. Errores de Proveedor/API

**Problema:** Errores de autenticación o API

- Asegúrate de haber configurado las claves API correctas para el modelo elegido (ej. `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- Verifica doblemente tu clave API y el estado de tu cuenta del proveedor
- Para Ollama y LM Studio, confirma que la URL de API coincida con tu instancia local. Las claves API solo son necesarias si habilitaste la autenticación.
- **Para problemas de OAuth con Claude Code**, consulta la [guía de configuración de Claude Code](CLAUDE_CODE.md) para ayuda con autenticación y expiración de tokens.

**Problema:** Modelo no disponible o no compatible

- Streamlake usa IDs de endpoints de inferencia en lugar de nombres de modelo. Asegúrate de proporcionar el ID del endpoint desde su consola.
- Verifica que el nombre del modelo sea correcto y sea compatible con tu proveedor
- Consulta la documentación del proveedor para ver los modelos disponibles

## 4. Problemas de Agrupación de Commits

**Problema:** La bandera `--group` no funciona como se espera

- La bandera `--group` analiza automáticamente los cambios en staging y puede crear múltiples commits lógicos
- El LLM puede decidir que un solo commit tiene sentido para tu conjunto de cambios en staging, incluso con `--group`
- Este es un comportamiento intencional: el LLM agrupa los cambios basándose en relaciones lógicas, no solo en la cantidad
- Asegúrate de tener múltiples cambios no relacionados en staging (ej. corrección de error + adición de característica) para mejores resultados
- Usa `gac --show-prompt` para depurar qué está viendo el LLM

**Problema:** Los commits se agrupan incorrectamente o no se agrupan cuando se espera

- La agrupación la determina el análisis del LLM de tus cambios
- El LLM puede crear un solo commit si determina que los cambios están lógicamente relacionados
- Intenta agregar pistas con `-h "pista"` para guiar la lógica de agrupación (ej., `-h "separar corrección de error de refactorización"`)
- Revisa los grupos generados antes de confirmar
- Si la agrupación no funciona bien para tu caso de uso, en su lugar confirma los cambios por separado

## 5. Seguridad y Detección de Secretos

**Problema:** Falso positivo: el escaneo de secretos detecta no-secretos

- El escáner de seguridad busca patrones que se parezcan a claves API, tokens y contraseñas
- Si estás confirmando código de ejemplo, fixtures de prueba o documentación con claves de marcador de posición, puedes ver falsos positivos
- Usa `--skip-secret-scan` para omitir el escaneo si estás seguro de que los cambios son seguros
- Considera excluir archivos de prueba/ejemplo de los commits, o usa marcadores de posición claramente etiquetados

**Problema:** El escaneo de secretos no detecta secretos reales

- El escáner usa coincidencia de patrones y puede no capturar todos los tipos de secretos
- Siempre revisa tus cambios en staging con `git diff --staged` antes de confirmar
- Considera usar herramientas de seguridad adicionales como `git-secrets` o `gitleaks` para protección completa
- Reporta cualquier patrón omitido como problemas para ayudar a mejorar la detección

**Problema:** Necesidad de deshabilitar permanentemente el escaneo de secretos

- Establece `GAC_SKIP_SECRET_SCAN=true` en tu archivo `.gac.env`
- Usa `gac config set GAC_SKIP_SECRET_SCAN true`
- Nota: Solo deshabilita si tienes otras medidas de seguridad en su lugar

## 6. Problemas con Hooks de Pre-commit y Lefthook

**Problema:** Los hooks de pre-commit o lefthook están fallando y bloqueando commits

- Usa `gac --no-verify` para omitir temporalmente todos los hooks de pre-commit y lefthook
- Soluciona los problemas subyacentes que causan que los hooks fallen
- Considera ajustar tu configuración de pre-commit o lefthook si los hooks son demasiado estrictos

**Problema:** Los hooks de pre-commit o lefthook tardan demasiado o están interfiriendo con el flujo de trabajo

- Usa `gac --no-verify` para omitir temporalmente todos los hooks de pre-commit y lefthook
- Considera configurar los hooks de pre-commit en `.pre-commit-config.yaml` o los hooks de lefthook en `.lefthook.yml` para que sean menos agresivos para tu flujo de trabajo
- Revisa tu configuración de hooks para optimizar el rendimiento

## 7. Problemas Comunes del Flujo de Trabajo

**Problema:** No hay cambios que confirmar / nada en staging

- gac requiere cambios en staging para generar un mensaje de commit
- Usa `git add <archivos>` para poner cambios en staging, o usa `gac -a` para poner en staging automáticamente todos los cambios
- Verifica `git status` para ver qué archivos han sido modificados
- Usa `gac diff` para ver una vista filtrada de tus cambios

**Problema:** El mensaje de commit no es el que esperaba

- Usa el sistema de retroalimentación interactivo: escribe `r` para volver a generar, `e` para editar, o proporciona retroalimentación en lenguaje natural
- Agrega contexto con `-h "tu pista"` para guiar al LLM
- Usa `-o` para mensajes más simples de una línea o `-v` para mensajes más detallados
- Usa `--show-prompt` para ver qué información está recibiendo el LLM

**Problema:** gac es demasiado lento

- Usa `gac -y` para omitir el prompt de confirmación
- Usa `gac -q` para el modo silencioso con menos salida
- Considera usar modelos más rápidos/baratos para commits de rutina
- Usa `gac --no-verify` para omitir hooks si te están ralentizando

**Problema:** No se puede editar o proporcionar retroalimentación después de la generación del mensaje

- En el prompt, escribe `e` para entrar en modo edición (soporta atajos de teclado vi/emacs)
- Escribe `r` para regenerar sin retroalimentación
- O simplemente escribe tu retroalimentación directamente (ej. "hazlo más corto", "enfócate en la corrección del error")
- Presiona Enter en entrada vacía para ver el prompt nuevamente

## 8. Depuración General

- Usa `gac init` para restablecer o actualizar tu configuración interactivamente
- Usa `gac --log-level=debug` para salida de depuración detallada y registro
- Usa `gac --show-prompt` para ver qué prompt se está enviando al LLM
- Usa `gac --help` para ver todas las banderas de línea de comandos disponibles
- Usa `gac config show` para ver todos los valores de configuración actuales
- Revisa los registros en busca de mensajes de error y trazas de pila
- Revisa el [README.md](../README.md) principal para características, ejemplos e instrucciones de inicio rápido

## ¿Sigues Atascado?

- Buscar problemas existentes o abrir uno nuevo en el [repositorio GitHub](https://github.com/cellwebb/gac)
- Incluir detalles sobre tu SO, versión de Python, versión de gac, proveedor y salida de error
- Cuanto más detalle proporciones, más rápido se puede resolver tu problema

## Dónde Obtener Ayuda Adicional

- Para características y ejemplos de uso, consulta el [README.md](../README.md) principal
- Para prompts de sistema personalizados, consulta [CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md)
- Para pautas de contribución, consulta [CONTRIBUTING.md](../CONTRIBUTING.md)
- Para información de licencia, consulta [LICENSE](../LICENSE)
