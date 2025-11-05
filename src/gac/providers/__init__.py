"""AI provider implementations for commit message generation."""

from .anthropic import call_anthropic_api
from .cerebras import call_cerebras_api
from .chutes import call_chutes_api
from .claude_code import call_claude_code_api
from .custom_anthropic import call_custom_anthropic_api
from .custom_openai import call_custom_openai_api
from .deepseek import call_deepseek_api
from .fireworks import call_fireworks_api
from .gemini import call_gemini_api
from .groq import call_groq_api
from .lmstudio import call_lmstudio_api
from .minimax import call_minimax_api
from .mistral import call_mistral_api
from .ollama import call_ollama_api
from .openai import call_openai_api
from .openrouter import call_openrouter_api
from .streamlake import call_streamlake_api
from .synthetic import call_synthetic_api
from .together import call_together_api
from .zai import call_zai_api, call_zai_coding_api

__all__ = [
    "call_anthropic_api",
    "call_cerebras_api",
    "call_chutes_api",
    "call_claude_code_api",
    "call_custom_anthropic_api",
    "call_custom_openai_api",
    "call_deepseek_api",
    "call_fireworks_api",
    "call_gemini_api",
    "call_groq_api",
    "call_lmstudio_api",
    "call_minimax_api",
    "call_mistral_api",
    "call_ollama_api",
    "call_openai_api",
    "call_openrouter_api",
    "call_streamlake_api",
    "call_synthetic_api",
    "call_together_api",
    "call_zai_api",
    "call_zai_coding_api",
]
