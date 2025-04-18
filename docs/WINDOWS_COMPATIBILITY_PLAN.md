# Windows Compatibility Plan

## Objective

Ensure the project works seamlessly on Windows by addressing platform-specific issues.

## Tasks

### 1. Path Handling

- **Action:** Replace hardcoded paths with `os.path.join()` or `pathlib.Path`.

- **Example:**

  ```python
  from pathlib import Path
  file_path = Path("some_directory") / "file.txt"
  ```

### 2. Shell Commands

- **Action:** Use `subprocess` with `shell=True` or platform-specific logic.

- **Example:**

  ```python
  import subprocess
  import platform

  if platform.system() == "Windows":
      subprocess.run(["cmd.exe", "/c", "echo Hello Windows"], shell=True)
  else:
      subprocess.run(["echo", "Hello Unix"], shell=True)
  ```

### 3. Environment Variables

- **Action:** Use `os.environ` for cross-platform environment variable access.

- **Example:**

  ```python
  import os
  home_dir = os.environ.get("HOME") or os.environ.get("USERPROFILE")
  ```

### 4. Line Endings

- **Action:** Use `open()` with the `newline` parameter.

- **Example:**

  ```python
  with open("file.txt", "r", newline="") as f:
      content = f.read()
  ```

### 5. File Permissions

- **Action:** Use `os.chmod()` carefully, and consider using `stat` for permission flags.

- **Example:**

  ```python
  import os
  import stat
  os.chmod("file.txt", stat.S_IRUSR | stat.S_IWUSR)
  ```

### 6. Testing on Windows

- **Action:** Use `pytest.mark.skipif` to skip tests not applicable to Windows.

- **Example:**

  ```python
  import pytest
  import platform

  @pytest.mark.skipif(platform.system() == "Windows", reason="Not applicable on Windows")
  def test_unix_specific_feature():
      assert True
  ```

### 7. Virtual Environment

- **Action:** Use `uv` for virtual environment management.

- **Example:**

  ```bash
  uv venv .venv
  ```

### 8. Documentation

- **Action:** Update `README.md` to include Windows-specific setup instructions.

- **Example:**

  ````markdown
  ## Windows Setup

  1. Install Python from [python.org](https://www.python.org/downloads/windows/).
  2. Use `uv` to create a virtual environment:
     ```bash
     uv venv .venv
     ```
  3. Activate the virtual environment:
     ```bash
     .venv\Scripts\activate
     ```
  ````

### 9. CI/CD Integration

- **Action:** Add a Windows job to your CI/CD configuration.

- **Example:**

  ```yaml
  jobs:
    windows:
      runs-on: windows-latest
      steps:
        - uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: "3.x"
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt
        - name: Run tests
          run: pytest
  ```

### 10. Dependencies

- **Action:** Check dependencies for Windows compatibility and update `requirements.txt` or `pyproject.toml`.

- **Example:**

  ```bash
  pip check
  ```

## Deliverables

- Updated codebase with cross-platform compatibility (Python 3.10+, macOS, Linux, and Windows)
- Updated `README.md` and `INSTALLATION.md` with Windows setup instructions
- CI/CD configuration with Windows job
- Comprehensive test suite with platform-specific tests
- Updated `CHANGELOG.md` with Windows compatibility changes (see [CHANGELOG.md](../CHANGELOG.md))

## Timeline

- **Day 1-2:** Path handling and shell commands.
- **Day 3-4:** Environment variables and line endings.
- **Day 5:** File permissions and testing.
- **Day 6:** Virtual environment and documentation.
- **Day 7:** CI/CD integration and dependencies.

## Notes

- Ensure all changes are tested on both Windows and Unix-based systems.
- Update the `CHANGELOG.md` with the changes made for Windows compatibility.
