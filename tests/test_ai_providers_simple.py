import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import gac.ai_utils as ai_providers  # noqa: E402
from gac.errors import AIError  # noqa: E402


def test_ai_providers_functions_exist():
    """Test that all expected functions exist in ai_utils module."""
    assert hasattr(ai_providers, "_classify_error")


def test_ai_error_class_exists():
    """Test that AIError class exists in errors module."""
    assert AIError is not None
