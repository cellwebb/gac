"""Additional tests to improve preprocess.py coverage."""

from unittest import mock

from gac.preprocess import (
    analyze_code_patterns,
    calculate_section_importance,
    extract_filtered_file_summary,
    get_extension_score,
    is_lockfile_or_generated,
    is_minified_content,
    preprocess_diff,
    process_section,
    process_sections_parallel,
    should_filter_section,
    smart_truncate_diff,
    split_diff_into_sections,
)


class TestPreprocessMissingCoverage:
    """Test missing coverage areas in preprocess.py."""

    def test_preprocess_diff_empty_string(self):
        """Test preprocess_diff with empty string (line 113->111)."""
        result = preprocess_diff("")
        assert result == ""

    def test_preprocess_diff_none_input(self):
        """Test preprocess_diff with None input."""
        result = preprocess_diff(None)  # type: ignore
        assert result is None or result == ""

    def test_process_sections_parallel_empty_list(self):
        """Test process_sections_parallel with empty list."""
        result = process_sections_parallel([])
        assert result == []

    def test_process_sections_parallel_small_list_sequential(self):
        """Test process_sections_parallel with small list (sequential processing - lines 166-161)."""
        sections = ["section1", "section2", "section3"]
        result = process_sections_parallel(sections)
        assert len(result) == 3

    def test_process_sections_parallel_large_list_parallel(self):
        """Test process_sections_parallel with large list (parallel processing)."""
        sections = ["section1", "section2", "section3", "section4", "section5"]

        with mock.patch("gac.preprocess.process_section") as mock_process:
            mock_process.return_value = "processed_section"

            result = process_sections_parallel(sections)

            # Should call process_section for each section
            assert mock_process.call_count == 5
            assert len(result) == 5

    def test_process_section_none_result(self):
        """Test process_section returns None for filtered sections."""
        with mock.patch("gac.preprocess.should_filter_section", return_value=True):
            with mock.patch("gac.preprocess.extract_filtered_file_summary") as mock_extract:
                mock_extract.return_value = None

                result = process_section("binary_file_section")

                assert result is None

    def test_extract_filtered_file_summary_binary_section(self):
        """Test extract_filtered_file_summary for binary sections (lines 208-211)."""
        binary_section = """diff --git a/image.jpg b/image.jpg
new file mode 100644
index 0000000..1234567
Binary file /dev/null => image.jpg (150 KB)
"""

        result = extract_filtered_file_summary(binary_section)
        assert "[Binary file change]" in result
        assert "image.jpg" in result

    def test_extract_filtered_file_summary_deleted_file(self):
        """Test extract_filtered_file_summary for deleted file."""
        deleted_section = """diff --git a/deleted.txt b/deleted.txt
deleted file mode 100644
index 1234567..0000000
"""

        result = extract_filtered_file_summary(deleted_section)
        assert "deleted file" in result

    def test_extract_filtered_file_summary_new_file(self):
        """Test extract_filtered_file_summary for new file."""
        new_section = """diff --git a/new.txt b/new.txt
new file mode 100644
index 0000000..1234567
"""

        result = extract_filtered_file_summary(new_section)
        assert "new file" in result

    def test_extract_filtered_file_summary_with_custom_change_type(self):
        """Test extract_filtered_file_summary with custom change type."""
        section = """diff --git a/file.py b/file.py
new file mode 100644
"""

        result = extract_filtered_file_summary(section, "[Custom change type]")
        assert "[Custom change type]" in result

    def test_extract_filtered_file_summary_no_filename_match(self):
        """Test extract_filtered_file_summary when filename doesn't match pattern."""
        invalid_section = "invalid diff format"

        result = extract_filtered_file_summary(invalid_section)
        assert result == "\n"

    def test_should_filter_section_binary_pattern_matched(self):
        """Test should_filter_section with binary pattern match."""
        binary_section = """diff --git a/image.png b/image.png
Binary file
"""

        with mock.patch("gac.preprocess.FilePatterns.BINARY", [r"Binary file"]):
            result = should_filter_section(binary_section)
            assert result is True

    def test_should_filter_section_minified_extension(self):
        """Test should_filter_section with minified extension."""
        minified_section = """diff --git a/app.min.js b/app.min.js
--- /dev/null
+++ b/app.min.js
"""

        with mock.patch("gac.preprocess.FilePatterns.MINIFIED_EXTENSIONS", [".min.js"]):
            result = should_filter_section(minified_section)
            assert result is True

    def test_should_filter_section_build_directory(self):
        """Test should_filter_section with build directory."""
        build_section = """diff --git a/dist/app.js b/dist/app.js
--- /dev/null
+++ b/dist/app.js
"""

        with mock.patch("gac.preprocess.FilePatterns.BUILD_DIRECTORIES", ["dist"]):
            result = should_filter_section(build_section)
            assert result is True

    def test_should_filter_section_lockfile_patterns(self):
        """Test should_filter_section with lockfile patterns (lines 282, 296)."""
        lockfile_section = """diff --git a/package-lock.json b/package-lock.json
--- /dev/null
+++ b/package-lock.json
"""

        result = should_filter_section(lockfile_section)
        assert result is True

    def test_should_filter_section_generated_patterns(self):
        """Test should_filter_section with generated file patterns."""
        generated_section = """diff --git a/autogen.proto b/autogen.proto
--- /dev/null
+++ b/autogen.proto
"""

        result = should_filter_section(generated_section)
        assert result is True

    def test_should_filter_section_minified_content(self):
        """Test should_filter_section with minified content."""
        minified_content = "var a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10;"

        with mock.patch("gac.preprocess.is_minified_content", return_value=True):
            section = f"""diff --git a/script.js b/script.js
--- /dev/null
+++ b/script.js
+{minified_content}
"""
            result = should_filter_section(section)
            assert result is True

    def test_is_lockfile_or_generated_package_lock(self):
        """Test is_lockfile_or_generated with package-lock.json."""
        result = is_lockfile_or_generated("package-lock.json")
        assert result is True

    def test_is_lockfile_or_generated_go_sum(self):
        """Test is_lockfile_or_generated with .sum file."""
        result = is_lockfile_or_generated("go.sum")
        assert result is True

    def test_is_lockfile_or_generated_protobuf(self):
        """Test is_lockfile_or_generated with .pb.go file."""
        result = is_lockfile_or_generated("service.pb.go")
        assert result is True

    def test_is_lockfile_or_generated_autogen(self):
        """Test is_lockfile_or_generated with autogen file."""
        result = is_lockfile_or_generated("autogen.proto")
        assert result is True

    def test_is_lockfile_or_generated_normal_file(self):
        """Test is_lockfile_or_generated with normal file."""
        result = is_lockfile_or_generated("main.py")
        assert result is False

    def test_is_minified_content_empty_string(self):
        """Test is_minified_content with empty string (line 346)."""
        result = is_minified_content("")
        assert result is False

    def test_is_minified_content_none(self):
        """Test is_minified_content with None."""
        result = is_minified_content(None)  # type: ignore
        assert result is False

    def test_is_minified_content_few_lines_long_content(self):
        """Test is_minified_content with few lines but long content."""
        content = "a" * 1500  # Long content with few lines
        result = is_minified_content(content)
        assert result is True

    def test_is_minified_content_single_long_line(self):
        """Test is_minified_content with single long line."""
        content = (
            "var a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10,k=11,l=12,m=13,n=14,o=15,p=16,q=17,r=18,s=19,t=20,u=21,v=22,w=23,x=24,y=25,z=26,w=27,x=28,y=29,z=30,a=31,b=32,c=33,d=34,e=35,f=36,g=37,h=38,i=39,j=40,k=41,l=42,m=43,n=44,o=45,p=46,q=47,r=48,s=49,t=50,u=51,v=52,w=53,x=54,y=55,z=56;"
            + "\n"
        )  # Add newline to make it multiline
        result = is_minified_content(content)
        assert result is True

    def test_is_minified_content_lines_with_few_spaces(self):
        """Test is_minified_content with lines containing few spaces (lines 354-358)."""
        content = "verylongvariablenamethatissuperlongevendehereanddoesn'thavesomuchspacing" * 3
        result = is_minified_content(content)
        assert result is True

    def test_is_minified_content_many_long_lines(self):
        """Test is_minified_content with many long lines."""
        lines = ["a" * 600 for _ in range(10)]  # 10 lines of 600 chars each
        content = "\n".join(lines)
        result = is_minified_content(content)
        assert result is True

    def test_is_minified_content_normal_code(self):
        """Test is_minified_content with normal code."""
        normal_code = """def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
"""
        result = is_minified_content(normal_code)
        assert result is False

    def test_calculate_section_importance_no_filename_match(self):
        """Test calculate_section_importance with invalid diff format (line 382)."""
        invalid_section = "not a valid diff"
        result = calculate_section_importance(invalid_section)
        assert result == 1.0  # Base importance

    def test_calculate_section_importance_new_file_mode(self):
        """Test calculate_section_importance with new file mode."""
        new_file_section = """diff --git a/new.py b/new.py
new file mode 100644
+++ b/new.py
"""
        result = calculate_section_importance(new_file_section)
        assert result > 1.0  # Should be boosted for new files

    def test_calculate_section_importance_deleted_file_mode(self):
        """Test calculate_section_importance with deleted file mode."""
        deleted_section = """diff --git a/deleted.py b/deleted.py
deleted file mode 100644
--- a/deleted.py
"""
        result = calculate_section_importance(deleted_section)
        assert result > 1.0  # Should be boosted for deleted files

    def test_calculate_section_importance_many_changes(self):
        """Test calculate_section_importance with many changes."""
        changes_section = """diff --git a/changes.py b/changes.py
+++ b/changes.py
+line1
+line2
+line3
+line4
+line5
+line6
+line7
+line8
+line9
+line10
"""
        result = calculate_section_importance(changes_section)
        assert result > 1.0  # Should be boosted for many changes

    def test_get_extension_score_pattern_match(self):
        """Test get_extension_score with pattern match (not extension)."""
        with mock.patch("gac.preprocess.FileTypeImportance.EXTENSIONS", {"test": 2.0}):
            result = get_extension_score("test_file")
            assert result == 2.0

    def test_get_extension_score_no_extension(self):
        """Test get_extension_score with no extension."""
        with mock.patch("gac.preprocess.FileTypeImportance.EXTENSIONS", {}):
            result = get_extension_score("README")
            assert result == 1.0

    def test_analyze_code_patterns_no_patterns_found(self):
        """Test analyze_code_patterns with no patterns found (line 421)."""
        section = "regular code without patterns"

        with mock.patch("gac.preprocess.CodePatternImportance.PATTERNS", {}):
            result = analyze_code_patterns(section)
            assert result == 0.9  # Should be reduced when no patterns found

    def test_analyze_code_patterns_multiple_patterns(self):
        """Test analyze_code_patterns with multiple patterns."""
        section = "def class interface enum"

        patterns = {
            r"def ": 1.1,
            r"class ": 1.2,
            r"interface ": 1.3,
            r"enum ": 1.4,
        }

        with mock.patch("gac.preprocess.CodePatternImportance.PATTERNS", patterns):
            result = analyze_code_patterns(section)
            expected = 1.1 * 1.2 * 1.3 * 1.4  # Patterns found, no 0.9 multiplier
            assert abs(result - expected) < 0.01

    def test_smart_truncate_diff_empty_sections(self):
        """Test smart_truncate_diff with empty sections."""
        result = smart_truncate_diff([], 100, "test-model")
        assert result == ""

    def test_smart_truncate_diff_high_token_limit(self):
        """Test smart_truncate_diff with high token limit (lines 488-509)."""
        sections = [
            ("section1", 1.0),
            ("section2", 2.0),
            ("section3", 0.5),
        ]

        result = smart_truncate_diff(sections, 1000, "test-model")
        # Should include all sections without complex processing
        assert "section1" in result
        assert "section2" in result
        assert "section3" in result

    def test_smart_truncate_diff_no_file_match(self):
        """Test smart_truncate_diff with sections that don't match file pattern."""
        sections = [
            ("invalid_section_without_filename", 1.0),
        ]

        result = smart_truncate_diff(sections, 100, "test-model")
        assert result == ""

    def test_smart_truncate_diff_duplicate_files(self):
        """Test smart_truncate_diff with duplicate file names."""
        sections = [
            ("diff --git a/file.py b/file.py\n+content1", 1.0),
            ("diff --git a/file.py b/file.py\n+content2", 2.0),
        ]

        with mock.patch("gac.preprocess.count_tokens", return_value=50):
            result = smart_truncate_diff(sections, 100, "test-model")
            # Should only include the first occurrence of each file
            # Check that the first occurrence is included but not the second
            assert "content1" in result
            assert "content2" not in result

    def test_smart_truncate_diff_with_skipped_sections_summary(self):
        """Test smart_truncate_diff with skipped sections and summary."""
        sections = []

        # Create many sections that will be skipped due to token limit
        for i in range(10):
            sections.append((f"diff --git a/file{i}.py b/file{i}.py\n+{'content' * 100}", 1.0))

        with mock.patch("gac.preprocess.count_tokens", return_value=20):
            result = smart_truncate_diff(sections, 100, "test-model")

            # Should include summary for skipped files
            has_summary = "[Skipped files" in result or "Summary:" in result
            assert has_summary, f"Expected summary in result but got: {result[:200]}..."

    def test_smart_truncate_diff_token_limit_exceeded_immediately(self):
        """Test smart_truncate_diff when first section exceeds token limit."""
        sections = [
            ("diff --git a/large.py b/large.py\n+{'content' * 1000}", 1.0),
        ]

        with mock.patch("gac.preprocess.count_tokens", return_value=150):
            result = smart_truncate_diff(sections, 100, "test-model")
            # Should be empty since first section exceeds limit
            assert result == ""

    def test_split_diff_into_sections_empty_string(self):
        """Test split_diff_into_sections with empty string."""
        result = split_diff_into_sections("")
        assert result == []

    def test_split_diff_into_sections_no_diff_git(self):
        """Test split_diff_into_sections without diff --git markers."""
        result = split_diff_into_sections("regular text")
        assert result == ["regular text"]

    def test_split_diff_into_sections_multiple_files(self):
        """Test split_diff_into_sections with multiple files."""
        diff = """diff --git a/file1.py b/file1.py
--- a/file1.py
+++ b/file1.py
+content1
diff --git a/file2.js b/file2.js
--- a/file2.js
+++ b/file2.js
+content2
"""
        result = split_diff_into_sections(diff)
        assert len(result) == 2
        assert "file1.py" in result[0]
        assert "file2.js" in result[1]
