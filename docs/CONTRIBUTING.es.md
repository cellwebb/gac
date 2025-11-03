# Contribuir a gac

English | [简体中文](CONTRIBUTING.zh-CN.md) | [繁體中文](CONTRIBUTING.zh-TW.md) | [日本語](CONTRIBUTING.ja.md) | [Français](CONTRIBUTING.fr.md) | **Русский** | **Español** | Português | हिन्दी

¡Gracias por tu interés en contribuir a este proyecto! ¡Tu ayuda es muy apreciada. Por favor, sigue estas guías para
hacer que el proceso sea fluido para todos.

## Tabla de Contenidos

- [Contribuir a gac](#contribuir-a-gac)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
    - [Configuración Rápida](#configuración-rápida)
    - [Configuración Alternativa (si prefieres paso a paso)](#configuración-alternativa-si-prefieres-paso-a-paso)
    - [Comandos Disponibles](#comandos-disponibles)
  - [Actualización de Versión](#actualización-de-versión)
    - [Cómo actualizar la versión](#cómo-actualizar-la-versión)
    - [Proceso de Lanzamiento](#proceso-de-lanzamiento)
    - [Usando bump-my-version (opcional)](#usando-bump-my-version-opcional)
  - [Añadir un Nuevo Proveedor de IA](#añadir-un-nuevo-proveedor-de-ia)
    - [Lista de Verificación para Añadir un Nuevo Proveedor](#lista-de-verificación-para-añadir-un-nuevo-proveedor)
    - [Ejemplo de Implementación](#ejemplo-de-implementación)
    - [Puntos Clave](#puntos-clave)
  - [Estándares de Codificación](#estándares-de-codificación)
  - [Git Hooks (Lefthook)](#git-hooks-lefthook)
    - [Configuración](#configuración)
    - [Omitir Git Hooks](#omitir-git-hooks)
  - [Guías de Pruebas](#guías-de-pruebas)
    - [Ejecutar Pruebas](#ejecutar-pruebas)
      - [Pruebas de Integración de Proveedores](#pruebas-de-integración-de-proveedores)
  - [Código de Conducta](#código-de-conducta)
  - [Licencia](#licencia)
  - [Dónde Obtener Ayuda](#dónde-obtener-ayuda)

## Configuración del Entorno de Desarrollo

Este proyecto usa `uv` para la gestión de dependencias y proporciona un Makefile para tareas comunes de desarrollo:

### Configuración Rápida

```bash
# Un comando para configurar todo incluyendo los hooks de Lefthook
make dev
```

Este comando hará:

- Instalar dependencias de desarrollo
- Instalar hooks de git
- Ejecutar hooks de Lefthook en todos los archivos para corregir problemas existentes

### Configuración Alternativa (si prefieres paso a paso)

```bash
# Crear entorno virtual e instalar dependencias
make setup

# Instalar dependencias de desarrollo
make dev

# Instalar hooks de Lefthook
brew install lefthook  # o ver los documentos a continuación para alternativas
lefthook install
lefthook run pre-commit --all
```

### Comandos Disponibles

- `make setup` - Crear entorno virtual e instalar todas las dependencias
- `make dev` - **Configuración de desarrollo completa** - incluye hooks de Lefthook
- `make test` - Ejecutar pruebas estándar (excluye pruebas de integración)
- `make test-integration` - Ejecutar solo pruebas de integración (requiere claves de API)
- `make test-all` - Ejecutar todas las pruebas
- `make test-cov` - Ejecutar pruebas con reporte de cobertura
- `make lint` - Verificar calidad del código (ruff, prettier, markdownlint)
- `make format` - Corregir automáticamente problemas de formato de código

## Actualización de Versión

**Importante**: Los PRs deben incluir una actualización de versión en `src/gac/__version__.py` cuando contengan cambios que deban ser lanzados.

### Cómo actualizar la versión

1. Edita `src/gac/__version__.py` e incrementa el número de versión
2. Sigue [Versionamiento Semántico](https://semver.org/):
   - **Patch** (1.6.X): Corrección de errores, pequeñas mejoras
   - **Minor** (1.X.0): Nuevas características, cambios compatibles hacia atrás (ej. añadir un nuevo proveedor)
   - **Major** (X.0.0): Cambios rupturistas

### Proceso de Lanzamiento

Los lanzamientos son activados al empujar etiquetas de versión:

1. Fusiona PR(s) con actualizaciones de versión a main
2. Crea una etiqueta: `git tag v1.6.1`
3. Empuja la etiqueta: `git push origin v1.6.1`
4. GitHub Actions publica automáticamente en PyPI

Ejemplo:

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # Actualizado desde 1.6.0
```

### Usando bump-my-version (opcional)

Si tienes `bump-my-version` instalado, puedes usarlo localmente:

```bash
# Para corrección de errores:
bump-my-version bump patch

# Para nuevas características:
bump-my-version bump minor

# Para cambios rupturistas:
bump-my-version bump major
```

## Añadir un Nuevo Proveedor de IA

Al añadir un nuevo proveedor de IA, necesitas actualizar múltiples archivos en el código base. Sigue esta lista de verificación completa:

### Lista de Verificación para Añadir un Nuevo Proveedor

- [ ] **1. Crear Implementación del Proveedor** (`src/gac/providers/<provider_name>.py`)

  - Crea un nuevo archivo nombrado después del proveedor (ej. `minimax.py`)
  - Implementa `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str`
  - Usa el formato compatible con OpenAI si el proveedor lo soporta
  - Maneja la clave de API desde la variable de entorno `<PROVIDER>_API_KEY`
  - Incluye manejo de errores apropiado con tipos `AIError`:
    - `AIError.authentication_error()` para problemas de autenticación
    - `AIError.rate_limit_error()` para límites de velocidad (HTTP 429)
    - `AIError.timeout_error()` para tiempos de espera
    - `AIError.model_error()` para errores de modelo y contenido vacío/nulo
  - Establece URL del endpoint de API
  - Usa tiempo de espera de 120 segundos para solicitudes HTTP

- [ ] **2. Registrar Proveedor en el Paquete** (`src/gac/providers/__init__.py`)

  - Añade import: `from .<provider> import call_<provider>_api`
  - Añade a la lista `__all__`: `"call_<provider>_api"`

- [ ] **3. Registrar Proveedor en el Módulo de IA** (`src/gac/ai.py`)

  - Añade import en la sección `from gac.providers import (...)`
  - Añade al diccionario `provider_funcs`: `"provider-name": call_<provider>_api`

- [ ] **4. Añadir a la Lista de Proveedores Soportados** (`src/gac/ai_utils.py`)

  - Añade `"provider-name"` a la lista `supported_providers` en `generate_with_retries()`
  - Mantén la lista ordenada alfabéticamente

- [ ] **5. Añadir a la Configuración Interactiva** (`src/gac/init_cli.py`)

  - Añade tupla a la lista `providers`: `("Provider Name", "default-model-name")`
  - Mantén la lista ordenada alfabéticamente
  - Añade cualquier manejo especial si es necesario (como Ollama/LM Studio para proveedores locales)

- [ ] **6. Actualizar Configuración de Ejemplo** (`.gac.env.example`)

  - Añade configuración de modelo de ejemplo en el formato: `# GAC_MODEL=provider:model-name`
  - Añade entrada de clave de API: `# <PROVIDER>_API_KEY=your_key_here`
  - Mantén las entradas ordenadas alfabéticamente
  - Añade comentarios para claves opcionales si aplica

- [ ] **7. Actualizar Documentación** (`README.md` y `README.zh-CN.md`)

  - Añade nombre del proveedor a la sección "Proveedores Soportados" en ambos README, inglés y chino
  - Mantén la lista ordenada alfabéticamente dentro de sus puntos

- [ ] **8. Crear Pruebas Comprensivas** (`tests/providers/test_<provider>.py`)

  - Crea archivo de prueba siguiendo la convención de nomenclatura
  - Incluye estas clases de prueba:
    - `Test<Provider>Imports` - Prueba de importaciones de módulo y función
    - `Test<Provider>APIKeyValidation` - Prueba de error de clave de API faltante
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - Hereda de `BaseProviderTest` para 9 pruebas estándar
    - `Test<Provider>EdgeCases` - Prueba contenido nulo y otros casos extremos
    - `Test<Provider>Integration` - Pruebas reales de llamada API (marcadas con `@pytest.mark.integration`)
  - Implementa propiedades requeridas en la clase de prueba mock:
    - `provider_name` - Nombre del proveedor (minúsculas)
    - `provider_module` - Ruta completa del módulo
    - `api_function` - Referencia a la función API
    - `api_key_env_var` - Nombre de variable de entorno para clave API (o None para proveedores locales)
    - `model_name` - Nombre del modelo por defecto para pruebas
    - `success_response` - Respuesta exitosa de API mock
    - `empty_content_response` - Respuesta de contenido vacío mock

- [ ] **9. Actualizar Versión** (`src/gac/__version__.py`)
  - Incrementa la versión **minor** (ej. 1.10.2 → 1.11.0)
  - Añadir un proveedor es una nueva característica y requiere una actualización de versión minor

### Ejemplo de Implementación

Ver la implementación del proveedor MiniMax como referencia:

- Proveedor: `src/gac/providers/minimax.py`
- Pruebas: `tests/providers/test_minimax.py`

### Puntos Clave

1. **Manejo de Errores**: Siempre usa el tipo `AIError` apropiado para diferentes escenarios de error
2. **Contenido Nulo/Vacío**: Siempre verifica tanto `None` como contenido de cadena vacío en respuestas
3. **Pruebas**: La clase `BaseProviderTest` proporciona 9 pruebas estándar que cada proveedor debe heredar
4. **Orden Alfabético**: Mantén las listas de proveedores ordenadas alfabéticamente para mantenibilidad
5. **Nomenclatura de Clave API**: Usa el formato `<PROVIDER>_API_KEY` (todo mayúsculas, guiones bajos para espacios)
6. **Formato de Nombre de Proveedor**: Usa minúsculas con guiones para nombres de múltiples palabras (ej. "lm-studio")
7. **Actualización de Versión**: Añadir un proveedor requiere una actualización de versión **minor** (nueva característica)

## Estándares de Codificación

- Python 3.10+ objetivo (3.10, 3.11, 3.12, 3.13, 3.14)
- Usa type hints para todos los parámetros de función y valores de retorno
- Mantén el código limpio, compacto y legible
- Evita complejidad innecesaria
- Usa logging en lugar de sentencias print
- El formato es manejado por `ruff` (linting, formatting y ordenamiento de imports en una sola herramienta; longitud máxima de línea: 120)
- Escribe pruebas mínimas y efectivas con `pytest`

## Git Hooks (Lefthook)

Este proyecto usa [Lefthook](https://github.com/evilmartians/lefthook) para mantener las verificaciones de calidad del código rápidas y consistentes. Los hooks configurados replican nuestra configuración pre-commit anterior:

- `ruff` - Linting y formato de Python (reemplaza black, isort y flake8)
- `markdownlint-cli2` - Linting de Markdown
- `prettier` - Formato de archivos (markdown, yaml, json)
- `check-upstream` - Hook personalizado para verificar cambios upstream

### Configuración

**Enfoque recomendado:**

```bash
make dev
```

**Configuración manual (si prefieres paso a paso):**

1. Instala Lefthook (elije la opción que coincida con tu configuración):

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # o
   cargo install lefthook         # Rust toolchain
   # o
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. Instala los hooks de git:

   ```sh
   lefthook install
   ```

3. (Opcional) Ejecutar contra todos los archivos:

   ```sh
   lefthook run pre-commit --all
   ```

Los hooks ahora se ejecutarán automáticamente en cada commit. Si alguna verificación falla, necesitarás corregir los problemas antes de confirmar.

### Omitir Git Hooks

Si necesitas omitir las verificaciones de Lefthook temporalmente, usa el flag `--no-verify`:

```sh
git commit --no-verify -m "Tu mensaje de commit"
```

Nota: Esto solo debería usarse cuando sea absolutamente necesario, ya que evita importantes verificaciones de calidad de código.

## Guías de Pruebas

El proyecto usa pytest para pruebas. Al añadir nuevas características o corregir errores, por favor incluye pruebas que cubran tus
cambios.

Nota que el directorio `scripts/` contiene scripts de prueba para funcionalidad que no puede ser fácilmente probada con pytest.
Siéntete libre de añadir scripts aquí para probar escenarios complejos o pruebas de integración que serían difíciles de implementar
usando el framework estándar pytest.

### Ejecutar Pruebas

```sh
# Ejecutar pruebas estándar (excluye pruebas de integración con llamadas reales a API)
make test

# Ejecutar solo pruebas de integración de proveedores (requiere claves de API)
make test-integration

# Ejecutar todas las pruebas incluyendo pruebas de integración de proveedores
make test-all

# Ejecutar pruebas con cobertura
make test-cov

# Ejecutar archivo de prueba específico
uv run -- pytest tests/test_prompt.py

# Ejecutar prueba específica
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### Pruebas de Integración de Proveedores

Las pruebas de integración de proveedores hacen llamadas reales a API para verificar que las implementaciones de proveedores funcionan correctamente con APIs reales. Estas pruebas están marcadas con `@pytest.mark.integration` y se omiten por defecto para:

- Evitar consumir créditos de API durante el desarrollo regular
- Prevenir fallos de pruebas cuando las claves de API no están configuradas
- Mantener rápida la ejecución de pruebas para iteración rápida

Para ejecutar pruebas de integración de proveedores:

1. **Configura claves de API** para los proveedores que quieres probar:

   ```sh
   export ANTHROPIC_API_KEY="your-key"
   export CEREBRAS_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export GROQ_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export OPENROUTER_API_KEY="your-key"
   export STREAMLAKE_API_KEY="your-key"
   export ZAI_API_KEY="your-key"
   # LM Studio y Ollama requieren una instancia local ejecutándose
   # Las claves de API para LM Studio y Ollama son opcionales a menos que tu despliegue exija autenticación
   ```

2. **Ejecutar pruebas de proveedores**:

   ```sh
   make test-integration
   ```

Las pruebas omitirán proveedores donde las claves de API no están configuradas. Estas pruebas ayudan a detectar cambios en las API temprano y asegurar compatibilidad con las APIs de los proveedores.

## Código de Conducta

Sé respetuoso y constructivo. El acoso o comportamiento abusivo no será tolerado.

## Licencia

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la misma licencia que el proyecto.

---

## Dónde Obtener Ayuda

- Para solución de problemas, ver [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Para uso y opciones de CLI, ver [../USAGE.md](../USAGE.md)
- Para detalles de licencia, ver [../LICENSE](../LICENSE)

¡Gracias por ayudar a mejorar gac!
