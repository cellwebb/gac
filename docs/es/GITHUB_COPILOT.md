# Usar GitHub Copilot con GAC

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | **Español** | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC admite autenticación a través de GitHub Copilot, permitiéndote usar tu suscripción de Copilot para acceder a modelos de OpenAI, Anthropic, Google y más — todo incluido en tu plan de GitHub Copilot.

## ¿Qué es GitHub Copilot OAuth?

GitHub Copilot OAuth usa el **Device Flow** — un método de autenticación seguro basado en navegador que no requiere un servidor de callback local. Visitas una URL, introduces un código de un solo uso y autorizas a GAC a usar tu acceso de Copilot. En segundo plano, GAC intercambia tu token OAuth de GitHub de larga duración por tokens de sesión de Copilot de corta duración (~30 min) que otorgan acceso a la API de Copilot.

Esto te da acceso a modelos de múltiples proveedores a través de una única suscripción:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Beneficios

- **Acceso multi-proveedor**: Usa modelos de OpenAI, Anthropic y Google a través de una única suscripción
- **Rentable**: Usa tu suscripción existente de Copilot en lugar de pagar por claves de API separadas
- **Sin gestión de claves de API**: Autenticación Device Flow — no hay claves que rotar o almacenar
- **Soporte para GitHub Enterprise**: Funciona con instancias GHE a través del flag `--host`

## Configuración

### Opción 1: Durante la configuración inicial (Recomendado)

Al ejecutar `gac init`, simplemente selecciona «Copilot» como tu proveedor:

```bash
gac init
```

El asistente:

1. Te pedirá que selecciones «Copilot» de la lista de proveedores
2. Mostrará un código de un solo uso y abrirá tu navegador para la autenticación Device Flow
3. Guardará tu token OAuth en `~/.gac/oauth/copilot.json`
4. Establecerá el modelo predeterminado

### Opción 2: Cambiar a Copilot más tarde

Si ya tienes GAC configurado con otro proveedor:

```bash
gac model
```

Luego selecciona «Copilot» de la lista de proveedores y autentícate.

### Opción 3: Inicio de sesión directo

Autentícate directamente sin cambiar tu modelo predeterminado:

```bash
gac auth copilot login
```

### Usar GAC normalmente

Una vez autenticado, usa GAC como de costumbre:

