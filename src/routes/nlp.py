from fastapi import FastAPI, APIRouter, status, Request, HTTPException
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
from models import ResponseSignal
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from bson import ObjectId
from langdetect import detect, LangDetectException

import logging

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
    )

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id # Pass positionally
    )
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found.")
    project_db_id = project.get('_id')

    # Get the app logger or create a default one
    app_logger = request.app.logger if hasattr(request.app, 'logger') else logger

    nlp_controller = NLPController(
        db_client=request.app.db_client,
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
        logger=app_logger
    )

    # Pass project_db_id string to controller
    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTOR_DB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id # Pass positionally
    )
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found.")
    project_db_id = project.get('_id')

    # Get the app logger or create a default one
    app_logger = request.app.logger if hasattr(request.app, 'logger') else logger

    nlp_controller = NLPController(
        db_client=request.app.db_client,
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
        logger=app_logger
    )

    # Pass project_id string and other params to controller
    results = nlp_controller.search_vector_db_collection(
        project_identifier_str=project_id, 
        query_text=search_request.text, 
        limit=search_request.limit
    )

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results": [ result.dict() if hasattr(result, 'dict') else result for result in results ]
        }
    )

class AnswerRAGRequest(BaseModel):
    """Request model for answering questions using RAG."""
    text: str = Field(..., description="The user's question text.")
    limit: int = Field(5, description="Maximum number of search results to retrieve.", ge=1, le=50)
    # Corrected type hint for Python 3.9
    file_id: Optional[str] = Field(None, description="Optional: The specific file_id (asset_id) to focus the answer on within the project.")
    conversation_history: Optional[List[Dict[str, str]]] = Field([], description="Optional: Previous conversation history for context")

class AnswerRAGResponse(BaseModel):
    """Response model for RAG answers."""
    signal: str
    answer: str
    full_prompt: str
    chat_history: list
    extracted_data_point: Optional[str] = None
    extracted_table_data: Optional[List[Dict[str, Any]]] = None

@nlp_router.post("/index/answer/{project_id_str}", response_model=AnswerRAGResponse)
async def answer_rag(request: Request, project_id_str: str, answer_rag_request: AnswerRAGRequest):
    """Answers a question based on indexed documents using RAG, for a specific project.

    Args:
        project_id_str: The string representation of the project ID.
        request: The request body containing the question text, limit, and optional file_id.

    Returns:
        An AnswerRAGResponse containing the generated answer.
    """
    logger.info(f"[/index/answer/{project_id_str}] CALLED. Request body: {answer_rag_request.dict()}")
    
    # Ensure dependencies are accessed from the request object, not the body model
    try:
        # Check if db_client is available
        if request.app.db_client is None:
            logger.error("Database client is not available - MongoDB connection may have failed during startup")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service is not available. Please try again later."
            )
            
        db_client = request.app.db_client
        project_model = ProjectModel(db_client=db_client)
        
        # Pass argument positionally
        project = await project_model.get_project_or_create_one(project_id_str)
        
        if project is None:
            logger.error(f"Project not found or could not be created for ID: {project_id_str} in answer_rag")
            # Return a proper HTTPException for FastAPI to handle CORS etc.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project context '{project_id_str}' not found.")
        
        # Access ID using dictionary key lookup, as 'project' is a dict
        project_db_id = project.get("_id") 
        if project_db_id is None:
            logger.error(f"Project dictionary missing '_id' after retrieval for project_id_str: {project_id_str}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Project record is missing ID after retrieval.")
        
        logger.info(f"Request for project_id_str: '{project_id_str}'. Found project with _id: '{project_db_id}'")

        # <<< ADD Language Detection and Setting >>>
        try:
            # Detect language from user question
            detected_lang = detect(answer_rag_request.text)
            logger.info(f"Detected language: {detected_lang}")
            # Set the language in the template parser for this request
            request.app.template_parser.set_language(detected_lang)
        except LangDetectException:
            logger.warning(f"Could not detect language for text: '{answer_rag_request.text[:50]}...'. Defaulting to '{request.app.template_parser.default_language}'.")
            request.app.template_parser.set_language(None) # Use default
        except Exception as lang_e: # Catch any other potential error during detection/setting
             logger.error(f"Error setting language: {lang_e}. Defaulting language.")
             request.app.template_parser.set_language(None) # Use default
        # <<< END Language Detection and Setting >>>

        # Initialize NLPController with dependencies
        app_logger = request.app.logger if hasattr(request.app, 'logger') else logging.getLogger('uvicorn.error')
        nlp_controller = NLPController(
            db_client=request.app.db_client, 
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            embedding_client=request.app.embedding_client,
            template_parser=request.app.template_parser,
            logger=app_logger
        )
        
        # Correctly access parameters from the request body model
        answer, full_prompt, chat_history, extracted_data, extracted_table = nlp_controller.answer_rag_question(
            project_identifier_str=project_id_str, # Use the ID string from the URL
            question=answer_rag_request.text,  # Access 'text' from body model
            file_id=answer_rag_request.file_id, # Access 'file_id' from body model
            conversation_history=answer_rag_request.conversation_history if hasattr(answer_rag_request, 'conversation_history') else []
        )

        # Handle case where answer_rag_question returns the "Cannot answer" message directly
        if full_prompt == "No RAG prompt generated.":
             # In this case, 'answer' holds the predefined message
             # We directly return it without raising 404, but maybe indicate differently?
             # For now, let's just return it as a successful response with the message.
             return AnswerRAGResponse(
                signal=ResponseSignal.RAG_ANSWER_SUCCESS.value, # Or a different signal?
                answer=answer,
                full_prompt=full_prompt,
                chat_history=chat_history,
                extracted_data_point=None, # No data extracted
                extracted_table_data=extracted_table
            )

        if answer is None:
            logger.warning(f"No answer generated by LLM for project {project_db_id}, file {answer_rag_request.file_id}, query '{answer_rag_request.text}'")
            # Return a proper HTTPException for FastAPI to handle CORS etc.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Could not generate an answer. No relevant documents found or an error occurred."
            )
        
        # Ensure this returns a dict or Pydantic model for automatic JSON conversion by FastAPI
        return AnswerRAGResponse(
            signal=ResponseSignal.RAG_ANSWER_SUCCESS.value,
            answer=answer,
            full_prompt=full_prompt if full_prompt is not None else "",
            chat_history=chat_history if chat_history is not None else [],
            extracted_data_point=extracted_data,
            extracted_table_data=extracted_table
        )
    except HTTPException:
        # Re-raise any HTTPExceptions we've already raised
        raise
    except Exception as e:
        # Get project ID safely for logging (if project was defined)
        project_id = "UNKNOWN"
        try:
            if 'project' in locals() and project is not None:
                project_id = project.get('_id', 'UNKNOWN')
        except:
            pass
            
        logger.exception(f"[NLP_ANSWER] CRITICAL UNHANDLED ERROR in /index/answer/{project_id_str}. Resolved DB ID: {project_id}. Error: {e}")
        # Raise HTTPException for FastAPI to handle response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            # Include project_id_str in the error detail for better debugging
            detail=f"Critical error during answer operation for project {project_id_str}: {str(e)}"
        )

