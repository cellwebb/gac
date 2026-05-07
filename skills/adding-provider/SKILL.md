---
name: adding-provider
description: Use when adding a new AI provider to the GAC project (e.g. a new OpenAI-compatible inference service, Anthropic-compatible endpoint, or OAuth-based provider). Lists every file that must be created or edited and the exact registration steps required for the provider to appear in the registry, the `gac init` flow, the README, and the test suite.
---

# Adding a Provider to GAC

## Overview

GAC supports ~30 providers via a registry pattern. Adding one means creating a provider class, registering it, listing it in the interactive setup CLI, advertising it in the README, and adding standardized tests. Skipping any step leaves the provider partially wired (e.g. selectable in `gac init` but not in the registry, or callable but not advertised).

**Core principle:** every provider lives in five places. Touch all five.

## When to Use

Use when:

- A user asks to "add X as a provider"
- You need to support a new OpenAI-compatible inference service (cheapest case — extend `OpenAICompatibleProvider`)
- You need to support an Anthropic-compatible or custom-protocol provider

Do NOT use for:

- Modifying behavior of an existing provider (just edit its file)
- Adding a new model to an existing provider (no code change needed; users set `GAC_MODEL`)

## The Five Touch Points

| #   | Path                                                                                       | Purpose                                                                                                         |
| --- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| 1   | `src/gac/providers/<key>.py`                                                               | Provider class (NEW file)                                                                                       |
| 2   | `src/gac/providers/__init__.py`                                                            | Import + `register_provider("<key>", Cls)`                                                                      |
| 3   | `src/gac/model_cli.py`                                                                     | Add to `providers` list in `_configure_model`; add alias mapping if display name → key derivation doesn't match |
| 4   | `README.md`                                                                                | Add to "Supported Providers" bullet list                                                                        |
| 5   | `tests/providers/test_<key>.py` + `tests/test_ai.py` + `tests/test_model_cli_providers.py` | Tests (NEW + edits)                                                                                             |

## Step-by-Step

### 1. Research the API

Before writing any code:

- Find base URL and auth scheme (Bearer token, OAuth, custom header)
- Confirm whether it's OpenAI-compatible (Bearer + `/v1/chat/completions`), Anthropic-compatible, or custom
- Get one known-good model ID for the default in `model_cli.py` and tests
- Get the env var convention used by other tools (e.g. `FOO_API_KEY`)

If OpenAI-compatible, you can almost always extend `OpenAICompatibleProvider`. Check `chutes.py`, `together.py`, `fireworks.py` for templates.

### 2. Choose the registry key

The registry key is short and lowercase: `crof`, `chutes`, `groq`. It becomes the prefix in `GAC_MODEL=<key>:<model>`.

The display name in `model_cli.py` is derived to a key via:

```python
provider.lower().replace(".", "").replace(" ", "-").replace("(", "").replace(")", "")
```

So `"Crof.ai"` → `"crofai"`. If that doesn't match your registry key, add an alias (see step 5).

### 3. Create the provider class

For OpenAI-compatible providers, mirror `chutes.py`:

```python
"""<Provider> API provider for gac."""

import os

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class <Name>Provider(OpenAICompatibleProvider):
    """<Name> OpenAI-compatible provider with custom base URL."""

    config = ProviderConfig(
        name="<DisplayName>",
        api_key_env="<KEY>_API_KEY",
        base_url="",  # Set in __init__
    )

    def __init__(self, config: ProviderConfig):
        base_url = os.getenv("<KEY>_BASE_URL", "https://example.com")
        config.base_url = f"{base_url.rstrip('/')}/v1"
        super().__init__(config)

    def _get_api_url(self, model: str | None = None) -> str:
        return f"{self.config.base_url}/chat/completions"
```

For Anthropic-compatible: mirror `custom_anthropic.py`. For OAuth: mirror `chatgpt_oauth.py` (much more involved — has its own token storage in `~/.gac/oauth/`).

### 4. Register in `src/gac/providers/__init__.py`

Two edits, both alphabetically ordered with neighbors:

```python
from .crof import CrofProvider          # add to imports

register_provider("crof", CrofProvider) # add to registrations
```

### 5. Wire into `gac init` (`src/gac/model_cli.py`)

Add a tuple `(display_name, default_model)` to the `providers` list inside `_configure_model`. Keep alphabetical.

If the derived key doesn't match the registry key, add a mapping:

```python
elif provider_key == "crofai":
    provider_key = "crof"
```

If the provider needs extra config (custom base URL, endpoint ID, OAuth flow), branch on `is_<name>` like Streamlake/Azure/Custom.

