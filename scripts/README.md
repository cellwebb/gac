# GAC Script Utilities

This directory contains utility scripts for maintaining and enhancing the Git Auto Commit (GAC)
tool.

## Model Update Script

The `update_current_models.py` script queries the APIs of supported language model providers to
fetch their current available text-to-text models. This helps keep the model lists in GAC current
without manual updates.

### Requirements

Before running the script, install the required SDK packages for the providers you want to query:

```bash
# Install all SDKs
pip install anthropic openai groq mistralai ollama

# Or install only specific ones
pip install openai mistralai
```

### Usage

Set your API keys as environment variables:

```bash
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here
export GROQ_API_KEY=your_key_here
export MISTRAL_API_KEY=your_key_here
```

Then run the script:

```bash
# Update the package models.json file (requires write permission)
python scripts/update_current_models.py

# Update your user-specific models file (~/.gac.models.json)
python scripts/update_current_models.py --user

# Write to a custom location
python scripts/update_current_models.py --output path/to/custom/models.json
```

### How It Works

The script:

1. Queries each provider's API to fetch available text-to-text models
2. Formats the results into a JSON dictionary mapping providers to model lists
3. Writes the updated data to a models.json file
4. For providers where listing models isn't supported via API (like Anthropic), it uses a predefined
   list

### Notes

- You only need API keys for the providers you want to query
- For local Ollama models, no API key is needed, but the Ollama service must be running
- The script will only update models for providers where it can successfully fetch data
