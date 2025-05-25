from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
import logging
from typing import List, Optional, Dict, Any, Union

class FallbackProvider(LLMInterface):
    """Fallback provider when normal LLM providers are unavailable.
    
    This provider implements the LLMInterface but returns static responses
    instead of calling external APIs. It's used when the actual LLM
    service is unavailable or credentials are invalid.
    """
    
    def __init__(self, 
                 embedding_size: int = 1536,
                 fallback_message: str = "I'm currently experiencing technical difficulties connecting to my language model. Please check your API key configuration."):
        """Initialize the fallback provider.
        
        Args:
            embedding_size: Size of the fallback embedding vectors to generate
            fallback_message: Default message to return for generate_text calls
        """
        self.logger = logging.getLogger(__name__)
        self.embedding_size = embedding_size
        self.fallback_message = fallback_message
        self.generation_model_id = "fallback-model"
        self.embedding_model_id = "fallback-embeddings"
        self.enums = OpenAIEnums
        
    def set_generation_model(self, model_id: str) -> None:
        """Set the generation model ID (stored but not used).
        
        Args:
            model_id: The model ID to store
        """
        self.logger.info(f"Setting fallback generation model ID: {model_id}")
        self.generation_model_id = model_id
    
    def set_embedding_model(self, model_id: str, embedding_size: int) -> None:
        """Set the embedding model ID and size (stored but not used).
        
        Args:
            model_id: The model ID to store
            embedding_size: The embedding size to use for fallback vectors
        """
        self.logger.info(f"Setting fallback embedding model ID: {model_id}, size: {embedding_size}")
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def process_text(self, text: str) -> str:
        """Process text input (just returns the input).
        
        Args:
            text: The input text to process
            
        Returns:
            The processed text (unchanged in this implementation)
        """
        return text
    
    def generate_text(self, 
                      prompt: str, 
                      chat_history: List[Dict[str, str]] = None,
                      max_output_tokens: Optional[int] = None,
                      temperature: Optional[float] = None) -> str:
        """Generate text response (returns fallback message).
        
        Args:
            prompt: The input prompt
            chat_history: Optional chat history
            max_output_tokens: Maximum tokens to generate (ignored)
            temperature: Temperature parameter (ignored)
            
        Returns:
            The fallback message
        """
        self.logger.info(f"Fallback generate_text called with prompt: {prompt[:50]}...")
        return self.fallback_message
    
    def embed_text(self, text: str, document_type: Optional[str] = None) -> List[float]:
        """Generate embeddings (returns zero vector).
        
        Args:
            text: The text to embed
            document_type: Optional document type
            
        Returns:
            A zero vector of the configured embedding size
        """
        self.logger.info(f"Fallback embed_text called for text: {text[:50]}...")
        return [0.0] * self.embedding_size
    
    def construct_prompt(self, prompt: str, role: str) -> Dict[str, str]:
        """Construct a prompt object for the chat history.
        
        Args:
            prompt: The prompt text
            role: The role (system, user, or assistant)
            
        Returns:
            A dictionary with role and content keys
        """
        return {
            "role": role,
            "content": prompt,
        } 