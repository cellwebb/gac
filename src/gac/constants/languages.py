"""Language code mappings and utilities for internationalization."""


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
