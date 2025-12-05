[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | **Español** | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# Usar Qwen.ai con GAC

GAC admite la autenticación a través de Qwen.ai OAuth, lo que le permite usar su cuenta de Qwen.ai para la generación de mensajes de confirmación. Esto utiliza la autenticación de flujo de dispositivo OAuth para una experiencia de inicio de sesión perfecta.

## ¿Qué es Qwen.ai?

Qwen.ai es la plataforma de inteligencia artificial de Alibaba Cloud que brinda acceso a la familia de modelos de lenguaje grandes Qwen. GAC admite la autenticación basada en OAuth, lo que le permite usar su cuenta de Qwen.ai sin necesidad de administrar claves API manualmente.

## Beneficios

- **Autenticación fácil**: Flujo de dispositivo OAuth: simplemente inicie sesión con su navegador
- **Sin gestión de claves API**: La autenticación se gestiona automáticamente
- **Acceso a modelos Qwen**: Utilice potentes modelos Qwen para la generación de mensajes de confirmación

## Configuración

GAC incluye autenticación OAuth integrada para Qwen.ai utilizando el flujo de dispositivo. El proceso de configuración mostrará un código y abrirá su navegador para la autenticación.

### Opción 1: Durante la configuración inicial (recomendado)

Al ejecutar `gac init`, simplemente seleccione "Qwen.ai (OAuth)" como su proveedor:

```bash
gac init
```

El asistente:

1. Le pedirá que seleccione "Qwen.ai (OAuth)" de la lista de proveedores
2. Mostrará un código de dispositivo y abrirá su navegador
3. Se autenticará en Qwen.ai e ingresará el código
4. Guardará su token de acceso de forma segura
5. Establecerá el modelo predeterminado

### Opción 2: Cambiar a Qwen.ai más tarde

Si ya tiene GAC configurado con otro proveedor y desea cambiar a Qwen.ai:

```bash
gac model
```

Luego:

1. Seleccione "Qwen.ai (OAuth)" de la lista de proveedores
2. Siga el flujo de autenticación de código de dispositivo
3. Token guardado de forma segura en `~/.gac/oauth/qwen.json`
4. Modelo configurado automáticamente

### Opción 3: Inicio de sesión directo

También puede autenticarse directamente usando:

```bash
gac auth qwen login
```

Esto:

1. Mostrará un código de dispositivo
2. Abrirá su navegador en la página de autenticación de Qwen.ai
3. Después de autenticarse, el token se guarda automáticamente

### Usar GAC normalmente

Una vez autenticado, use GAC como de costumbre:

```bash
# Prepare sus cambios
git add .

# Genere y confirme con Qwen.ai
gac

# O anule el modelo para una sola confirmación
gac -m qwen:qwen3-coder-plus
```

## Modelos disponibles

La integración de Qwen.ai OAuth utiliza:

- `qwen3-coder-plus`: optimizado para tareas de codificación (predeterminado)

Este es el modelo disponible a través del punto final OAuth de portal.qwen.ai. Para otros modelos Qwen, considere usar el proveedor OpenRouter que ofrece opciones de modelos Qwen adicionales.

## Comandos de autenticación

GAC proporciona varios comandos para administrar la autenticación de Qwen.ai:

```bash
# Iniciar sesión en Qwen.ai
gac auth qwen login

# Verificar el estado de autenticación
gac auth qwen status

# Cerrar sesión y eliminar el token almacenado
gac auth qwen logout

# Verificar el estado de todos los proveedores de OAuth
gac auth
```

### Opciones de inicio de sesión

```bash
# Inicio de sesión estándar (abre el navegador automáticamente)
gac auth qwen login

# Iniciar sesión sin abrir el navegador (muestra la URL para visitar manualmente)
gac auth qwen login --no-browser

# Modo silencioso (salida mínima)
gac auth qwen login --quiet
```

## Solución de problemas

### Token caducado

Si ve errores de autenticación, es posible que su token haya caducado. Vuelva a autenticarse ejecutando:

```bash
gac auth qwen login
```

Se iniciará el flujo de código de dispositivo y su navegador se abrirá para la reautenticación.

### Verificar el estado de autenticación

Para verificar si está autenticado actualmente:

```bash
gac auth qwen status
```

O verifique todos los proveedores a la vez:

```bash
gac auth
```

### Cerrar sesión

Para eliminar su token almacenado:

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (No se encontró la autenticación de Qwen)

Esto significa que GAC no puede encontrar su token de acceso. Autentíquese ejecutando:

```bash
gac auth qwen login
```

O ejecute `gac model` y seleccione "Qwen.ai (OAuth)" de la lista de proveedores.

### "Authentication failed" (Error de autenticación)

Si la autenticación OAuth falla:

1. Asegúrese de tener una cuenta de Qwen.ai
2. Verifique que su navegador se abra correctamente
3. Verifique que ingresó el código de dispositivo correctamente
4. Pruebe con un navegador diferente si los problemas persisten
5. Verifique la conectividad de red a `qwen.ai`

### El código de dispositivo no funciona

Si la autenticación de código de dispositivo no funciona:

1. Asegúrese de que el código no haya caducado (los códigos son válidos por un tiempo limitado)
2. Intente ejecutar `gac auth qwen login` nuevamente para obtener un código nuevo
3. Use la bandera `--no-browser` y visite manualmente la URL si falla la apertura del navegador

## Notas de seguridad

- **Nunca confirme su token de acceso** en el control de versiones
- GAC almacena automáticamente los tokens en `~/.gac/oauth/qwen.json` (fuera del directorio de su proyecto)
- Los archivos de token tienen permisos restringidos (legibles solo por el propietario)
- Los tokens pueden caducar y requerirán reautenticación
- El flujo de dispositivo OAuth está diseñado para una autenticación segura en sistemas sin cabeza

## Ver también

- [Documentación principal](USAGE.md)
- [Configuración de Claude Code](CLAUDE_CODE.md)
- [Guía de solución de problemas](TROUBLESHOOTING.md)
- [Documentación de Qwen.ai](https://qwen.ai)
