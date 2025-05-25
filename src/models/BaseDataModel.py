from helpers.config import get_settings, Settings
import logging

logger = logging.getLogger('uvicorn.error')

class BaseDataModel:

    def __init__(self, db_client: object):
        self.db_client = db_client
        self.app_settings = get_settings()
        
        if self.db_client is None:
            logger.error("BaseDataModel initialized with None db_client - database operations will fail")
            

        