### 6. Update `README.md`

Add the display name (with `.ai`/`.io` suffix if applicable) to the "Supported Providers" bullet list. Keep alphabetical within its line.

### 7. Add tests

**Create `tests/providers/test_<key>.py`** — copy `tests/providers/test_chutes.py` and replace identifiers. The file MUST contain four classes:

- `Test<Name>Imports` — module import + registry membership
- `Test<Name>APIKeyValidation` — missing API key raises `AIError`
- `Test<Name>ProviderMocked(BaseProviderTest)` — inherits the 9 standard HTTP-mocked tests via fixtures
- `Test<Name>EdgeCases` — at minimum, null content returns error
- `Test<Name>Integration` — real API call gated by `@pytest.mark.integration` and env var

**Edit `tests/test_ai.py`** — add the registry key to `expected_providers` in `test_provider_registry_complete`.

**Edit `tests/test_model_cli_providers.py`** — add a `test_configure_model_<key>_success` mirroring `test_configure_model_chutes_success`.

### 8. Verify

```bash
uv run -- pytest tests/providers/test_<key>.py \
                 tests/test_model_cli_providers.py::test_configure_model_<key>_success \
                 tests/test_ai.py::TestProviderRegistry -x
```

All of these must pass before claiming done.

## Quick Reference Checklist

```
[ ] 1. Research API: base URL, auth, default model, env var name
[ ] 2. Pick registry key (short, lowercase)
[ ] 3. Create src/gac/providers/<key>.py
[ ] 4. Edit src/gac/providers/__init__.py: import + register_provider
[ ] 5. Edit src/gac/model_cli.py: add to providers list (+ alias if needed)
[ ] 6. Edit README.md: add to provider bullets
[ ] 7. Create tests/providers/test_<key>.py (copy chutes template)
[ ] 8. Edit tests/test_ai.py: expected_providers set
[ ] 9. Edit tests/test_model_cli_providers.py: add config test
[ ] 10. Run targeted pytest, confirm green
```

## Common Mistakes

| Mistake                                                        | Symptom                                                                                  | Fix                                                            |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Forgot `register_provider` call                                | `KeyError: '<key>'` from `PROVIDER_REGISTRY[<key>]`                                      | Add the registration in `__init__.py`                          |
| Display name → key mismatch, no alias                          | `gac init` selects provider but `GAC_MODEL` prefix is wrong (e.g. `crofai:` not `crof:`) | Add `elif provider_key == "..."` mapping in `_configure_model` |
| Missed `tests/test_ai.py` update                               | `test_provider_registry_complete` fails                                                  | Add key to `expected_providers` set                            |
| Used `pip install` instead of `uv pip install`                 | CLAUDE.md violation                                                                      | Always use `uv pip install`                                    |
| Tried to manually bump `__version__.py` or edit `CHANGELOG.md` | CLAUDE.md violation                                                                      | Don't — these are auto-managed                                 |
| Hardcoded base URL instead of env-overridable                  | Users on enterprise gateways can't redirect                                              | Read `<KEY>_BASE_URL` env var with fallback default            |

## Provider Type Cheat Sheet

| API Style                                           | Base Class                                           | Template File                                      |
| --------------------------------------------------- | ---------------------------------------------------- | -------------------------------------------------- |
| OpenAI-compatible (Bearer + `/v1/chat/completions`) | `OpenAICompatibleProvider`                           | `chutes.py`, `together.py`, `fireworks.py`         |
| OpenAI-compatible with custom auth header           | `OpenAICompatibleProvider` (override `_get_headers`) | `copilot.py`                                       |
| Anthropic-compatible                                | `BaseConfiguredProvider`                             | `anthropic.py`, `custom_anthropic.py`              |
| OAuth-based                                         | Custom                                               | `chatgpt_oauth.py`, `claude_code.py`, `copilot.py` |
| Local/no-auth                                       | `OpenAICompatibleProvider` (no API key)              | `ollama.py`, `lmstudio.py`                         |

## Why Each Touch Point Matters

- **Provider class**: actually implements the API call.
- **`__init__.py` registration**: makes it callable via `PROVIDER_REGISTRY[key]`. Without this, the class exists but is unreachable.
- **`model_cli.py`**: makes it discoverable via `gac init`. Without this, users must hand-edit `~/.gac.env`.
- **README**: marketing/discoverability. Without this, users don't know the provider exists.
- **Tests**: prevents regressions; the `BaseProviderTest` inheritance enforces standard behavior across all providers.
