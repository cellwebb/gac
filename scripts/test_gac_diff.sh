#!/usr/bin/env bash
set -eo pipefail

# Test script for GAC diff functionality
TEST_DIR="$HOME/.gac_diff_testing"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "===== Starting GAC Diff Tests ====="

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
cat > README.md << 'EOF'
# Test Project

This is a test project for GAC.
EOF

cat > main.py << 'EOF'
def hello():
    print('Hello, world!')
EOF

cat > test.py << 'EOF'
from main import hello

def test_hello():
    hello()
EOF

# Make initial commit
git add .
git commit -m "Initial commit"
INITIAL_COMMIT=$(git rev-parse HEAD)
echo "Initial commit: $INITIAL_COMMIT"

# Make some changes
cat > main.py << 'EOF'
def hello():
    print('Hello, GAC!')

def goodbye():
    print('Goodbye!')
EOF

cat > utils.py << 'EOF'
import sys
import os
EOF

# Test diff on modified files (unstaged)
echo
echo "== Testing diff on unstaged changes =="
gac diff --unstaged

# Stage some changes
git add main.py

# Test diff on staged changes
echo
echo "== Testing diff on staged changes =="
gac diff --staged

# Test diff with both staged and unstaged
echo
echo "== Testing diff with mixed changes =="
cat > utils.py << 'EOF'
import sys
import os
import json
EOF
gac diff

# Commit changes
git add .
git commit -m "Update main.py and add utils.py"
SECOND_COMMIT=$(git rev-parse HEAD)
echo "Second commit: $SECOND_COMMIT"

# Make more changes
cat > main.py << 'EOF'
def hello():
    name = 'GAC'
    print(f'Hello, {name}!')

def goodbye():
    print('Goodbye!')
EOF

# Test diff between commits
echo
echo "== Testing diff between commits =="
gac diff $INITIAL_COMMIT $SECOND_COMMIT

# Test diff with filter disabled
echo
echo "== Testing diff with no-filter flag =="
# Need to have unstaged changes for this test
cat > main.py << 'EOF'
def hello():
    name = 'GAC'
    print(f'Hello, {name}!')

def goodbye():
    print('Goodbye!')
EOF
gac diff --unstaged --no-filter

# Test diff with no-color flag
echo
echo "== Testing diff with no-color flag =="
gac diff --unstaged --no-color

# Create multiple file changes with different extensions
echo
echo "== Setting up complex changes =="
cat > logging_setup.py << 'EOF'
import logging
logger = logging.getLogger(__name__)
EOF

cat > config.py << 'EOF'
# Configuration file
DEBUG = True
VERSION = '1.0.0'
EOF

cat > style.css << 'EOF'
/* CSS file */
body { color: red; }
EOF

cat > package.json << 'EOF'
{"name": "test", "version": "1.0.0"}
EOF
git add .
git commit -m "Add configuration and logging files"

# Modify multiple files
cat > logging_setup.py << 'EOF'
import logging
import sys
logger = logging.getLogger(__name__)
EOF

cat > config.py << 'EOF'
# Configuration file
DEBUG = False
VERSION = '1.0.1'
AUTHOR = 'GAC Test'
EOF

cat > style.css << 'EOF'
/* CSS file */
body { 
    color: blue;
    font-size: 14px;
}
EOF

cat > package.json << 'EOF'
{"name": "test", "version": "1.0.1", "author": "GAC"}
EOF

# Test diff with multiple complex changes
echo
echo "== Testing diff with multiple file types =="
gac diff --unstaged

# Test diff with specific file (using commit reference)
echo
echo "== Testing diff for specific file =="
# First stage the changes to have something to compare
git add .
gac diff HEAD -- config.py

# Test diff with truncation disabled
echo
echo "== Testing diff with no-truncate flag =="
# Create a large change for testing truncation
cat > large_file.py << 'EOF'
# This is a large file with many lines to test truncation
import os
import sys
import json
import logging
import datetime
import random
import string
import collections
import itertools
import functools

def function1():
    """First function"""
    print("Function 1")
    return 1

def function2():
    """Second function"""
    print("Function 2")
    return 2

def function3():
    """Third function"""
    print("Function 3")
    return 3

def function4():
    """Fourth function"""
    print("Function 4")
    return 4

def function5():
    """Fifth function"""
    print("Function 5")
    return 5

# Add more content to make it larger
class TestClass:
    def __init__(self):
        self.value = 0
    
    def method1(self):
        return self.value + 1
    
    def method2(self):
        return self.value + 2
    
    def method3(self):
        return self.value + 3
EOF
gac diff --unstaged --no-truncate -- large_file.py

# Test diff with max-tokens option
echo
echo "== Testing diff with max-tokens option =="
gac diff --unstaged --max-tokens 100

# Test diff against HEAD
echo
echo "== Testing diff against HEAD =="
# Create changes first
echo "# Additional comment" >> config.py
gac diff HEAD

# Test diff with commit range
echo
echo "== Testing diff with commit range =="
gac diff HEAD~1..HEAD

# Create a binary file
echo
echo "== Testing diff with binary file =="
printf '\x00\x01\x02\x03' > binary.dat
git add binary.dat
gac diff --staged

# Test an invalid hash scenario (should fail gracefully)
echo
echo "== Testing diff with invalid hash (should fail) =="
gac diff invalid_hash 2>&1 || echo "Test passed: Invalid hash correctly failed"

# Test diff with no changes
echo
echo "== Testing diff with no changes =="
git add .
git commit -m "Commit all changes" > /dev/null 2>&1
gac diff || echo "Test passed: No changes detected"

echo
echo "===== Finished GAC Diff Tests ====="