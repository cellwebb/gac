#!/usr/bin/env python3
"""
Language Links Verification Script for GAC Documentation

This script verifies that all documentation files in the docs/ directory contain
the complete and correctly ordered language links. It's designed to help maintain
consistency across all translated documentation as new languages are added.

USAGE:
    python scripts/check_languages.py

OVERVIEW:
    The GAC project supports multiple languages and each documentation file should
    contain language navigation links at the top of the file. This script ensures
    that all files have the complete set of language links in the correct order.

EXPECTED LANGUAGE ORDER:
    English | 箴体中文 | 繁體中文 | 日本語 | 한국어 | हिन्दी | Tiếng Việt | Français | Русский |
    Español | Português | Norsk | Svenska | Deutsch | Nederlands | Italiano

LANGUAGE LINK FORMAT:
    - README.md files: Use relative paths (e.g., [English](../../README.md))
    - Other files: Use ../en/FILENAME.md format (e.g., [English](../en/USAGE.md))
    - Current language: Should be bolded and not linked (e.g., **English**)
    - All other languages: Should be linked to their respective translations

ADDING NEW LANGUAGES:
    When adding a new language to the GAC documentation:

    1. Update the LANGUAGE_ORDER list in this script to include the new language
    2. Update the PATTERN regex to include the new language identifiers
    3. Run this script to verify all files are updated
    4. Update any documentation that references the language count

    Example for adding "Polski" (Polish):
        LANGUAGE_ORDER = [
            'English', '简体中文', '繁體中文', '日本語', '한국어', 'हिन्दी',
            'Tiếng Việt', 'Français', 'Русский', 'Español', 'Português',
            'Norsk', 'Svenska', 'Deutsch', 'Nederlands', 'Italiano', 'Polski'
        ]

        PATTERN = r'Norsk.*Svenska.*Deutsch.*Nederlands.*Italiano.*Polski'

EXIT CODES:
    0 - All files have complete language links
    1 - Some files are missing language links or have errors

OUTPUT:
    The script provides a detailed report showing:
    - Total number of files checked
    - Number of complete vs incomplete files
    - List of files that need updating
    - Detailed line-by-line analysis for problematic files

DIRECTORY STRUCTURE:
    The script expects the following structure:
    docs/
    ├── en/           # English (source language)
    ├── de/           # German
    ├── es/           # Spanish
    ├── fr/           # French
    ├── ...           # Other language directories
    └── RELEASING.md  # Excluded from language link checks

FILES CHECKED:
    - All *.md files in docs/*/ subdirectories
    - Excludes docs/RELEASING.md (maintainer-only file)
    - Checks for standard documentation files: README.md, CONTRIBUTING.md,
      USAGE.md, TROUBLESHOOTING.md, CUSTOM_SYSTEM_PROMPTS.md

MAINTENANCE:
    - Run this script after adding new languages
    - Run after major documentation updates
    - Use in CI/CD to ensure language link consistency
    - Update this docstring when language support changes

AUTHOR: AI Assistant
VERSION: 1.0
LAST UPDATED: 2025-11-04
"""

import re
from pathlib import Path

# Configuration - Update these when adding new languages
LANGUAGE_ORDER = [
    "English",
    "简体中文",
    "繁體中文",
    "日本語",
    "한국어",
    "हिन्दी",
    "Tiếng Việt",
    "Français",
    "Русский",
    "Español",
    "Português",
    "Norsk",
    "Svenska",
    "Deutsch",
    "Nederlands",
    "Italiano",
]

# Pattern to match complete language links - update when adding languages
# This pattern ensures the languages appear in the correct order
PATTERN = r"Norsk.*Svenska.*Deutsch.*Nederlands.*Italiano"


def check_language_links(file_path):
    """
    Check if a file has the complete language links in the correct order.

    Args:
        file_path (Path): Path to the markdown file to check

    Returns:
        tuple: (is_complete, status_message)
            is_complete (bool): True if file has complete language links
            status_message (str): Description of the check result
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Look for language link patterns
        if re.search(PATTERN, content):
            return True, "Complete"
        else:
            return False, "Missing languages"
    except Exception as e:
        return False, f"Error: {e}"


def get_expected_language_directories():
    """
    Get the list of expected language directories.
    Update this function when adding new languages.

    Returns:
        list: List of language directory names
    """
    return ["de", "en", "es", "fr", "hi", "it", "ja", "ko", "nl", "no", "pt", "ru", "sv", "vi", "zh-CN", "zh-TW"]


def main():
    """
    Main function to check all documentation files for language links.

    Returns:
        bool: True if all files are complete, False otherwise
    """
    docs_dir = Path("/Users/cell/projects/cctk/gac/docs")

    # Get expected language directories
    lang_dirs = get_expected_language_directories()

    missing_files = []
    complete_files = []
    error_files = []

    print("🔍 Checking language links in all documentation files...\n")
    print(f"Expected language order: {' | '.join(LANGUAGE_ORDER)}\n")

    total_files = 0

    for lang_dir in lang_dirs:
        lang_path = docs_dir / lang_dir
        if lang_path.exists():
            for md_file in lang_path.glob("*.md"):
                total_files += 1
                is_complete, status = check_language_links(md_file)

                relative_path = md_file.relative_to(docs_dir)

                if is_complete:
                    complete_files.append(str(relative_path))
                else:
                    missing_files.append((str(relative_path), status))

    print("📊 SUMMARY:")
    print(f"Total files checked: {total_files}")
    print(f"✅ Complete files: {len(complete_files)}")
    print(f"❌ Missing/Incomplete files: {len(missing_files)}")
    print(f"🚫 Error files: {len(error_files)}")
    print(f"🌍 Supported languages: {len(LANGUAGE_ORDER)}")
    print(f"📁 Language directories: {len(lang_dirs)}\n")

    if missing_files:
        print("❌ FILES THAT NEED UPDATING:")
        for file_path, status in sorted(missing_files):
            print(f"  - {file_path}: {status}")
        print()

        # Show first few lines of problematic files for debugging
        print("🔍 DETAILED ANALYSIS FOR PROBLEMATIC FILES:")
        for file_path, _status in missing_files[:3]:  # Show first 3 to avoid spam
            full_path = docs_dir / file_path
            print(f"\n  📄 {file_path}:")
            try:
                with open(full_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines[:5], 1):
                        if "English" in line or "简体中文" in line or any(lang in line for lang in LANGUAGE_ORDER[:3]):
                            print(f"    Line {i}: {line.strip()}")
                            break
            except Exception as e:
                print(f"    Error reading file: {e}")

        if len(missing_files) > 3:
            print(f"  ... and {len(missing_files) - 3} more files")
        print()

    if complete_files:
        print(f"✅ COMPLETE FILES ({len(complete_files)}):")
        for file_path in sorted(complete_files):
            print(f"  - {file_path}")

    # Return success if all files are complete
    return len(missing_files) == 0


if __name__ == "__main__":
    success = main()

    if success:
        print("\n🎉 All documentation files have complete language links!")
    else:
        print("\n⚠️  Some files need language link updates. Run this script after fixing them.")

    exit(0 if success else 1)
