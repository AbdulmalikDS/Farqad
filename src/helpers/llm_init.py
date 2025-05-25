"""Utilities for initializing LLM providers."""

import logging
from typing import Tuple, Any, Optional
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.llm.providers.FallbackProvider import FallbackProvider

logger = logging.getLogger(__name__)

def initialize_llm_providers(
    settings: Any,
    llm_provider_factory: LLMProviderFactory
) -> Tuple[Any, Any]:
    """Initialize generation and embedding clients with proper fallbacks.
    
    Args:
        settings: Application settings
        llm_provider_factory: Factory for creating LLM providers
        
    Returns:
        Tuple of (generation_client, embedding_client)
    """
    # Initialize generation client
    generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    if generation_client:
        generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
        logger.info(f"Generation client initialized with {settings.GENERATION_BACKEND}")
    else:
        logger.warning("Generation client initialization failed, using fallback provider")
        generation_client = FallbackProvider(
            fallback_message="I'm sorry, I couldn't process your request. Please ensure your OpenAI API key is correctly configured."
        )
        generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Initialize embedding client
    embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    if embedding_client:
        embedding_client.set_embedding_model(
            model_id=settings.EMBEDDING_MODEL_ID,
            embedding_size=settings.EMBEDDING_MODEL_SIZE
        )
        logger.info(f"Embedding client initialized with {settings.EMBEDDING_BACKEND}")
    else:
        logger.warning("Embedding client initialization failed, using fallback provider")
        embedding_client = FallbackProvider(embedding_size=settings.EMBEDDING_MODEL_SIZE)
        embedding_client.set_embedding_model(
            model_id=settings.EMBEDDING_MODEL_ID,
            embedding_size=settings.EMBEDDING_MODEL_SIZE
        )
        
    return generation_client, embedding_client

def create_fallback_providers(
    settings: Any
) -> Tuple[FallbackProvider, FallbackProvider]:
    """Create fallback providers when regular initialization fails.
    
    Args:
        settings: Application settings
        
    Returns:
        Tuple of (generation_client, embedding_client) as fallback providers
    """
    generation_client = FallbackProvider(
        fallback_message="I'm sorry, I couldn't process your request due to a technical issue. Please try again later."
    )
    generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    
    embedding_client = FallbackProvider(embedding_size=settings.EMBEDDING_MODEL_SIZE)
    embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID, 
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )
    
    return generation_client, embedding_client 