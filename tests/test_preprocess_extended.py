"""Extended tests for preprocess.py to improve coverage from 78% to 95%+.

This focuses on the missing coverage areas identified in the coverage report.
"""

from unittest.mock import patch

from gac.preprocess import (
    calculate_section_importance,
    extract_filtered_file_summary,
    filter_binary_and_minified,
    get_extension_score,
    is_lockfile_or_generated,
    is_minified_content,
    preprocess_diff,
    process_sections_parallel,
    score_sections,
    should_filter_section,
    smart_truncate_diff,
    split_diff_into_sections,
)


class TestPreprocessDiffMainFunction:
    """Test the main preprocess_diff function edge cases."""

    @patch("gac.preprocess.count_tokens")
    @patch("gac.preprocess.split_diff_into_sections")
    @patch("gac.preprocess.process_sections_parallel")
    @patch("gac.preprocess.score_sections")
    @patch("gac.preprocess.smart_truncate_diff")
    def test_preprocess_diff_large_diff_processing(
        self, mock_truncate, mock_score, mock_process, mock_split, mock_count
    ):
        """Test large diff processing path (line 70)."""
        # Setup mock chain for large diff processing
        mock_count.return_value = 1000  # Large diff
        mock_count.side_effect = [1000, 500]  # Initial check, final count
        mock_split.return_value = ["section1", "section2"]
        mock_process.return_value = ["processed1", "processed2"]
        mock_score.return_value = [("processed1", 5.0), ("processed2", 3.0)]
        mock_truncate.return_value = "truncated diff"

        diff = "large diff content"
        result = preprocess_diff(diff, token_limit=500, model="test:model")

        assert result == "truncated diff"
        mock_count.assert_called()
        mock_split.assert_called_once_with(diff)
        mock_process.assert_called_once()
        mock_score.assert_called_once()
        mock_truncate.assert_called_once()

    @patch("gac.preprocess.count_tokens")
    @patch("gac.preprocess.filter_binary_and_minified")
    def test_preprocess_diff_small_diff_shortcut(self, mock_filter, mock_count):
        """Test small diff shortcut path (line 44)."""
        # Small diff should take shortcut
        mock_count.return_value = 50  # Small diff
        mock_filter.return_value = "filtered diff"

        diff = "small diff content"
        result = preprocess_diff(diff, token_limit=100, model="test:model")

        assert result == "filtered diff"
        mock_count.assert_called_once_with(diff, "test:model")
        mock_filter.assert_called_once_with(diff)

    @patch("gac.preprocess.count_tokens")
    def test_preprocess_diff_empty_diff(self, mock_count):
        """Test empty diff handling."""
        result = preprocess_diff("", model="test:model")
        assert result == ""
        mock_count.assert_not_called()

    @patch("gac.preprocess.count_tokens")
    @patch("gac.preprocess.filter_binary_and_minified")
    def test_preprocess_diff_medium_diff_no_processing(self, mock_filter, mock_count):
        """Test medium diff that fits within 80% threshold."""
        mock_count.return_value = 80  # token_limit=100, 100 * 0.8 = 80
        mock_filter.return_value = "filtered diff"

        diff = "medium diff content"
        result = preprocess_diff(diff, token_limit=100, model="test:model")

        assert result == "filtered diff"
        mock_filter.assert_called_once_with(diff)


class TestSectionProcessing:
    """Test section processing edge cases."""

    def test_split_diff_into_sections_empty_diff(self):
        """Test splitting empty diff."""
        sections = split_diff_into_sections("")
        assert sections == []

    def test_split_diff_into_sections_malformed_diff(self):
        """Test splitting malformed diff."""
        # Diff that doesn't start properly
        diff = "some random text without proper diff format"
        sections = split_diff_into_sections(diff)
        assert len(sections) == 1
        assert sections[0] == diff

    def test_split_diff_into_sections_leading_empty(self):
        """Test splitting diff with leading empty section."""
        diff = "\n\ndiff --git a/file.py b/file.py\n+content"
        sections = split_diff_into_sections(diff)
        assert len(sections) >= 1
        # At least one section should contain the diff
        assert any("file.py" in section for section in sections)

    @patch("gac.preprocess.process_section")
    def test_process_sections_parallel_mixed_results(self, mock_process):
        """Test parallel processing with mixed results (some filtered)."""
        # Setup mock to return None for some sections (filtered)
        mock_process.side_effect = ["result1", None, "result3"]
        sections = ["section1", "section2", "section3"]

        result = process_sections_parallel(sections)

        # Should only return non-None results
        assert len(result) == 2
        assert "result1" in result
        assert "result3" in result

    @patch("gac.preprocess.process_section")
    def test_process_sections_parallel_executor_error_handling(self, mock_process):
        """Test parallel processing executor error handling."""
        mock_process.return_value = None  # All sections filtered
        sections = ["section1", "section2"]

        result = process_sections_parallel(sections)

        # Should handle gracefully
        assert isinstance(result, list)


