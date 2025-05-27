"""Tests for ai module."""

from unittest.mock import patch

import pytest
import tiktoken

from gac.ai import extract_text_content, get_encoding
from gac.errors import AIError


class TestAiUtils:
    """Tests for the AI utilities."""

    def test_extract_text_content(self):
        """Test extracting text content from various input formats."""
        # Test string input
        assert extract_text_content("test") == "test"

        # Test list of messages
        messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "World"}]
        assert extract_text_content(messages) == "Hello\nWorld"

        # Test dict with content
        message = {"role": "user", "content": "Test"}
        assert extract_text_content(message) == "Test"

        # Test empty input
        assert extract_text_content({}) == ""

    def test_get_encoding_known_model(self):
        """Test getting encoding for known models without mocking."""
        # Test with a well-known OpenAI model that should map to cl100k_base
        encoding = get_encoding("openai:gpt-4")
        assert isinstance(encoding, tiktoken.Encoding)
        assert encoding.name == "cl100k_base"

        # Verify encoding behavior
        tokens = encoding.encode("Hello world")
        assert len(tokens) > 0
        assert isinstance(tokens[0], int)

        # Decode should round-trip correctly
        decoded = encoding.decode(tokens)
        assert decoded == "Hello world"