```bash
# Prepara tus cambios
git add .

# Genera y confirma con Copilot
gac

# O anula el modelo para un commit único
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Modelos disponibles

Copilot proporciona acceso a modelos de múltiples proveedores. Los modelos actuales incluyen:

| Proveedor | Modelos                                                                                        |
| --------- | ---------------------------------------------------------------------------------------------- |
| OpenAI    | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google    | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Nota:** La lista de modelos mostrada después del inicio de sesión es informativa y puede quedar desactualizada a medida que GitHub añade nuevos modelos. Consulta la [documentación de GitHub Copilot](https://docs.github.com/en/copilot) para los modelos disponibles más recientes.

## GitHub Enterprise

Para autenticarte con una instancia de GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC usará automáticamente los endpoints correctos de Device Flow y API para tu instancia GHE. El token de sesión se cachea por host, por lo que diferentes instancias GHE se gestionan de forma independiente.

## Comandos de CLI

GAC proporciona comandos de CLI dedicados para la gestión de autenticación de Copilot:

### Iniciar sesión

Autentícate o vuelve a autenticarte con GitHub Copilot:

```bash
gac auth copilot login
```

Tu navegador se abrirá en una página de Device Flow donde introduces un código de un solo uso. Si ya estás autenticado, se te preguntará si deseas re-autenticarte.

Para GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Cerrar sesión

Elimina los tokens de Copilot almacenados:

```bash
gac auth copilot logout
```

Esto elimina el archivo de token almacenado en `~/.gac/oauth/copilot.json` y la caché de sesión.

### Estado

Verifica tu estado de autenticación de Copilot actual:

```bash
gac auth copilot status
```

O verifica todos los proveedores a la vez:

```bash
gac auth
```

## Cómo funciona

El flujo de autenticación de Copilot difiere del OAuth de ChatGPT y Claude Code:

1. **Device Flow** — GAC solicita un código de dispositivo a GitHub y lo muestra
2. **Autorización del navegador** — Visitas la URL e introduces el código
3. **Sondeo de token** — GAC consulta a GitHub hasta que completes la autorización
4. **Intercambio de token de sesión** — El token OAuth de GitHub se intercambia por un token de sesión de Copilot de corta duración
5. **Auto-refresh** — Los tokens de sesión (~30 min) se renuevan automáticamente desde el token OAuth cacheado

A diferencia del OAuth basado en PKCE (ChatGPT/Claude Code), el Device Flow no requiere un servidor de callback local ni gestión de puertos.

## Solución de problemas

### «Autenticación de Copilot no encontrada»

Ejecuta el comando de inicio de sesión para autenticarte:

```bash
gac auth copilot login
```

### «No se pudo obtener el token de sesión de Copilot»

Esto significa que GAC obtuvo un token OAuth de GitHub pero no pudo intercambiarlo por un token de sesión de Copilot. Normalmente esto significa:

1. **Sin suscripción de Copilot** — Tu cuenta de GitHub no tiene una suscripción activa de Copilot
2. **Token revocado** — El token OAuth fue revocado; re-autentícate con `gac auth copilot login`

### Token de sesión expirado

Los tokens de sesión expiran después de ~30 minutos. GAC los renueva automáticamente desde el token OAuth cacheado, por lo que no deberías necesitar re-autenticarte frecuentemente. Si el auto-refresh falla:

```bash
gac auth copilot login
```

### «Nombre de host no válido o inseguro»

El flag `--host` valida los nombres de host estrictamente para prevenir ataques SSRF. Si ves este error:

- Asegúrate de que el nombre de host no incluya puertos (ej. usa `ghe.company.com` no `ghe.company.com:8080`)
- No incluyas protocolos ni rutas (ej. usa `ghe.company.com` no `https://ghe.company.com/api`)
- Las direcciones IP privadas y `localhost` están bloqueadas por seguridad

### Problemas de GitHub Enterprise

Si la autenticación GHE falla:

1. Verifica que tu instancia GHE tenga Copilot habilitado
2. Comprueba que el nombre de host de tu GHE sea accesible desde tu máquina
3. Asegúrate de que tu cuenta GHE tenga una licencia de Copilot
4. Intenta con el flag `--host` explícitamente: `gac auth copilot login --host ghe.mycompany.com`

## Diferencias con otros proveedores OAuth

| Característica     | ChatGPT OAuth                 | Claude Code                  | Copilot                                       |
| ------------------ | ----------------------------- | ---------------------------- | --------------------------------------------- |
| Método de auth     | PKCE (callback de navegador)  | PKCE (callback de navegador) | Device Flow (código de un solo uso)           |
| Servidor callback  | Puertos 1455-1465             | Puertos 8765-8795            | No necesario                                  |
| Duración del token | Larga duración (auto-refresh) | Expirando (re-auth)          | Sesión ~30 min (auto-refresh)                 |
| Modelos            | OpenAI optimizado para Codex  | Familia Claude               | Multi-proveedor (OpenAI + Anthropic + Google) |
| Soporte GHE        | No                            | No                           | Sí (flag `--host`)                            |

## Notas de seguridad

- **Nunca hagas commit de tu token OAuth** al control de versiones
- GAC almacena tokens OAuth en `~/.gac/oauth/copilot.json` (fuera del directorio de tu proyecto)
- Los tokens de sesión se cachean en `~/.gac/oauth/copilot_session.json` con permisos `0o600`
- Los nombres de host se validan estrictamente para prevenir ataques SSRF e inyección de URL
- Las direcciones IP privadas, direcciones de loopback y `localhost` están bloqueados como nombres de host
- El Device Flow no expone ningún puerto local, reduciendo la superficie de ataque

## Véase también

- [Documentación principal](USAGE.md)
- [Guía de solución de problemas](TROUBLESHOOTING.md)
- [Guía de ChatGPT OAuth](CHATGPT_OAUTH.md)
- [Guía de Claude Code](CLAUDE_CODE.md)
- [Documentación de GitHub Copilot](https://docs.github.com/en/copilot)
