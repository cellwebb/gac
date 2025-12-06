"""AI provider implementations for commit message generation.

This module provides a unified interface to all AI providers. Provider classes
are registered and wrapper functions are auto-generated with error handling.

Usage:
    from gac.providers import PROVIDER_REGISTRY

    # Get the function for a provider
    func = PROVIDER_REGISTRY["openai"]
    result = func(model="gpt-4", messages=[...], temperature=0.7, max_tokens=1000)
"""

# Import provider classes for registration
from .anthropic import AnthropicProvider
from .azure_openai import AzureOpenAIProvider
from .cerebras import CerebrasProvider
from .chutes import ChutesProvider
from .claude_code import ClaudeCodeProvider
from .custom_anthropic import CustomAnthropicProvider
from .custom_openai import CustomOpenAIProvider
from .deepseek import DeepSeekProvider
from .fireworks import FireworksProvider
from .gemini import GeminiProvider
from .groq import GroqProvider
from .kimi_coding import KimiCodingProvider
from .lmstudio import LMStudioProvider
from .minimax import MinimaxProvider
from .mistral import MistralProvider
from .moonshot import MoonshotProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .openrouter import OpenRouterProvider
from .qwen import QwenProvider
from .registry import (
    PROVIDER_REGISTRY,
    register_provider,
)
from .replicate import ReplicateProvider
from .streamlake import StreamlakeProvider
from .synthetic import SyntheticProvider
from .together import TogetherProvider
from .zai import ZAICodingProvider, ZAIProvider

# Register all providers - this populates PROVIDER_REGISTRY automatically
register_provider("anthropic", AnthropicProvider)
register_provider("azure-openai", AzureOpenAIProvider)
register_provider("cerebras", CerebrasProvider)
register_provider("chutes", ChutesProvider)
register_provider("claude-code", ClaudeCodeProvider)
register_provider("custom-anthropic", CustomAnthropicProvider)
register_provider("custom-openai", CustomOpenAIProvider)
register_provider("deepseek", DeepSeekProvider)
register_provider("fireworks", FireworksProvider)
register_provider("gemini", GeminiProvider)
register_provider("groq", GroqProvider)
register_provider("kimi-coding", KimiCodingProvider)
register_provider("lm-studio", LMStudioProvider)
register_provider("minimax", MinimaxProvider)
register_provider("mistral", MistralProvider)
register_provider("moonshot", MoonshotProvider)
register_provider("ollama", OllamaProvider)
register_provider("openai", OpenAIProvider)
register_provider("openrouter", OpenRouterProvider)
register_provider("qwen", QwenProvider)
register_provider("replicate", ReplicateProvider)
register_provider("streamlake", StreamlakeProvider)
register_provider("synthetic", SyntheticProvider)
register_provider("together", TogetherProvider)
register_provider("zai", ZAIProvider)
register_provider("zai-coding", ZAICodingProvider)

# List of supported provider names - derived from registry keys
SUPPORTED_PROVIDERS = sorted(PROVIDER_REGISTRY.keys())

__all__ = [
    "PROVIDER_REGISTRY",
    "SUPPORTED_PROVIDERS",
    "register_provider",
]
