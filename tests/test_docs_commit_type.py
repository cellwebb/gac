"""Tests for ensuring documentation-only changes are properly labeled as 'docs:'."""

import unittest

from gac.prompt import build_prompt


class TestDocsCommitType(unittest.TestCase):
    """Test cases for documentation commit type detection."""

    def test_build_prompt_with_docs_only_changes(self):
        """Test that the prompt emphasizes documentation-only detection."""
        status = "On branch main\nChanges to be committed:\n  modified: README.md"
        diff = """diff --git a/README.md b/README.md
index abc123..def456 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,5 @@
 # My Project

-This is my project.
+This is my project with improved documentation.
+
+## New Section
+Added more details about installation."""

        system_prompt, user_prompt = build_prompt(status=status, processed_diff=diff, diff_stat="README.md | 4 +++-")
        prompt = system_prompt + "\n" + user_prompt

        # Check that the prompt includes the enhanced documentation detection instructions
        assert "Check file types FIRST" in prompt
        assert "ONLY to documentation files" in prompt
        assert "INCLUDING README updates" in prompt

    def test_docs_only_change_with_significant_content(self):
        """Test that significant README changes still get 'docs:' prefix."""
        status = """On branch main
Changes to be committed:
  modified: README.md
  modified: docs/api.md"""

        diff = """diff --git a/README.md b/README.md
index abc123..def456 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,50 @@
 # My Project

-This is my project.
+This is my project with completely rewritten documentation.
+
+## Installation
+Step-by-step installation guide...
+
+## Configuration
+Detailed configuration options...
+
+## API Reference
+Complete API documentation...
+
+[40+ more lines of documentation changes]

diff --git a/docs/api.md b/docs/api.md
index 111222..333444 100644
--- a/docs/api.md
+++ b/docs/api.md
@@ -1,10 +1,100 @@
-# API
+# API Reference
+
+[90+ lines of API documentation]"""

        system_prompt, user_prompt = build_prompt(
            status=status,
            processed_diff=diff,
            diff_stat="README.md | 47 +++++++++++++++++++++++++++++++++++++++++++++--\n docs/api.md | 90 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-",
        )
        prompt = system_prompt + "\n" + user_prompt

        # The prompt should guide the AI to use 'docs:' for documentation-only changes
        assert "ONLY to documentation files" in prompt
        assert "*.md" in prompt

    def test_mixed_changes_with_docs_and_code(self):
        """Test that mixed changes prioritize code change type."""
        status = """On branch main
Changes to be committed:
  modified: README.md
  modified: src/main.py"""

        diff = """diff --git a/README.md b/README.md
index abc123..def456 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # My Project

 This is my project.
+Added installation instructions.

diff --git a/src/main.py b/src/main.py
index 111222..333444 100644
--- a/src/main.py
+++ b/src/main.py
@@ -10,6 +10,10 @@ def main():
     print("Hello World")
+
+def new_feature():
+    \"\"\"New feature implementation.\"\"\"
+    return "feature"
"""

        system_prompt, user_prompt = build_prompt(
            status=status, processed_diff=diff, diff_stat="README.md | 1 +\n src/main.py | 4 ++++"
        )
        prompt = system_prompt + "\n" + user_prompt

        # Check that the prompt mentions handling mixed changes
        assert "If changes include both documentation and code" in prompt

    def test_prompt_emphasizes_docs_detection(self):
        """Test that the prompt properly emphasizes documentation-only detection."""
        # Create a simple documentation-only diff
        diff = """diff --git a/README.md b/README.md
index abc123..def456 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,10 @@
 # Project Title

-Short description
+Enhanced description with much more detail.
+
+## Installation
+Step-by-step installation guide.
+
+## Usage
+Comprehensive usage examples.
+
+## Contributing
+Guidelines for contributors."""

        status = "On branch main\nChanges to be committed:\n  modified: README.md"
        diff_stat = " README.md | 9 ++++++++-"

        # Use the diff directly without preprocessing (to avoid token counting issues in tests)
        processed_diff = diff

        # Build the prompt
        system_prompt, user_prompt = build_prompt(status=status, processed_diff=processed_diff, diff_stat=diff_stat)
        prompt = system_prompt + "\n" + user_prompt

        # Verify the prompt contains the enhanced instructions
        assert "Check file types FIRST" in prompt
        assert "ONLY to documentation files" in prompt
        assert "*.md" in prompt
        assert "README.md" in processed_diff


if __name__ == "__main__":
    unittest.main()
