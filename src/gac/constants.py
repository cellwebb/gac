"""Constants for the Git Auto Commit (gac) project."""

import os
from enum import Enum


class FileStatus(Enum):
    """File status for Git operations."""

    MODIFIED = "M"
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNTRACKED = "?"


class EnvDefaults:
    """Default values for environment variables."""

    MAX_RETRIES: int = 3
    TEMPERATURE: float = 1
    MAX_OUTPUT_TOKENS: int = 4096  # includes reasoning tokens
    WARNING_LIMIT_TOKENS: int = 32768
    ALWAYS_INCLUDE_SCOPE: bool = False
    SKIP_SECRET_SCAN: bool = False
    VERBOSE: bool = False
    HOOK_TIMEOUT: int = 120  # Timeout for pre-commit and lefthook hooks in seconds


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


class FilePatterns:
    """Patterns for identifying special file types."""

    # Regex patterns to detect binary file changes in git diffs (e.g., images or other non-text files)
    BINARY: list[str] = [
        r"Binary files .* differ",
        r"GIT binary patch",
    ]

    # Regex patterns to detect minified files in git diffs (e.g., JavaScript or CSS files)
    MINIFIED_EXTENSIONS: list[str] = [
        ".min.js",
        ".min.css",
        ".bundle.js",
        ".bundle.css",
        ".compressed.js",
        ".compressed.css",
        ".opt.js",
        ".opt.css",
    ]

    # Regex patterns to detect build directories in git diffs (e.g., dist, build, vendor, etc.)
    BUILD_DIRECTORIES: list[str] = [
        "/dist/",
        "/build/",
        "/vendor/",
        "/node_modules/",
        "/assets/vendor/",
        "/public/build/",
        "/static/dist/",
    ]


class FileTypeImportance:
    """Importance multipliers for different file types."""

    EXTENSIONS: dict[str, float] = {
        # Programming languages
        ".py": 5.0,  # Python
        ".js": 4.5,  # JavaScript
        ".ts": 4.5,  # TypeScript
        ".jsx": 4.8,  # React JS
        ".tsx": 4.8,  # React TS
        ".go": 4.5,  # Go
        ".rs": 4.5,  # Rust
        ".java": 4.2,  # Java
        ".c": 4.2,  # C
        ".h": 4.2,  # C/C++ header
        ".cpp": 4.2,  # C++
        ".rb": 4.2,  # Ruby
        ".php": 4.0,  # PHP
        ".scala": 4.0,  # Scala
        ".swift": 4.0,  # Swift
        ".kt": 4.0,  # Kotlin
        # Configuration
        ".json": 3.5,  # JSON config
        ".yaml": 3.8,  # YAML config
        ".yml": 3.8,  # YAML config
        ".toml": 3.8,  # TOML config
        ".ini": 3.5,  # INI config
        ".env": 3.5,  # Environment variables
        # Documentation
        ".md": 2.5,  # Markdown (reduced to prioritize code changes)
        ".rst": 2.5,  # reStructuredText (reduced to prioritize code changes)
        # Web
        ".html": 3.5,  # HTML
        ".css": 3.5,  # CSS
        ".scss": 3.5,  # SCSS
        ".svg": 2.5,  # SVG graphics
        # Build & CI
        "Dockerfile": 4.0,  # Docker
        ".github/workflows": 4.0,  # GitHub Actions
        "CMakeLists.txt": 3.8,  # CMake
        "Makefile": 3.8,  # Make
        "package.json": 4.2,  # NPM package
        "pyproject.toml": 4.2,  # Python project
        "requirements.txt": 4.0,  # Python requirements
    }


class CodePatternImportance:
    """Importance multipliers for different code patterns."""

    # Regex patterns to detect code structure changes in git diffs (e.g., class, function, import)
    # Note: The patterns are prefixed with "+" to match only added and modified lines
    PATTERNS: dict[str, float] = {
        # Structure changes
        r"\+\s*(class|interface|enum)\s+\w+": 1.8,  # Class/interface/enum definitions
        r"\+\s*(def|function|func)\s+\w+\s*\(": 1.5,  # Function definitions
        r"\+\s*(import|from .* import)": 1.3,  # Imports
        r"\+\s*(public|private|protected)\s+\w+": 1.2,  # Access modifiers
        # Configuration changes
        r"\+\s*\"(dependencies|devDependencies)\"": 1.4,  # Package dependencies
        r"\+\s*version[\"\s:=]+[0-9.]+": 1.3,  # Version changes
        # Logic changes
        r"\+\s*(if|else|elif|switch|case|for|while)[\s(]": 1.2,  # Control structures
        r"\+\s*(try|catch|except|finally)[\s:]": 1.2,  # Exception handling
        r"\+\s*return\s+": 1.1,  # Return statements
        r"\+\s*await\s+": 1.1,  # Async/await
        # Comments & docs
        r"\+\s*(//|#|/\*|\*\*)\s*TODO": 1.2,  # TODOs
        r"\+\s*(//|#|/\*|\*\*)\s*FIX": 1.3,  # FIXes
        r"\+\s*(\"\"\"|\'\'\')": 1.1,  # Docstrings
        # Test code
        r"\+\s*(test|describe|it|should)\s*\(": 1.1,  # Test definitions
        r"\+\s*(assert|expect)": 1.0,  # Assertions
    }