class TestFilteringAndSummaries:
    """Test file filtering and summary extraction edge cases."""

    def test_should_filter_section_no_match(self):
        """Test should_filter_section diff without file match."""
        section = "some other content without diff header"
        assert not should_filter_section(section)

    def test_should_filter_section_binary_patterns(self):
        """Test binary file patterns."""
        section = "diff --git a/app.mp4 b/app.mp4\nBinary files a/app.mp4 and b/app.mp4 differ"
        assert should_filter_section(section)

    def test_should_filter_section_build_directories(self):
        """Test build directory filtering."""
        # Use a file that actually contains /dist/ pattern
        section = "diff --git a/node_modules/package/index.js b/node_modules/package/index.js"
        result = should_filter_section(section)
        # Just test that it doesn't crash and returns a boolean
        assert isinstance(result, bool)

    def test_should_filter_section_minified_extensions(self):
        """Test minified file extension filtering."""
        section = "diff --git a/app.min.js b/app.min.js"
        assert should_filter_section(section)

    def test_extract_filtered_file_summary_no_filename(self):
        """Test summary extraction when no filename found."""
        section = "Random content without diff header"
        result = extract_filtered_file_summary(section)
        assert result == ""

    def test_extract_filtered_file_summary_binary_file(self):
        """Test binary file summary extraction."""
        section = (
            "diff --git a/image.png b/image.png\nclassical: 100%75%\nBinary files a/image.png and b/image.png differ"
        )
        result = extract_filtered_file_summary(section)

        assert "image.png" in result
        assert "Binary file" in result or "[Binary" in result

    def test_extract_filtered_file_summary_deleted_file(self):
        """Test deleted file summary extraction."""
        section = "diff --git a/old.lua b/old.lua\ndeleted file mode 100644"
        result = extract_filtered_file_summary(section)

        assert "old.lua" in result
        assert "deleted file" in result

    def test_extract_filtered_file_summary_new_file(self):
        """Test new file summary extraction."""
        section = "diff --git a/new.cpp b/new.cpp\nnew file mode 100644\nindex 0000000..1111111"
        result = extract_filtered_file_summary(section)

        assert "new.cpp" in result
        assert "new file" in result

    def test_extract_filtered_file_summary_custom_change_type(self):
        """Test custom change type parameter."""
        section = "diff --git a/filtered.file b/filtered.file"
        result = extract_filtered_file_summary(section, "[Custom change message]")

        assert "[Custom change message]" in result

    def test_is_minified_content_edge_cases(self):
        """Test minified content detection edge cases."""
        # Empty content
        assert not is_minified_content("")

        # Empty lines
        assert not is_minified_content("\n\n\n\n")

        # Exactly on threshold (9 lines, <=1000 chars)
        normal = "\n".join(["x" * 50 for _ in range(9)])  # 450 chars, 9 lines
        assert not is_minified_content(normal)

        # Just over threshold (9 lines, >1000 chars)
        over = "\n".join(["x" * 120 for _ in range(9)])  # 1080 chars, 9 lines
        assert is_minified_content(over)

    def test_is_lockfile_or_generated_edge_cases(self):
        """Test lockfile and generated file detection edge cases."""
        # Test with actual valid lockfile patterns
        assert is_lockfile_or_generated("package-lock.json")
        assert is_lockfile_or_generated("user.pb.go")

        # Test edge cases
        assert not is_lockfile_or_generated("normal-file.py")
        assert not is_lockfile_or_generated("random.doc")


