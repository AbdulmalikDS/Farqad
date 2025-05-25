from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List, Optional
from models.db_schemes.data_chunk import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, distance_method: str):

        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True
        
        return False
    
    def insert_one(self, collection_name: str, text: str, vector: list,
                   metadata: dict = None,
                   record_id: str = None):
        
        if not self.is_collection_existed(collection_name):
             self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
             return False
         
        try:
            # Ensure record_id is a single value, not a list
            if isinstance(record_id, list) and len(record_id) > 0:
                self.logger.warning(f"record_id was passed as a list: {record_id}, using first element")
                actual_id = record_id[0]
            else:
                actual_id = record_id
                
            self.logger.info(f"Inserting record with ID: {actual_id} into collection: {collection_name}")
            
            # Create point object
            point = models.PointStruct(
                id=actual_id,
                vector=vector,
                payload={"text": text}
            )
            
            # Add metadata if provided
            if metadata:
                point.payload.update(metadata)
                
            # Insert the point
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error inserting record: {str(e)}")
            return False

    def insert_many(self, collection_name: str, texts: str,
                    vectors: list, metadata: list = None,
                   record_ids: str = None, batch_size: int = 50):
        
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_text = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_records = [
                 models.Record(
                     id=batch_record_ids[x],
                     vector=batch_vectors[x],
                     payload={
                         "text": batch_text[x], "metadata": batch_metadata[x]
                     }
                 )

                for x in range(len(batch_text))
            ]
            try:
                _ = self.client.upload_records(
                collection_name=collection_name,
                records=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True
    
    def search_by_vector(self, collection_name: str, vector:list, limit: int = 5,
                           query_filter = None, score_threshold: Optional[float] = None):
        """ Search for vectors similar to the query vector, with optional filtering.

        Args:
            collection_name: Name of the collection to search in.
            vector: The query vector.
            limit: Max number of results to return.
            query_filter: Qdrant filter object (e.g., models.Filter).
            score_threshold: Minimum score threshold for results.
        """

        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                query_filter=query_filter,
                score_threshold=score_threshold,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            if not results or len(results) == 0:
                return None
            
            return [
                RetrievedDocument(**{
                    "score": result.score,
                    "text": result.payload["text"],    
                })
            for result in results
            ]
        except Exception as e:
            self.logger.error(f"Error in search_by_vector: {e}")
            return None