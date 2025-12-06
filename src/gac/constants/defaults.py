"""Default values for environment variables and provider configurations."""

import os


class EnvDefaults:
    """Default values for environment variables."""

    MAX_RETRIES: int = 3
    TEMPERATURE: float = 1
    MAX_OUTPUT_TOKENS: int = 4096  # includes reasoning tokens
    WARNING_LIMIT_TOKENS: int = 32768
    ALWAYS_INCLUDE_SCOPE: bool = False
    SKIP_SECRET_SCAN: bool = False
    VERBOSE: bool = False
    NO_TIKTOKEN: bool = False
    NO_VERIFY_SSL: bool = False  # Skip SSL certificate verification (for corporate proxies)
    HOOK_TIMEOUT: int = 120  # Timeout for pre-commit and lefthook hooks in seconds


class ProviderDefaults:
    """Default values for provider configurations."""

    HTTP_TIMEOUT: int = 120  # seconds - timeout for HTTP requests to LLM providers


class Logging:
    """Logging configuration constants."""

    DEFAULT_LEVEL: str = "WARNING"
    LEVELS: list[str] = ["DEBUG", "INFO", "WARNING", "ERROR"]


class Utility:
    """General utility constants."""

    DEFAULT_ENCODING: str = "cl100k_base"  # llm encoding
    DEFAULT_DIFF_TOKEN_LIMIT: int = 15000  # Maximum tokens for diff processing
    MAX_WORKERS: int = os.cpu_count() or 4  # Maximum number of parallel workers
    MAX_DISPLAYED_SECRET_LENGTH: int = 50  # Maximum length for displaying secrets
