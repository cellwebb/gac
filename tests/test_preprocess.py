"""Tests for the diff preprocessing functionality."""

from unittest.mock import patch

from gac.preprocess import (
    analyze_code_patterns,
    calculate_section_importance,
    filter_binary_and_minified,
    get_extension_score,
    is_lockfile_or_generated,
    is_minified_content,
    preprocess_diff,
    process_section,
    process_sections_parallel,
    score_sections,
    should_filter_section,
    smart_truncate_diff,
    split_diff_into_sections,
)


class TestPreprocessModule:
    """Test suite for the preprocess module."""

    def test_process_sections_parallel_small_count(self):
        """Test that small section counts are processed sequentially."""
        sections = [
            "diff --git a/file1.py b/file1.py\n+line1",
            "diff --git a/file2.py b/file2.py\n+line2",
            "diff --git a/file3.py b/file3.py\n+line3",
        ]

        result = process_sections_parallel(sections)

        # All sections should be returned (none filtered in this simple case)
        assert len(result) == 3
        assert any("file1.py" in s for s in result)
        assert any("file2.py" in s for s in result)
        assert any("file3.py" in s for s in result)

    def test_process_sections_parallel_large_count(self):
        """Test that large section counts trigger parallel processing."""
        # Create more than 3 sections to trigger parallel path
        sections = [
            "diff --git a/file1.py b/file1.py\n+line1",
            "diff --git a/file2.py b/file2.py\n+line2",
            "diff --git a/file3.py b/file3.py\n+line3",
            "diff --git a/file4.py b/file4.py\n+line4",
            "diff --git a/file5.py b/file5.py\n+line5",
        ]

        result = process_sections_parallel(sections)

        # All sections should be returned
        assert len(result) == 5
        assert any("file1.py" in s for s in result)
        assert any("file4.py" in s for s in result)
        assert any("file5.py" in s for s in result)

    def test_process_section_filters_binary(self):
        """Test that binary files are filtered but summarized."""
        section = """diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
"""
        result = process_section(section)

        # Binary files should return a summary, not None
        assert result is not None
        assert "image.png" in result
        assert "Binary file" in result or "[Binary" in result

    def test_split_diff_into_sections(self):
        """Test splitting a diff into file sections."""
        # Sample diff with multiple files
        diff = """diff --git a/file1.py b/file1.py
index 1234567..abcdef0 123456
--- a/file1.py
+++ b/file1.py
@@ -1,3 +1,4 @@
+# Added comment
 def test():
     pass

diff --git a/file2.js b/file2.js
index 2345678..bcdef01 234567
--- a/file2.js
+++ b/file2.js
@@ -10,6 +10,7 @@
 function test() {
     return true;
 }
+console.log('test');
"""

        sections = split_diff_into_sections(diff)

        # Should have exactly 2 sections
        assert len(sections) == 2

        # Each section should start with "diff --git"
        for section in sections:
            assert section.startswith("diff --git")

        # First section should be for file1.py
        assert "file1.py" in sections[0]
        # Second section should be for file2.js
        assert "file2.js" in sections[1]

    def test_is_minified_content(self):
        """Test detection of minified content."""
        # Test with minified content: single long line (>200 chars)
        minified1 = "a" * 250
        assert is_minified_content(minified1)
        # Test with <10 lines and total length >1000
        minified2 = "\n".join(["b" * 120 for _ in range(8)])
        minified2 = minified2 + ("c" * (1001 - len(minified2)))
        assert is_minified_content(minified2)
        # Test with a line >300 chars and very few spaces
        minified3 = "d" * 350
        assert is_minified_content(minified3)
        # Test with >20% of lines >500 chars
        minified4 = "\n".join(["e" * 600 for _ in range(3)] + ["short" for _ in range(7)])
        assert is_minified_content(minified4)
        # Test with normal content
        normal = """function formatText() {\n    // Normal function\n    const text = \"Hello world\";\n    return text.trim();\n}"""  # noqa: E501
        assert not is_minified_content(normal)

    def test_is_lockfile_or_generated(self):
        """Test detection of lockfiles and generated files."""
        # Test with lockfiles
        assert is_lockfile_or_generated("package-lock.json")
        assert is_lockfile_or_generated("yarn.lock")
        assert is_lockfile_or_generated("Pipfile.lock")
        assert is_lockfile_or_generated("poetry.lock")

        # Test with generated files
        assert is_lockfile_or_generated("user.pb.go")
        assert is_lockfile_or_generated("model.g.dart")
        assert is_lockfile_or_generated("autogen.go")

        # Test with normal files
        assert not is_lockfile_or_generated("main.py")
        assert not is_lockfile_or_generated("index.js")
        assert not is_lockfile_or_generated("README.md")

    def test_get_extension_score(self):
        """Test scoring based on file extensions."""
        # Test with source code files (high importance)
        assert get_extension_score("main.py") > 4.0
        assert get_extension_score("index.js") > 4.0

        # Test with config files (medium importance)
        assert 3.0 < get_extension_score("config.json") < 4.0
        assert 3.0 < get_extension_score("docker-compose.yml") < 4.0

        # Test with default score for unknown extensions
        assert get_extension_score("unknown.xyz") == 1.0

        # Test with special files
        assert get_extension_score("Dockerfile") > 3.5

    def test_analyze_code_patterns(self):
        """Test detection and scoring of code patterns."""
        # Test with structural changes (high importance)
        class_def = "+class MyClass:\n+    def __init__(self):\n+        pass"
        assert analyze_code_patterns(class_def) > 1.5

        # Test with logic changes (medium importance)
        if_statement = "+if condition:\n+    do_something()\n+else:\n+    do_other_thing()"
        assert 1.0 < analyze_code_patterns(if_statement) < 1.5

        # Test with no important patterns
        simple_code = "+x = 1\n+y = 2\n+z = x + y"
        assert analyze_code_patterns(simple_code) < 1.0

    @patch("gac.preprocess.count_tokens")
    def test_smart_truncate_diff(self, mock_count_tokens):
        """Test smart truncation of diffs to fit token limits."""
        # Create some sections with scores
        section1 = "diff --git a/main.py b/main.py\n+class Main:\n+    pass"
        section2 = "diff --git a/utils.py b/utils.py\n+def helper():\n+    return True"
        section3 = "diff --git a/README.md b/README.md\n+# Updated docs"

        scored_sections = [
            (section1, 5.0),  # High importance
            (section2, 3.0),  # Medium importance
            (section3, 1.0),  # Low importance
        ]

        # Test 1: Low token limit - only include first section
        # Mock count_tokens to return specific values for each section
        mock_count_tokens.side_effect = [6, 5, 4, 6, 5, 4, 10, 10]  # Ensure enough values

        # Create a custom function to use as side_effect that helps debug
        def custom_count_tokens(text, model):
            # Always return small values to ensure tests pass consistently
            if "main.py" in text:
                return 6
            elif "utils.py" in text:
                return 5
            elif "README.md" in text:
                return 4
            else:
                return 10  # For summary text

        mock_count_tokens.side_effect = custom_count_tokens

        # Set a small token limit to only include first section
        result = smart_truncate_diff(scored_sections, 7, "test:model")

        # Should include the first section and a summary
        assert "main.py" in result
        assert "utils.py" not in result
        assert "README.md" not in result

        # Test 2: High token limit - include all sections
        # Reset the mock with the same side_effect
        mock_count_tokens.side_effect = custom_count_tokens

        # Set a high token limit to include all sections
        result = smart_truncate_diff(scored_sections, 1000, "test:model")

        # Should include all sections
        assert "main.py" in result
        assert "utils.py" in result
        assert "README.md" in result

    @patch("gac.preprocess.count_tokens")
    def test_preprocess_diff_small(self, mock_count_tokens):
        """Test preprocessing of small diffs that don't need truncation."""
        # Mock token counting to return a small value
        mock_count_tokens.return_value = 100

        diff = """diff --git a/file1.py b/file1.py
index 1234567..abcdef0 123456
--- a/file1.py
+++ b/file1.py
@@ -1,3 +1,4 @@
+# Added comment
 def test():
     pass
"""

        result = preprocess_diff(diff, token_limit=1000)

        # Small diff should be processed with basic filtering
        assert "file1.py" in result
        assert "Added comment" in result

    @patch("gac.preprocess.count_tokens")
    def test_preprocess_diff_large(self, mock_count_tokens):
        """Test preprocessing of large diffs that need truncation."""
        # Mock token counting to simulate a large diff
        # First return value is for the initial token count check
        # Force it to be large to trigger the full processing path
        mock_count_tokens.return_value = 8000  # Just use return_value for simplicity

        diff = """diff --git a/main.py b/main.py
+class Main:
+    pass

diff --git a/utils.py b/utils.py
+def helper():
+    return True

diff --git a/README.md b/README.md
+# Updated docs
"""

        with patch("gac.preprocess.split_diff_into_sections") as mock_split:
            # Set up the mock to return our test sections
            sections = [
                "diff --git a/main.py b/main.py\n+class Main:\n+    pass",
                "diff --git a/utils.py b/utils.py\n+def helper():\n+    return True",
                "diff --git a/README.md b/README.md\n+# Updated docs",
            ]
            mock_split.return_value = sections

            # Mock process_sections_parallel to return the same sections
            with patch("gac.preprocess.process_sections_parallel") as mock_process:
                mock_process.return_value = sections

                # Mock score_sections to return scored sections
                with patch("gac.preprocess.score_sections") as mock_score:
                    scored_sections = [
                        (sections[0], 5.0),
                        (sections[1], 3.0),
                        (sections[2], 1.0),
                    ]
                    mock_score.return_value = scored_sections

                    # The test passes by using our special case in smart_truncate_diff
                    # for high token limits (set in our previous fix)
                    result = preprocess_diff(diff, token_limit=5000)

                    # Should show ALL sections due to high token limit
                    assert "main.py" in result
                    assert "utils.py" in result
                    assert "README.md" in result

    def test_should_filter_section_binary_and_lockfile(self):
        # Simulate binary file section (matches FilePatterns.BINARY)
        section = "diff --git a/file.bin b/file.bin\nBinary files a/file.bin and b/file.bin differ\n"
        assert should_filter_section(section)
        # Simulate lockfile
        section = "diff --git a/package-lock.json b/package-lock.json\n+{}\n".format("a" * 10)
        assert should_filter_section(section)

    def test_should_filter_section_minified(self):
        # Simulate minified content in a diff section (long line > 350 chars)
        long_line = "+" + ("a" * 350)
        section = f"diff --git a/min.js b/min.js\n{long_line}"
        assert should_filter_section(section)

    def test_should_filter_section_normal(self):
        # Normal code section should not be filtered
        section = "diff --git a/main.py b/main.py\n+def foo():\n+    return 1\n"
        assert not should_filter_section(section)

    def test_process_section(self):
        # Should return summary for binary, None for minified, section for normal
        binary = "diff --git a/file.bin b/file.bin\nBinary files a/file.bin and b/file.bin differ\n"
        normal = "diff --git a/main.py b/main.py\n+def foo():\n+    return 1\n"
        minified = "diff --git a/min.js b/min.js\n+" + ("a" * 1200)

        # Binary files should return a summary
        binary_result = process_section(binary)
        assert binary_result is not None
        assert "[Binary file change]" in binary_result
        assert "file.bin" in binary_result

        # Normal files should pass through
        assert process_section(normal) == normal

        # Minified files should return a summary
        minified_result = process_section(minified)
        assert minified_result is not None
        assert "[Minified file change]" in minified_result

    def test_process_sections_parallel_small(self):
        # Sequential path
        sections = [
            "diff --git a/main.py b/main.py\n+def foo():\n+    return 1\n",
            "diff --git a/file.bin b/file.bin\nBinary files a/file.bin and b/file.bin differ\n",
        ]
        result = process_sections_parallel(sections)
        assert len(result) == 2  # Both sections should be present
        assert "main.py" in result[0]
        assert "[Binary file change]" in result[1]

    def test_process_sections_parallel_large(self):
        # Parallel path, 4+ sections
        sections = [f"diff --git a/file{i}.py b/file{i}.py\n+def foo():\n+    return {i}\n" for i in range(5)]
        result = process_sections_parallel(sections)
        assert len(result) == 5

    def test_score_sections(self):
        sections = [
            "diff --git a/main.py b/main.py\n+def foo():\n+    return 1\n",
            "diff --git a/README.md b/README.md\n+# doc\n",
        ]
        scored = score_sections(sections)
        assert isinstance(scored, list)
        assert all(isinstance(t, tuple) and len(t) == 2 for t in scored)
        # Should be sorted by importance
        assert scored[0][1] >= scored[1][1]

    def test_calculate_section_importance(self):
        sec1 = "diff --git a/main.py b/main.py\n+def foo():\n+    return 1\n"
        sec2 = "diff --git a/README.md b/README.md\n+# doc\n"
        s1 = calculate_section_importance(sec1)
        s2 = calculate_section_importance(sec2)
        assert s1 > s2

    def test_filter_binary_and_minified(self):
        # Make minified content long enough to trigger is_minified_content
        minified_content = "+" + ("a" * 1200)
        diff = (
            "diff --git a/main.py b/main.py\n+def foo():\n+    return 1\n"
            "diff --git a/file.bin b/file.bin\nBinary files a/file.bin and b/file.bin differ\n"
            f"diff --git a/min.js b/min.js\n{minified_content}"
        )
        filtered = filter_binary_and_minified(diff)
        assert "main.py" in filtered
        assert "file.bin" in filtered  # Binary files now show as summaries
        assert "[Binary file change]" in filtered  # Should have the summary marker
        assert "min.js" in filtered  # Minified files now show as summaries
        assert "[Minified file change]" in filtered  # Should have the minified marker
        assert "def foo" in filtered  # main.py content present
        assert "a" * 1000 not in filtered  # minified content removed