class Languages:
    """Language code mappings and utilities."""

    # Language code to full name mapping
    # Supports ISO 639-1 codes and common variants
    CODE_MAP: dict[str, str] = {
        # English
        "en": "English",
        # Chinese
        "zh": "Simplified Chinese",
        "zh-cn": "Simplified Chinese",
        "zh-hans": "Simplified Chinese",
        "zh-tw": "Traditional Chinese",
        "zh-hant": "Traditional Chinese",
        # Japanese
        "ja": "Japanese",
        # Korean
        "ko": "Korean",
        # Spanish
        "es": "Spanish",
        # Portuguese
        "pt": "Portuguese",
        # French
        "fr": "French",
        # German
        "de": "German",
        # Russian
        "ru": "Russian",
        # Hindi
        "hi": "Hindi",
        # Italian
        "it": "Italian",
        # Polish
        "pl": "Polish",
        # Turkish
        "tr": "Turkish",
        # Dutch
        "nl": "Dutch",
        # Vietnamese
        "vi": "Vietnamese",
        # Thai
        "th": "Thai",
        # Indonesian
        "id": "Indonesian",
        # Swedish
        "sv": "Swedish",
        # Arabic
        "ar": "Arabic",
        # Hebrew
        "he": "Hebrew",
        # Greek
        "el": "Greek",
        # Danish
        "da": "Danish",
        # Norwegian
        "no": "Norwegian",
        "nb": "Norwegian",
        "nn": "Norwegian",
        # Finnish
        "fi": "Finnish",
    }

    # List of languages with display names and English names for CLI selection
    # Format: (display_name, english_name)
    LANGUAGES: list[tuple[str, str]] = [
        ("English", "English"),
        ("简体中文", "Simplified Chinese"),
        ("繁體中文", "Traditional Chinese"),
        ("日本語", "Japanese"),
        ("한국어", "Korean"),
        ("Español", "Spanish"),
        ("Português", "Portuguese"),
        ("Français", "French"),
        ("Deutsch", "German"),
        ("Русский", "Russian"),
        ("हिन्दी", "Hindi"),
        ("Italiano", "Italian"),
        ("Polski", "Polish"),
        ("Türkçe", "Turkish"),
        ("Nederlands", "Dutch"),
        ("Tiếng Việt", "Vietnamese"),
        ("ไทย", "Thai"),
        ("Bahasa Indonesia", "Indonesian"),
        ("Svenska", "Swedish"),
        ("العربية", "Arabic"),
        ("עברית", "Hebrew"),
        ("Ελληνικά", "Greek"),
        ("Dansk", "Danish"),
        ("Norsk", "Norwegian"),
        ("Suomi", "Finnish"),
        ("Custom", "Custom"),
    ]

    @staticmethod
    def resolve_code(language: str) -> str:
        """Resolve a language code to its full name.

        Args:
            language: Language name or code (e.g., 'Spanish', 'es', 'zh-CN')

        Returns:
            Full language name (e.g., 'Spanish', 'Simplified Chinese')

        If the input is already a full language name, it's returned as-is.
        If it's a recognized code, it's converted to the full name.
        Otherwise, the input is returned unchanged (for custom languages).
        """
        # Normalize the code to lowercase for lookup
        code_lower = language.lower().strip()

        # Check if it's a recognized code
        if code_lower in Languages.CODE_MAP:
            return Languages.CODE_MAP[code_lower]

        # Return as-is (could be a full name or custom language)
        return language


class CommitMessageConstants:
    """Constants for commit message generation and cleaning."""

    # Conventional commit type prefixes
    CONVENTIONAL_PREFIXES: list[str] = [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
    ]

    # XML tags that may leak from prompt templates into AI responses
    XML_TAGS_TO_REMOVE: list[str] = [
        "<git-status>",
        "</git-status>",
        "<git_status>",
        "</git_status>",
        "<git-diff>",
        "</git-diff>",
        "<git_diff>",
        "</git_diff>",
        "<repository_context>",
        "</repository_context>",
        "<instructions>",
        "</instructions>",
        "<format>",
        "</format>",
        "<conventions>",
        "</conventions>",
    ]

    # Indicators that mark the start of the actual commit message in AI responses
    COMMIT_INDICATORS: list[str] = [
        "# Your commit message:",
        "Your commit message:",
        "The commit message is:",
        "Here's the commit message:",
        "Commit message:",
        "Final commit message:",
        "# Commit Message",
    ]
