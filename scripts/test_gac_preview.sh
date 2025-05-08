#!/usr/bin/env bash
set -eo pipefail

# Test script for GAC preview functionality
TEST_DIR="$HOME/.gac_preview_testing"

echo "===== Starting GAC Preview Tests ====="

# 1. Create the folder if it doesn't exist
mkdir -p "$TEST_DIR"

# 2. Clear the folder if not empty (including hidden files/folders)
if [ -d "$TEST_DIR" ]; then
  find "$TEST_DIR" -mindepth 1 -delete 2>/dev/null || find "$TEST_DIR" -mindepth 1 -exec rm -rf {} \; 2>/dev/null
fi

cd "$TEST_DIR"

# 3. Set up git repo
rm -rf .git
git init

# 4. Configure Git
git config user.name "GAC Test User"
git config user.email "test@gac.local"

echo "== Creating test repository =="

# Create initial files
echo -e "# Test Project\n\nThis is a test project for GAC." > README.md
echo -e "def hello():\n    print('Hello, world!')" > main.py
echo -e "from main import hello\n\ndef test_hello():\n    hello()" > test.py

# Make initial commit
git add .
git commit -m "Initial commit"
INITIAL_COMMIT=$(git rev-parse HEAD)
echo "Initial commit: $INITIAL_COMMIT"

# Make some changes
echo -e "def hello():\n    print('Hello, GAC!')\n\ndef goodbye():\n    print('Goodbye!')" > main.py
echo -e "import sys\nimport os" > utils.py

# Test preview on modified files
echo -e "\n== Testing preview against HEAD =="
gac preview HEAD

# Commit changes
git add .
git commit -m "Update main.py and add utils.py"
SECOND_COMMIT=$(git rev-parse HEAD)
echo "Second commit: $SECOND_COMMIT"

# Make more changes
echo -e "def hello():\n    name = 'GAC'\n    print(f'Hello, {name}!')\n\ndef goodbye():\n    print('Goodbye!')" > main.py

# Test preview between commits
echo -e "\n== Testing preview between commits =="
gac preview $INITIAL_COMMIT $SECOND_COMMIT

# Test preview with options
echo -e "\n== Testing preview with one-liner option =="
gac preview HEAD --one-liner

# Test with hint flag
echo -e "\n== Testing preview with hint =="
gac preview HEAD --hint "Fix string formatting"

# Test with show-prompt flag
echo -e "\n== Testing preview with show-prompt flag =="
gac preview HEAD --show-prompt

# Test a complex scenario with multiple files
echo -e "\n== Testing preview with multiple file changes =="
echo -e "import logging\nlogger = logging.getLogger(__name__)" > logging_setup.py
echo -e "# Configuration file\nDEBUG = True\nVERSION = '1.0.0'" > config.py
git add .
git commit -m "Add configuration and logging files"
echo -e "import logging\nimport sys\nlogger = logging.getLogger(__name__)" > logging_setup.py
echo -e "# Configuration file\nDEBUG = False\nVERSION = '1.0.1'\nAUTHOR = 'GAC Test'" > config.py
echo -e "def hello():\n    name = 'GAC'\n    print(f'Hello, {name}!')\n\ndef goodbye(name='User'):\n    print(f'Goodbye, {name}!')" > main.py
echo -e "\n== Testing preview with multiple complex changes =="
gac preview HEAD

# Test an invalid hash scenario (should fail gracefully)
echo -e "\n== Testing preview with invalid hash (should fail) =="
gac preview invalid_hash 2>&1 || echo "Test passed: Invalid hash correctly failed"

echo -e "\n===== Finished GAC Preview Tests ====="
