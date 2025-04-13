"""Constants for the Git Auto Commit (GAC) project."""

from enum import Enum


class FileStatus(Enum):
    """File status for Git operations."""

    MODIFIED = "M"
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNTRACKED = "?"


# Default values for environment variables
DEFAULT_MAX_RETRIES = 3
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_OUTPUT_TOKENS = 256

# Logging Constants
DEFAULT_LOG_LEVEL = "WARNING"
LOGGING_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]

# Utility Constants
DEFAULT_ENCODING = "cl100k_base"

# File patterns to filter out
BINARY_FILE_PATTERNS = [r"Binary files .* differ", r"GIT binary patch"]

MINIFIED_FILE_EXTENSIONS = [
    ".min.js",
    ".min.css",
    ".bundle.js",
    ".bundle.css",
    ".compressed.js",
    ".compressed.css",
    ".opt.js",
    ".opt.css",
]

BUILD_DIRECTORIES = [
    "/dist/",
    "/build/",
    "/vendor/",
    "/node_modules/",
    "/assets/vendor/",
    "/public/build/",
    "/static/dist/",
]

# Important file extensions and patterns
SOURCE_CODE_EXTENSIONS = {
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
    ".md": 4.0,  # Markdown
    ".rst": 3.8,  # reStructuredText
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

# Important code patterns with their importance multipliers
CODE_PATTERNS = {
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

# Default token limit for diffs to keep them within model context
DEFAULT_TOKEN_LIMIT = 6000

# Max workers for parallel processing
MAX_WORKERS = 4
