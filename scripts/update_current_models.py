#!/usr/bin/env python3
"""Update models.json with current models from provider APIs.

This script fetches current text-to-text models from supported provider APIs
and updates the models.json file with the latest information.
"""

import argparse
import json
import os
import pathlib
import sys
from typing import Dict, List, Optional

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gac.config import PACKAGE_DIR
except ImportError:
    PACKAGE_DIR = pathlib.Path(__file__).parent.parent / "src" / "gac"


def fetch_anthropic_models(api_key: str) -> List[str]:
    """Fetch available text models from Anthropic API.

    Args:
        api_key: Anthropic API key

    Returns:
        List of model names
    """
    try:
        import anthropic

        # Anthropic doesn't have a list models endpoint, so we use a predefined list
        # of their known models regardless of the API key
        _ = anthropic.Client(api_key=api_key)  # Verify API key works
        models = [
            "claude-3-5-sonnet-20240620",
            "claude-3-5-haiku-20240307",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
        ]
        return models
    except ImportError:
        print("Anthropic SDK not installed. Run: pip install anthropic")
        return []
    except Exception as e:
        print(f"Error fetching Anthropic models: {e}")
        return []


def fetch_openai_models(api_key: str) -> List[str]:
    """Fetch available text models from OpenAI API.

    Args:
        api_key: OpenAI API key

    Returns:
        List of model names
    """
    try:
        import openai

        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()

        # Filter for GPT text models only
        text_models = []
        for model in models.data:
            if model.id.startswith(("gpt-", "text-")) and not model.id.endswith(
                ("-vision", "vision")
            ):
                text_models.append(model.id)

        # Sort and return unique models
        return sorted(set(text_models))
    except ImportError:
        print("OpenAI SDK not installed. Run: pip install openai")
        return []
    except Exception as e:
        print(f"Error fetching OpenAI models: {e}")
        return []


def fetch_groq_models(api_key: str) -> List[str]:
    """Fetch available text models from Groq API.

    Args:
        api_key: Groq API key

    Returns:
        List of model names
    """
    try:
        import groq

        client = groq.Groq(api_key=api_key)
        models = client.models.list()

        # Return all model names
        return [model.id for model in models.data]
    except ImportError:
        print("Groq SDK not installed. Run: pip install groq")
        return []
    except Exception as e:
        print(f"Error fetching Groq models: {e}")
        return []


def fetch_mistral_models(api_key: str) -> List[str]:
    """Fetch available text models from Mistral API.

    Args:
        api_key: Mistral API key

    Returns:
        List of model names
    """
    try:
        import mistralai.client

        client = mistralai.client.MistralClient(api_key=api_key)
        models = client.list_models()

        # Return all model names
        return [model.id for model in models]
    except ImportError:
        print("Mistral SDK not installed. Run: pip install mistralai")
        return []
    except Exception as e:
        print(f"Error fetching Mistral models: {e}")
        return []


def fetch_ollama_models() -> List[str]:
    """Fetch available models from Ollama (local installation).

    Returns:
        List of model names
    """
    try:
        import ollama

        models = ollama.list()
        return [model["name"] for model in models.get("models", [])]
    except ImportError:
        print("Ollama SDK not installed. Run: pip install ollama")
        return []
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return []


def update_models_file(
    models_data: Dict[str, List[str]], output_path: Optional[str] = None
) -> None:
    """Update the models JSON file with new data.

    Args:
        models_data: Dictionary mapping providers to their model lists
        output_path: Optional path to write the JSON file
    """
    # Use default location if not specified
    if not output_path:
        output_path = PACKAGE_DIR / "models.json"
    else:
        output_path = pathlib.Path(output_path)

    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    with open(output_path, "w") as f:
        json.dump(models_data, f, indent=2)

    print(f"Updated models written to: {output_path}")


def main():
    """Run the model update script."""
    parser = argparse.ArgumentParser(description="Update available models from provider APIs")
    parser.add_argument(
        "--output", "-o", help="Path to write the models JSON file (default: package models.json)"
    )
    parser.add_argument(
        "--user",
        "-u",
        action="store_true",
        help="Write to user's ~/.gac.models.json instead of package location",
    )
    args = parser.parse_args()

    # Determine output path
    output_path = None
    if args.user:
        output_path = pathlib.Path.home() / ".gac.models.json"
    elif args.output:
        output_path = args.output

    # Get API keys from environment variables
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    mistral_key = os.environ.get("MISTRAL_API_KEY")

    # Initialize models dictionary
    models_data = {}

    # Fetch models from each provider if API key is available
    if anthropic_key:
        print("Fetching Anthropic models...")
        models_data["anthropic"] = fetch_anthropic_models(anthropic_key)
        print(f"Found {len(models_data['anthropic'])} Anthropic models")

    if openai_key:
        print("Fetching OpenAI models...")
        models_data["openai"] = fetch_openai_models(openai_key)
        print(f"Found {len(models_data['openai'])} OpenAI models")

    if groq_key:
        print("Fetching Groq models...")
        models_data["groq"] = fetch_groq_models(groq_key)
        print(f"Found {len(models_data['groq'])} Groq models")

    if mistral_key:
        print("Fetching Mistral models...")
        models_data["mistral"] = fetch_mistral_models(mistral_key)
        print(f"Found {len(models_data['mistral'])} Mistral models")

    # For Ollama, no API key is needed
    print("Fetching Ollama models...")
    ollama_models = fetch_ollama_models()
    if ollama_models:
        models_data["ollama"] = ollama_models
        print(f"Found {len(models_data['ollama'])} Ollama models")

    # If no models were found, exit
    if not models_data:
        print("No models were found. Make sure your API keys are set as environment variables.")
        sys.exit(1)

    # Update the models JSON file
    update_models_file(models_data, output_path)


if __name__ == "__main__":
    main()
