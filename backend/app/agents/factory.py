"""
Agent Provider Factory.
"""
from typing import Dict, Type
from app.agents.base import AgentProvider
from app.agents.mock_provider import MockProvider
from app.agents.gemini_provider import GeminiProvider
from app.agents.groq_provider import GroqProvider

_PROVIDERS: Dict[str, Type[AgentProvider]] = {
    "mock": MockProvider,
    "gemini": GeminiProvider,
    "groq": GroqProvider,
}

def get_provider(provider_name: str, **kwargs) -> AgentProvider:
    """
    Get an instance of an agent provider.
    
    Args:
        provider_name: Name of the provider (e.g., "mock", "openai")
        **kwargs: Provider-specific configuration
        
    Returns:
        AgentProvider instance
        
    Raises:
        ValueError: If provider is not supported
    """
    if provider_name not in _PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider_name}. Supported: {list(_PROVIDERS.keys())}")
        
    provider_class = _PROVIDERS[provider_name]
    return provider_class(**kwargs)
