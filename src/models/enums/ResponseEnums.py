from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "file_validated_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    PROCESSING_FAILED = "processing_failed"
    PROCESSING_SUCCESS = "processing_success"
    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR = "no_file_found_with_this_id"
    PROJECT_NOT_FOUND = "project_not_found"
    INSERT_INTO_VECTORDB_ERROR= "insert_into_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS= "insert_into_vectordb_success"
    VECTOR_DB_COLLECTION_RETRIEVED = "vector_db_collection_retrieved"
    VECTORDB_SEARCH_ERROR = "search_vectordb_error"
    VECTORDB_SEARCH_SUCCESS = "search_vectordb_success"
    RAG_ANSWER_SUCCESS = "rag_answer_success"
    RAG_ANSWER_ERROR = "rag_answer_error"
    PROCESSING_STARTED = "processing_started"
    GENERAL_CHAT_SUCCESS = "general_chat_success"
    