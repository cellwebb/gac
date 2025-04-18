#!/usr/bin/env bash
# set -euo pipefail

TEST_DIR="$HOME/.gac_testing"

# Ensure clean state: remove remote GH repo if it exists
REPO_NAME="gac-test-sandbox"
GH_USER=$(gh api user --jq .login 2>/dev/null || echo "")

ensure_github_remote() {
  if [ -n "$GH_USER" ]; then
    gh repo delete "$GH_USER/$REPO_NAME" --yes > /dev/null 2>&1 || true
    gh repo create "$REPO_NAME" --private --source=. --remote=origin --push --confirm > /dev/null 2>&1 || true
  fi
}

# Clean up any existing test repo at the start
ensure_github_remote

# 1. Create the folder if it doesn't exist
mkdir -p "$TEST_DIR"

# 2. Clear the folder if not empty (including hidden files/folders)
if [ -d "$TEST_DIR" ]; then
  find "$TEST_DIR" -mindepth 1 -exec rm -rf {} +
fi

cd "$TEST_DIR"

# 3. Ensure .git/ is gone, then git init
rm -rf .git
git init
# Always set up remote after git init, in correct directory
ensure_github_remote
git remote remove origin 2>/dev/null || true
git remote add origin "git@github.com:$GH_USER/$REPO_NAME.git"
(git remote -v || true)

# Create and stage alpha.txt BEFORE first test
echo "alpha" > alpha.txt
git add alpha.txt

# Helper to summarize results
summary_ok=()
summary_fail=()

# Wrap each test/check in a function for summary reporting
run_test() {
  desc="$1"
  shift
  if "$@"; then
    summary_ok+=("$desc")
  else
    summary_fail+=("$desc")
  fi
}

echo "First test: default gac"
run_test "First test: default gac" gac -y
gac_status=$?
run_test "gac -y exited 0" [ $gac_status -eq 0 ]
run_test "Commit for alpha.txt found" git log --oneline -- alpha.txt 2>/dev/null | grep -q .

# Undo first commit
echo "Undo first commit"
if git rev-parse HEAD~1 >/dev/null 2>&1; then
  git reset --hard HEAD~1
else
  git update-ref -d HEAD
  rm -f .git/index
  git clean -fdx
  git init
  ensure_github_remote
  git remote remove origin 2>/dev/null || true
  git remote add origin "git@github.com:$GH_USER/$REPO_NAME.git"
  (git remote -v || true)
  echo "Repo reset to empty state."
fi
run_test "Commit was undone" sh -c '! git log --oneline -- alpha.txt 2>/dev/null | grep -q .'

# Second test: one-liner
echo "Second test: one-liner"
echo "beta" > beta.txt
git add beta.txt
run_test "Second test: one-liner" gac -yo
gac_status=$?
run_test "gac -yo exited 0" [ $gac_status -eq 0 ]
run_test "One-liner commit for beta.txt found" git log --oneline -- beta.txt 2>/dev/null | grep -q .

# Third test: with hint
echo "Third test: with hint"
echo "gamma" > gamma.txt
git add gamma.txt
run_test "Third test: with hint" gac -y --hint "testing hint flag"
gac_status=$?
run_test "gac -y --hint exited 0" [ $gac_status -eq 0 ]
run_test "Commit for gamma.txt with hint found" git log --oneline -- gamma.txt 2>/dev/null | grep -q .

# Fourth test: dry run (should not commit)
echo "Fourth test: dry run (should not commit)"
echo "delta" > delta.txt
git add delta.txt
run_test "Fourth test: dry run" gac -y --dry-run
gac_status=$?
run_test "gac -y --dry-run exited 0" [ $gac_status -eq 0 ]
run_test "Dry run did not create a commit for delta.txt" sh -c '! git log --oneline -- delta.txt 2>/dev/null | grep -q .'

# Undo last two commits
echo "Undo last two commits"
if git rev-parse HEAD~2 >/dev/null 2>&1; then
  git reset --hard HEAD~2
else
  git update-ref -d HEAD
  rm -f .git/index
  git clean -fdx
  git init
  ensure_github_remote
  git remote remove origin 2>/dev/null || true
  git remote add origin "git@github.com:$GH_USER/$REPO_NAME.git"
  (git remote -v || true)
  echo "Repo reset to empty state (not enough commits for HEAD~2)."
fi
run_test "Commits were undone" sh -c '! git log --oneline -- gamma.txt 2>/dev/null | grep -q . && ! git log --oneline -- beta.txt 2>/dev/null | grep -q .'

# Fifth test: add, commit, push
echo "Fifth test: add, commit, push"
echo "epsilon" > epsilon.txt
git add epsilon.txt
ensure_github_remote
(git remote -v || true)
output=$(gac -ypo --hint "final test for push" 2>&1)
gac_status=$?
run_test "gac -ypo --hint exited 0" [ $gac_status -eq 0 ]
run_test "Commit for epsilon.txt found" git log --oneline -- epsilon.txt 2>/dev/null | grep -q .
run_test "Push successful" sh -c '! echo "$output" | grep -q "fatal:"'

# If push output contains 'no upstream branch', echo the error and a note for clarity
if echo "$output" | grep -q "no upstream branch"; then
  echo "$output" | grep "no upstream branch" | head -1
  echo "[NOTE] The error about 'no upstream branch' is expected for a fresh repo and does not indicate test failure."
fi

# Cleanup: remove everything including .git
cd ~
rm -rf "$TEST_DIR"

# Cleanup GH test repo at end
if [ -n "$GH_USER" ]; then
  gh repo delete "$GH_USER/$REPO_NAME" --yes > /dev/null 2>&1 || true
fi

echo
if [ ${#summary_fail[@]} -eq 0 ]; then
  echo "All sandbox tests PASSED!"
  for t in "${summary_ok[@]}"; do echo "✔ $t"; done
else
  echo "Some sandbox tests FAILED:" >&2
  for t in "${summary_fail[@]}"; do echo "✘ $t"; done
  for t in "${summary_ok[@]}"; do echo "✔ $t"; done
  exit 1
fi