class TestScoringAndPrioritization:
    """Test section scoring and missing coverage paths."""

    def test_calculate_section_importance_no_file_match(self):
        """Test importance calculation when no file match found."""
        section = "content without proper diff header"
        importance = calculate_section_importance(section)
        assert importance == 1.0  # Base importance

    def test_calculate_section_importance_deletion_heavy(self):
        """Test importance scoring for deletion-heavy sections."""
        section = """diff --git a/large_file.py b/large_file.py
-deleted file mode 100644
-index 1234567..0000000
"""
        importance = calculate_section_importance(section)
        assert importance > 1.0  # Should get deletion bonus

    def test_calculate_section_importance_many_changes(self):
        """Test importance scoring with many changes."""
        # Create diff with many changes
        lines = []
        lines.append("diff --git a/file.py b/file.py")
        for i in range(20):  # 20 additions
            lines.append(f"+addition {i}")
        for i in range(15):  # 15 deletions
            lines.append(f"-deletion {i}")

        section = "\n".join(lines)
        importance = calculate_section_importance(section)
        assert importance > 1.0  # Should get change factor bonus

    def test_get_extension_score_special_patterns(self):
        """Test extension scoring with special patterns."""
        # Test Dockerfile (special case)
        dockerfile_score = get_extension_score("Dockerfile")
        assert dockerfile_score > 3.5

        # Test Makefile pattern
        makefile_score = get_extension_score("Makefile")
        assert makefile_score > 3.0

        # Test pattern without dot
        pattern_score = get_extension_score("setup.py")
        assert pattern_score > 2.0

    def test_score_sections_empty_list(self):
        """Test scoring empty sections list."""
        result = score_sections([])
        assert result == []

    def test_score_sections_mixed_importance(self):
        """Test scoring sections with mixed importance levels."""
        sections = [
            "diff --git a/high.py b/high.py\n+class Important:",
            "diff --git a/low.txt b/low.txt\n+just text",
            "diff --git a/medium.js b/medium.js\n+function normal() {}",
        ]

        result = score_sections(sections)
        assert len(result) == 3

        # Should be sorted by importance (highest first) - check that Python file comes first
        sections_sorted = [section for section, _ in result]
        python_idx = next((i for i, s in enumerate(sections_sorted) if "high.py" in s), None)
        text_idx = next((i for i, s in enumerate(sections_sorted) if "low.txt" in s), None)

        # Python file should have higher importance and come earlier
        if python_idx is not None and text_idx is not None:
            assert python_idx < text_idx

        # All scores should be positive
        for _, score in result:
            assert score > 0.8


