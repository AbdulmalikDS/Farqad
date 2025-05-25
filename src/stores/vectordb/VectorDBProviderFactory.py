from .providers.QdrantDBProvider import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums, DistanceMethodEnums
from controllers.BaseController import BaseController
import logging

class VectorDBProviderFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        # Case-insensitive comparison to handle both "qdrant" and "QDRANT"
        if provider.lower() == VectorDBEnums.QDRANT.value.lower():
            db_path = self.base_controller.get_database_path(db_name=self.config.vector_db_path)
            
            # Log more information for debugging
            logger = logging.getLogger(__name__)
            logger.info(f"Initializing QdrantDBProvider with db_path: {db_path}")
            logger.info(f"VECTOR_DB_BACKEND config value: {provider}")
            
            # Use the correct constructor parameters to match QdrantDBProvider's __init__ method
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=DistanceMethodEnums.COSINE.value
            )
        else:
            raise ValueError(f"Unknown VectorDB provider: {provider}")