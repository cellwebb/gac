#!/bin/bash
# Test script for the --scope/-s flag functionality

set -e

echo "=== Testing GAC --scope flag ==="
echo

# Create a temporary test directory
TEST_DIR="/tmp/gac-scope-test-$$"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Initialize git repo
git init
git config user.email "test@example.com"
git config user.name "Test User"

# Create initial commit
echo "Initial content" > test.py
git add test.py
git commit -m "Initial commit"

echo "1. Testing --scope with specific value (auth)"
echo "   Creating a new authentication file..."
cat > auth.py << 'EOF'
def login(username, password):
    """Handle user login."""
    return True
EOF
git add auth.py

echo "   Running: gac preview --scope auth"
gac preview --scope auth || echo "Note: Preview may fail if AI providers aren't configured"
echo

echo "2. Testing -s short flag with value (api)"
echo "   Creating an API endpoint file..."
cat > api.py << 'EOF'
def get_users():
    """Get all users from the API."""
    return []
EOF
git add api.py

echo "   Running: gac preview -s api"
gac preview -s api || echo "Note: Preview may fail if AI providers aren't configured"
echo

echo "3. Testing --scope without value (AI determines scope)"
echo "   Modifying multiple files..."
echo "# Database config" >> test.py
cat > database.py << 'EOF'
def connect():
    """Connect to database."""
    pass
EOF
git add test.py database.py

echo "   Running: gac preview --scope"
gac preview --scope || echo "Note: Preview may fail if AI providers aren't configured"
echo

echo "4. Testing without --scope flag"
echo "   Adding a README file..."
cat > README.md << 'EOF'
# Test Project
This is a test project for GAC scope testing.
EOF
git add README.md

echo "   Running: gac preview"
gac preview || echo "Note: Preview may fail if AI providers aren't configured"
echo

echo "5. Testing --scope with other flags"
echo "   Modifying auth.py with hint..."
echo "def logout(): pass" >> auth.py
git add auth.py

echo "   Running: gac preview --scope auth --one-liner --hint 'Add logout functionality'"
gac preview --scope auth --one-liner --hint "Add logout functionality" || echo "Note: Preview may fail if AI providers aren't configured"
echo

# Cleanup
cd /
rm -rf "$TEST_DIR"

echo "=== Test script completed ==="
echo
echo "Note: This script demonstrates the --scope flag usage."
echo "Actual commit message generation requires AI provider configuration."
echo "Run 'pytest tests/test_scope_flag.py' for comprehensive unit tests."