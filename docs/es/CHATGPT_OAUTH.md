# Usar ChatGPT OAuth con GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC admite autenticación a través de ChatGPT OAuth, permitiéndote usar tu suscripción de ChatGPT para acceder a la API Codex de OpenAI en lugar de pagar claves de API de OpenAI por separado. Esto refleja el mismo flujo OAuth utilizado por el CLI Codex de OpenAI.

> ⚠️ **Atención — uso no autorizado:** Esto usa el mismo flujo OAuth que el CLI Codex de OpenAI, y aunque actualmente funciona, OpenAI puede restringir el uso de tokens de terceros en cualquier momento. GAC es lo suficientemente pequeño como para haber pasado desapercibido hasta ahora, pero usar ChatGPT OAuth aquí **no está oficialmente aprobado** para herramientas de terceros y podría dejar de funcionar en cualquier momento. Si necesitas generación confiable de mensajes de commit, usa un proveedor de API directo (`openai`, etc.). Consulta la [documentación de Codex de OpenAI](https://openai.com/codex) para conocer la política actual.

## ¿Qué es ChatGPT OAuth?

ChatGPT OAuth te permite aprovechar tu suscripción existente de ChatGPT Plus o Pro para acceder a la API Codex para generar mensajes de commit. En lugar de administrar claves de API y facturación por token, te autenticas una vez a través de tu navegador y GAC maneja automáticamente el ciclo de vida del token.

## Beneficios

- **Rentable**: Usa tu suscripción existente de ChatGPT Plus/Pro en lugar de pagar por separado el acceso a la API
- **Mismos modelos**: Accede a modelos optimizados para Codex (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **Sin gestión de claves de API**: OAuth basado en navegador significa que no hay claves de API que rotar o almacenar
- **Facturación separada**: El uso de ChatGPT OAuth está separado de la facturación directa de la API de OpenAI

## Configuración

GAC incluye autenticación OAuth integrada para ChatGPT. El proceso de configuración está completamente automatizado y abrirá tu navegador para la autenticación.

### Opción 1: Durante la configuración inicial (Recomendado)

Al ejecutar `gac init`, simplemente selecciona «ChatGPT OAuth» como tu proveedor:

```bash
gac init
```

El asistente:

1. Te pedirá que selecciones «ChatGPT OAuth» de la lista de proveedores
2. Abrirá automáticamente tu navegador para la autenticación OAuth
3. Guardará tu token de acceso en `~/.gac/oauth/chatgpt-oauth.json`
4. Establecerá el modelo predeterminado

### Opción 2: Cambiar a ChatGPT OAuth más tarde

Si ya tienes GAC configurado con otro proveedor y quieres cambiar a ChatGPT OAuth:

```bash
gac model
```

Luego:

1. Selecciona «ChatGPT OAuth» de la lista de proveedores
2. Tu navegador se abrirá automáticamente para la autenticación OAuth
3. Token guardado en `~/.gac/oauth/chatgpt-oauth.json`
4. Modelo configurado automáticamente

### Usar GAC normalmente

Una vez autenticado, usa GAC como de costumbre:

```bash
# Prepara tus cambios
git add .

# Genera y confirma con ChatGPT OAuth
gac

# O anula el modelo para un commit único
gac -m chatgpt-oauth:gpt-5.5
```

## Modelos disponibles

ChatGPT OAuth proporciona acceso a modelos optimizados para Codex. Los modelos actuales incluyen:

- `gpt-5.5` — Modelo Codex más reciente y potente
- `gpt-5.4` — Modelo Codex de generación anterior
- `gpt-5.3-codex` — Modelo Codex de tercera generación

Consulta la [documentación de OpenAI](https://platform.openai.com/docs/models) para obtener la lista completa de modelos disponibles.

## Comandos de CLI

GAC proporciona comandos de CLI dedicados para la gestión de ChatGPT OAuth:

### Iniciar sesión

Autentícate o vuelve a autenticarte con ChatGPT OAuth:

```bash
gac auth chatgpt login
```

Tu navegador se abrirá automáticamente para completar el flujo OAuth. Si ya estás autenticado, esto actualizará tus tokens.

### Cerrar sesión

Elimina los tokens de ChatGPT OAuth almacenados:

```bash
gac auth chatgpt logout
```

Esto elimina el archivo de token almacenado en `~/.gac/oauth/chatgpt-oauth.json`.

### Estado

Verifica tu estado de autenticación de ChatGPT OAuth actual:

```bash
gac auth chatgpt status
```

O verifica todos los proveedores a la vez:

```bash
gac auth
```

## Solución de problemas

### Token caducado

Si ves errores de autenticación, es posible que tu token haya caducado. Vuelve a autenticarte ejecutando:

```bash
gac auth chatgpt login
```

Tu navegador se abrirá automáticamente para una nueva autenticación OAuth. GAC usa automáticamente tokens de actualización para renovar el acceso sin volver a autenticar cuando es posible.

### Verificar el estado de autenticación

Para verificar si estás actualmente autenticado:

```bash
gac auth chatgpt status
```

O verifica todos los proveedores a la vez:

```bash
gac auth
```

### Cerrar sesión

Para eliminar tu token almacenado:

```bash
gac auth chatgpt logout
```

### «No se encontró el token de ChatGPT OAuth»

Esto significa que GAC no puede encontrar tu token de acceso. Autentícate ejecutando:

```bash
gac model
```

Luego selecciona «ChatGPT OAuth» de la lista de proveedores. El flujo OAuth se iniciará automáticamente.

### «Error de autenticación»

Si la autenticación OAuth falla:

1. Asegúrate de tener una suscripción activa de ChatGPT Plus o Pro
2. Verifica que tu navegador se abra correctamente
3. Prueba con otro navegador si los problemas persisten
4. Verifica la conectividad de red con `auth.openai.com`
5. Verifica que los puertos 1455-1465 estén disponibles para el servidor de devolución de llamada local

### Puerto ya en uso

El servidor de devolución de llamada de OAuth prueba automáticamente los puertos 1455-1465. Si todos los puertos están ocupados:

```bash
# En macOS/Linux:
lsof -ti:1455-1465 | xargs kill -9

# En Windows (PowerShell):
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Luego vuelve a ejecutar `gac auth chatgpt login`.

## Diferencias con el proveedor de OpenAI

| Característica    | OpenAI (`openai:`)              | ChatGPT OAuth (`chatgpt-oauth:`)                                       |
| ----------------- | ------------------------------- | ---------------------------------------------------------------------- |
| Autenticación     | Clave de API (`OPENAI_API_KEY`) | OAuth (flujo de navegador automatizado)                                |
| Facturación       | Facturación de API por token    | Basada en suscripción (ChatGPT Plus/Pro)                               |
| Configuración     | Entrada manual de clave de API  | OAuth automático a través de `gac init` o `gac model`                  |
| Gestión de tokens | Claves de API de larga duración | Tokens de OAuth (actualización automática con tokens de actualización) |
| Modelos           | Todos los modelos de OpenAI     | Modelos optimizados para Codex                                         |

## Notas de seguridad

- **Nunca hagas commit de tu token de acceso** al control de versiones
- GAC almacena tokens de OAuth en `~/.gac/oauth/chatgpt-oauth.json` (fuera del directorio de tu proyecto)
- El flujo de OAuth usa PKCE (Proof Key for Code Exchange) para mayor seguridad
- El servidor de devolución de llamada local se ejecuta solo en localhost (puertos 1455-1465)
- Los tokens de actualización se usan para renovar automáticamente el acceso sin volver a autenticar

## Véase también

- [Documentación principal](USAGE.md)
- [Guía de solución de problemas](TROUBLESHOOTING.md)
- [Documentación de Codex de OpenAI](https://openai.com/codex)