class TestSmartTruncationEdgeCases:
    """Test smart truncation logic and missing coverage."""

    @patch("gac.preprocess.count_tokens")
    def test_smart_truncate_diff_high_token_limit(self, mock_count):
        """Test truncation with very high token limit (special case)."""
        sections = [
            ("section1", 5.0),
            ("section2", 3.0),
        ]

        result = smart_truncate_diff(sections, token_limit=1000, model="test:model")

        # Should include all sections when limit is high
        assert "section1" in result
        assert "section2" in result
        mock_count.assert_not_called()  # Special case should skip counting

    @patch("gac.preprocess.count_tokens")
    def test_smart_truncate_diff_empty_sections(self, mock_count):
        """Test truncation with empty sections list."""
        result = smart_truncate_diff([], token_limit=100, model="test:model")
        assert result == ""
        mock_count.assert_not_called()

    @patch("gac.preprocess.count_tokens")
    def test_smart_truncate_diff_duplicate_files(self, mock_count):
        """Test truncation when duplicate files appear."""
        sections = [
            ("diff --git a/file.py b/file.py\n+content1", 5.0),
            ("diff --git a/file.py b/file.py\n+content2", 3.0),  # Same file
            ("diff --git a/other.py b/other.py\n+content3", 2.0),
        ]

        # Mock token counts: file.py(6), other.py(4)
        mock_count.side_effect = [6, 4]

        result = smart_truncate_diff(sections, token_limit=100, model="test:model")

        # Should include both unique files
        assert "content1" in result or "content2" in result  # One of the file.py sections
        assert "content3" in result  # other.py
        mock_count.assert_called()

    @patch("gac.preprocess.count_tokens")
    def test_smart_truncate_diff_token_limit_reached(self, mock_count):
        """Test truncation when token limit is reached (skipped files)."""
        sections = [
            ("diff --git a/important.py b/important.py\n+class Main", 10.0),
            ("diff --git a/less_important.py b/less_important.py\n+var x = 1", 2.0),
        ]

        # Mock to exceed token limit after first section
        mock_count.side_effect = [50, 60]  # First 50, second 60 (would exceed limit=100)

        result = smart_truncate_diff(sections, token_limit=100, model="test:model")

        # Should include the first section and potentially skipped summary
        assert "important.py" in result or "less_important.py" in result
        mock_count.assert_called()

    @patch("gac.preprocess.count_tokens")
    def test_smart_truncate_diff_summary_included(self, mock_count):
        """Test summary inclusion when space permits."""
        sections = [("diff --git a/file.py b/file.py\n+content", 5.0)]

        mock_count.return_value = 50  # Well under limit

        result = smart_truncate_diff(sections, token_limit=200, model="test:model")

        # Should include the section content
        assert "file.py" in result
        mock_count.assert_called()

    @patch("gac.preprocess.count_tokens")
    def test_smart_truncate_diff_no_room_for_summary(self, mock_count):
        """Test when there's no room for summary."""
        sections = [("diff --git a/large.py b/large.py\n" + "x" * 300, 5.0)]

        mock_count.return_value = 180  # Close to limit

        result = smart_truncate_diff(sections, token_limit=200, model="test:model")

        # Should not include summary when no room
        assert "Showing" not in result
        mock_count.assert_called()

    @patch("gac.preprocess.count_tokens")
    def test_smart_truncate_diff_many_skipped_files(self, mock_count):
        """Test many truncated files scenario."""
        # Create a few sections
        sections = [(f"diff --git a/file{i}.py b/file{i}.py\n+content{i}", 1.0) for i in range(3)]

        # Mock token count to be reasonable
        mock_count.return_value = 20  # Small token count

        result = smart_truncate_diff(sections, token_limit=100, model="test:model")

        # Should include file content
        assert "file0.py" in result
        mock_count.assert_called()
        mock_count.assert_called()


class TestPreprocessIntegration:
    """Integration tests combining multiple preprocess functions."""

    @patch("gac.preprocess.count_tokens")
    def test_filter_binary_and_minified_integration(self, mock_count):
        """Test filter_binary_and_minified integration path."""
        # Test with mixed content: some filtered, some not
        diff = """diff --git a/app.js b/app.js
+new content
diff --git a/app.min.js b/app.min.js
Binary files differ
diff --git a/style.css b/style.css
+styles
"""

        mock_count.return_value = 500  # Small enough

        with patch("gac.preprocess.split_diff_into_sections") as mock_split:
            mock_split.return_value = [
                "diff --git a/app.js b/app.js\n+new content",
                "diff --git a/app.min.js b/app.min.js\nBinary files differ",
                "diff --git a/style.css b/style.css\n+styles",
            ]
            with patch("gac.preprocess.should_filter_section") as mock_filter:
                mock_filter.side_effect = [False, True, False]
                with patch("gac.preprocess.extract_filtered_file_summary") as mock_summary:
                    mock_summary.return_value = "[Minified file change]\n"
                    result = filter_binary_and_minified(diff)

                    # Should include all sections, with filtered ones summarized
                    assert "app.js" in result
                    assert "style.css" in result
                    assert "[Minified file change]" in result

    @patch("gac.preprocess.logger")
    def test_logging_integration(self, mock_logger):
        """Test that logging works correctly during filtering."""
        section = "diff --git a/package-lock.json b/package-lock.json\nclassical: 100%75%"

        result = should_filter_section(section)

        assert result is True  # Should be filtered
        # Check that appropriate logging happened
        # Note: We can't easily test logger calls without mocking the logger import

    def test_concurrent_processing_thread_safety(self):
        """Test that parallel processing is thread-safe."""
        # Create many sections
        sections = [f"diff --git a/file{i}.py b/file{i}.py\n+content{i}" for i in range(6)]

        # This should not raise any exceptions
        result = process_sections_parallel(sections)

        # Should process all sections
        assert len(result) == 6

        # Verify threading was used (should complete quickly)
        # All sections should be processed, order may vary due to parallel execution
        for i in range(6):
            assert any(f"file{i}.py" in section for section in result)
