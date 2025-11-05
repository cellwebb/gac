# Usar Claude Code con GAC

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | **Español** | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC admite la autenticación mediante suscripciones de Claude Code, permitiéndote usar tu suscripción de Claude Code en lugar de pagar por la costosa API de Anthropic. Esto es perfecto para usuarios que ya tienen acceso a Claude Code a través de su suscripción.

## ¿Qué es Claude Code?

Claude Code es el servicio de suscripción de Anthropic que proporciona acceso a los modelos Claude mediante OAuth. En lugar de usar claves API (que se facturan por token), Claude Code usa tokens OAuth de tu suscripción.

## Beneficios

- **Rentable**: Usa tu suscripción existente de Claude Code en lugar de pagar por separado por acceso a la API
- **Mismos modelos**: Accede a los mismos modelos Claude (ej., `claude-sonnet-4-5`)
- **Facturación separada**: El uso de Claude Code está separado de la facturación de la API de Anthropic

## Configuración

GAC incluye autenticación OAuth incorporada para Claude Code. El proceso de configuración está completamente automatizado y abrirá tu navegador para autenticación.

### Opción 1: Durante la Configuración Inicial (Recomendado)

Al ejecutar `gac init`, simplemente selecciona "Claude Code" como tu proveedor:

```bash
gac init
```

El asistente:

1. Te pedirá que selecciones "Claude Code" de la lista de proveedores
2. Abrirá automáticamente tu navegador para autenticación OAuth
3. Guardará tu token de acceso en `~/.gac.env`
4. Establecerá el modelo predeterminado

### Opción 2: Cambiar a Claude Code Más Tarde

Si ya tienes GAC configurado con otro proveedor y quieres cambiar a Claude Code:

```bash
gac model
```

Luego:

1. Selecciona "Claude Code" de la lista de proveedores
2. Tu navegador se abrirá automáticamente para autenticación OAuth
3. Token guardado en `~/.gac.env`
4. Modelo configurado automáticamente

### Usar GAC Normalmente

Una vez autenticado, usa GAC como de costumbre:

```bash
# Prepara tus cambios
git add .

# Genera y confirma con Claude Code
gac

# O anula el modelo para un solo commit
gac -m claude-code:claude-sonnet-4-5
```

## Modelos Disponibles

Claude Code proporciona acceso a los mismos modelos que la API de Anthropic. Los modelos actuales de la familia Claude 4.5 incluyen:

- `claude-sonnet-4-5` - Modelo Sonnet más reciente e inteligente, mejor para codificación
- `claude-haiku-4-5` - Rápido y eficiente
- `claude-opus-4-1` - Modelo más capaz para razonamiento complejo

Consulta la [documentación de Claude](https://docs.claude.com/en/docs/about-claude/models/overview) para la lista completa de modelos disponibles.

## Solución de Problemas

### Token Expirado

Si ves errores de autenticación, tu token puede haber expirado. Reautentícate ejecutando:

```bash
gac model
```

Luego selecciona "Claude Code" y elige "Reautenticar (obtener nuevo token)". Tu navegador se abrirá para nueva autenticación OAuth.

### "CLAUDE_CODE_ACCESS_TOKEN no encontrado"

Esto significa que GAC no puede encontrar tu token de acceso. Autentícate ejecutando:

```bash
gac model
```

Luego selecciona "Claude Code" de la lista de proveedores. El flujo OAuth comenzará automáticamente.

### "Autenticación fallida"

Si la autenticación OAuth falla:

1. Asegúrate de tener una suscripción activa de Claude Code
2. Verifica que tu navegador abra correctamente
3. Intenta un navegador diferente si los problemas persisten
4. Verifica la conectividad de red a `claude.ai`
5. Verifica que los puertos 8765-8795 estén disponibles para el servidor de callback local

## Diferencias con el Proveedor Anthropic

| Característica    | Anthropic (`anthropic:`)        | Claude Code (`claude-code:`)                                     |
| ----------------- | ------------------------------- | ---------------------------------------------------------------- |
| Autenticación     | Clave API (`ANTHROPIC_API_KEY`) | OAuth (flujo automático del navegador)                           |
| Facturación       | Facturación API por token       | Basada en suscripción                                            |
| Configuración     | Entrada manual de clave API     | OAuth automático via `gac init` o `gac model`                    |
| Gestión de Tokens | Claves API de larga duración    | Tokens OAuth (pueden expirar, fácil reautenticación via `model`) |
| Modelos           | Mismos modelos                  | Mismos modelos                                                   |

## Notas de Seguridad

- **Nunca hagas commit de tu token de acceso** al control de versiones
- GAC almacena automáticamente tokens en `~/.gac.env` (fuera de tu directorio de proyecto)
- Los tokens pueden expirar y requerirán reautenticación via `gac model`
- El flujo OAuth usa PKCE (Proof Key for Code Exchange) para seguridad mejorada
- El servidor de callback local solo se ejecuta en localhost (puertos 8765-8795)

## Ver También

- [Documentación Principal](USAGE.md)
- [Guía de Solución de Problemas](TROUBLESHOOTING.md)
- [Documentación de Claude Code](https://claude.ai/code)