class GeneralChatRequest(BaseModel):
    """Request model for general chat without RAG context."""
    text: str = Field(..., description="The user's message text.")
    conversation_history: Optional[List[Dict[str, str]]] = Field([], description="Optional: Previous conversation history for context")

class GeneralChatResponse(BaseModel):
    """Response model for general chat."""
    signal: str
    answer: str

@nlp_router.post("/general/answer", response_model=GeneralChatResponse)
async def general_chat(request: Request, chat_request: GeneralChatRequest):
    """Provides a general chat response without requiring document context.
    
    Args:
        chat_request: The request body containing the user's message.
        
    Returns:
        A GeneralChatResponse containing the generated answer.
    """
    logger.info(f"[/general/answer] CALLED. Request body: {chat_request.dict()}")
    
    try:
        # Detect language from user message
        try:
            detected_lang = detect(chat_request.text)
            logger.info(f"Detected language: {detected_lang}")
            request.app.template_parser.set_language(detected_lang)
        except Exception as lang_e:
            logger.warning(f"Language detection failed: {lang_e}. Using default.")
            request.app.template_parser.set_language(None)
        
        # Initialize NLPController with dependencies
        app_logger = request.app.logger if hasattr(request.app, 'logger') else logging.getLogger('uvicorn.error')
        nlp_controller = NLPController(
            db_client=request.app.db_client, 
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            embedding_client=request.app.embedding_client,
            template_parser=request.app.template_parser,
            logger=app_logger
        )
        
        # Get a direct answer from the generation client (LLM)
        # Extract conversation history from request if available
        conversation_history = getattr(chat_request, 'conversation_history', [])
        answer = nlp_controller.direct_llm_query(
            question=chat_request.text,
            conversation_history=conversation_history
        )
        
        if answer is None or answer == "":
            logger.warning("[/general/answer] direct_llm_query returned empty response")
            answer = "I'm sorry, I couldn't generate a response for your query. Please try asking something else."
        
        # Safeguard: If the answer is very short, it might be an error
        if len(answer) < 10:
            logger.warning(f"[/general/answer] Suspiciously short answer: '{answer}'")
            answer = f"{answer} (I apologize if this answer seems incomplete. Please try phrasing your question differently.)"
        
        return GeneralChatResponse(
            signal=ResponseSignal.GENERAL_CHAT_SUCCESS.value,
            answer=answer
        )
    
    except Exception as e:
        logger.exception(f"[GENERAL_CHAT] ERROR in /general/answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing general chat request: {str(e)}"
        )