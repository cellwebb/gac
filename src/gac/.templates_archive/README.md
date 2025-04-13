# Templates Archive

This directory contains archived template files that were previously used in the project but are no longer needed.

## Context

The template system has been simplified to use a single embedded template in the `prompt.py` file. This eliminates the
need for:

1. Multiple template files across different directories
2. Complex template search logic
3. Backward compatibility with older template formats

## Archived Files

- `default.prompt.bak`: The original template from `src/gac/templates/`
- `project_default.prompt.bak`: The original template from the project root `prompts/` directory

These files are kept for reference only and can be safely deleted once the new template system is confirmed working.
