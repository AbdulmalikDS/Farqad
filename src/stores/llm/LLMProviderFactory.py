from .LLMEnums import LLMEnums
from .providers.OpenAIProvider import OpenAIProvider
from .providers.CoHereProvider import CoHereProvider
import logging

class LLMProviderFactory:
    """Factory for creating LLM provider instances based on configuration.
    
    This factory creates and configures the appropriate LLM provider based on
    the application settings. It handles instantiation of OpenAI or Cohere
    providers with the correct configuration parameters.
    """
    
    def __init__(self, config: dict):
        """Initialize the factory with application settings.
        
        Args:
            config: Application configuration with LLM settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def create(self, provider: str):
        """Create and return an LLM provider instance.
        
        Args:
            provider: Provider type string (e.g., "openai", "cohere")
            
        Returns:
            An instance of the requested LLM provider or None if initialization fails
        """
        # Case-insensitive comparison for better reliability
        if provider.lower() == LLMEnums.OPENAI.value.lower():
            try:
                return OpenAIProvider(
                    api_key = self.config.LLM_API_KEY or self.config.openai_api_key,
                    api_url = self.config.openai_api_url,
                    default_input_max_characters = self.config.input_default_max_character,
                    default_generation_max_output_tokens = self.config.generation_default_max_tokens,
                    default_generation_temperature = self.config.generation_default_temperature
                )
            except Exception as e:
                self.logger.error(f"Error creating OpenAI provider: {str(e)}")
                return None

        if provider.lower() == LLMEnums.COHERE.value.lower():
            try:
                return CoHereProvider(
                    api_key = self.config.cohere_api_key,
                    default_input_max_characters = self.config.input_default_max_character,
                    default_generation_max_output_tokens = self.config.generation_default_max_tokens,
                    default_generation_temperature = self.config.generation_default_temperature
                )
            except Exception as e:
                self.logger.error(f"Error creating Cohere provider: {str(e)}")
                return None

        self.logger.error(f"Unsupported provider type: '{provider}'")
        return None
