from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request, BackgroundTasks, HTTPException, Body
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController, NLPController
import aiofiles
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from models.enums.AssetTypeEnum import AssetTypeEnum
from helpers import utils
from bson.objectid import ObjectId
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
import tempfile

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
        
    
    project_model = ProjectModel(db_client=request.app.db_client)
    asset_model = AssetModel(db_client=request.app.db_client)

    # Get the project record, creating if necessary
    # Pass the argument positionally using the correct variable name from the route path
    project = await project_model.get_project_or_create_one(project_id)
    
    if project is None:
        logger.error(f"Failed to get or create project for ID: {project_id} in upload_data")
        raise HTTPException(status_code=500, detail="Failed to resolve project context")
    
    # Use the actual database ObjectId (or string representation) for consistency
    project_db_id_str = project.get("_id") # Assuming the method returns a dict
    if project_db_id_str is None:
         logger.error(f"Project dictionary missing '_id' field for project_id: {project_id}")
         raise HTTPException(status_code=500, detail="Project record is missing ID")

    # Generate a unique filename to avoid collisions
    unique_filename = f"{utils.generate_random_string()}_{file.filename}"

    # validate the file properties
    data_controller = DataController()

    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    # --- Start Synchronous Processing Logic --- 
    file_content_bytes = await file.read() # Read the entire file content into memory
    await file.seek(0) # Reset file pointer in case it's needed again (e.g., for saving)

    # Generate a temporary file path to use with Langchain loaders
    # Langchain loaders often work best with file paths
    file_ext = os.path.splitext(file.filename)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        temp_file.write(file_content_bytes)
        temp_file_path = temp_file.name
    logger.info(f"Saved uploaded content to temporary file: {temp_file_path}")

    if not is_valid:
        os.unlink(temp_file_path) # Clean up temp file
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )

    # Use the actual resolved project's ID string for path generation
    # Access the ID using dictionary lookup
    resolved_project_id_str = str(project["_id"]) 

    # project_dir_path = ProjectController().get_project_path(project_id=project_id) # Old way
    project_dir_path = ProjectController().get_project_path(project_id=resolved_project_id_str) # New way
    
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        # project_id=project_id # Old way
        project_id=resolved_project_id_str # New way
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    # store the assets into the database
    asset_resource = Asset(
        # Use dictionary lookup and convert to ObjectId
        asset_project_id=ObjectId(project["_id"]),
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=unique_filename, # Use the generated unique filename
        asset_size=os.path.getsize(file_path)
    )

    # --- Load content using LangChain loader --- 
    logger.info(f"Attempting to load content from temp file: {temp_file_path}")
    loader = None
    loaded_documents = None
    try:
        if file_ext == '.txt':
            loader = TextLoader(temp_file_path, encoding="utf-8")
        elif file_ext == '.pdf':
            loader = PyMuPDFLoader(temp_file_path)
        
        if loader:
            loaded_documents = loader.load()
            logger.info(f"Successfully loaded {len(loaded_documents)} document(s) from temp file using {type(loader).__name__}.")
        else:
            logger.warning(f"Unsupported file extension '{file_ext}' for temporary file based on {file.filename}. Skipping processing.")
            os.unlink(temp_file_path) # Clean up temp file
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
    except Exception as load_err:
        logger.error(f"Error loading file content from temp path {temp_file_path}: {load_err}", exc_info=True)
        os.unlink(temp_file_path) # Clean up temp file
        raise HTTPException(status_code=500, detail=f"Error processing file content: {load_err}")
    finally:
        # Ensure temp file is deleted even if loader fails later
        if os.path.exists(temp_file_path):
            logger.info(f"Cleaning up temporary file: {temp_file_path}")
            os.unlink(temp_file_path)

    if not loaded_documents:
        logger.error(f"Loaded_documents is empty or None after loading attempt for {file.filename}. Cannot proceed.")
        raise HTTPException(status_code=500, detail="Failed to load document content after successful upload.")

    # +++ Create the Asset record in DB BEFORE chunking/indexing +++
    asset_resource = await asset_model.create_asset(asset=asset_resource)
    if not asset_resource or not asset_resource.id:
        logger.error(f"Failed to create asset record in DB for file {unique_filename} or asset record has no ID.")
        raise HTTPException(status_code=500, detail="Failed to save file metadata to database.")
    logger.info(f"Asset record created in DB with ID: {asset_resource.id}")
    # +++ Asset record now exists with a valid ID +++

    # --- Chunking --- 
    # Use ProcessController just for its chunking logic (or move chunking logic here)
    process_controller = ProcessController(project_id=resolved_project_id_str) # Init with resolved ID
    # TODO: Get chunk/overlap size from config or request if needed
    chunk_size = 512 
    overlap_size = 64
    logger.info(f"Chunking content for {file.filename} (asset: {asset_resource.id}) using size={chunk_size}, overlap={overlap_size}")
    file_chunks = process_controller.process_file_content(
        file_content=loaded_documents, # Pass loaded LangChain documents
        file_id=str(asset_resource.id), # Pass asset_id for metadata
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )

    if file_chunks is None or not file_chunks:
        logger.error(f"No chunks generated for file: {file.filename}, asset_id: {asset_resource.id}. Skipping indexing.")
        # Decide if this should be an error response or just a warning
        raise HTTPException(status_code=500, detail="Failed to generate chunks from the document.")
    logger.info(f"Generated {len(file_chunks)} chunks for asset_id: {asset_resource.id}")

    # --- Save Chunks to DB --- 
    chunk_model = ChunkModel(db_client=request.app.db_client)
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=ObjectId(project["_id"]), # Use actual ObjectId
            chunk_asset_id=asset_resource.id # Use the asset ObjectId
        )
        for i, chunk in enumerate(file_chunks)
    ]
    inserted_count = await chunk_model.insert_many_chunks(chunks=file_chunks_records)
    logger.info(f"Inserted {inserted_count} chunks into DB for asset_id: {asset_resource.id}")
    # NOTE: The inserted_count confirms the number saved. 
    # The file_chunks_records list holds the objects (though their .id might not be populated yet by the driver).
    # We rely on NLPController.index_into_vector_db to handle the DataChunk objects directly.

    # --- Index Chunks into Vector DB --- 
    logger.info(f"Initiating indexing for {inserted_count} chunks of asset_id: {asset_resource.id}")
    nlp_controller = NLPController(
        db_client=request.app.db_client,
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
        logger=logger
    )
    try:
        # Note: We are resetting the collection for this specific project on *every* upload
        # This might not be desired if you want multiple files per project later.
        # Set do_reset=False if you want to add to existing collection.
        # For simplicity now, we reset to ensure only current file content is indexed.
        is_indexed = nlp_controller.index_into_vector_db(
            project_identifier_str=resolved_project_id_str, # Use the correct parameter name
            chunks=file_chunks_records, # Pass the chunk objects we created
            do_reset=True # Reset collection for this project on each upload (for now)
        )
        if is_indexed:
            logger.info(f"Successfully indexed {inserted_count} chunks for asset_id: {asset_resource.id}")
        else:
            logger.error(f"Indexing failed for asset_id: {asset_resource.id}")
            raise HTTPException(status_code=500, detail="Failed to index document chunks.")
    except Exception as index_err:
        logger.error(f"Error during indexing for asset_id {asset_resource.id}: {index_err}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error indexing document: {index_err}")

    # --- End Synchronous Processing Logic ---

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_resource.id),
                "project_id": str(project["_id"])
            }
        )

@data_router.delete("/document/{document_id}")
async def delete_document(document_id: str, request: Request, project_data: dict = Body(...)):
    """Delete a document from a project."""
    try:
        project_id = project_data.get("project_id")
        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")
            
        app = request.app
        if not app.db_client:
            raise HTTPException(status_code=503, detail="Database connection is not available")
            
        # Get the document collection
        documents = app.db_client.get_collection("documents")
        
        # Check if document exists
        document = await documents.find_one({"_id": document_id, "project_id": project_id})
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found in project {project_id}")
        
        # Delete document from MongoDB
        delete_result = await documents.delete_one({"_id": document_id, "project_id": project_id})
        
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found or could not be deleted")
            
        # Delete document from vector database if configured
        if app.vectordb_client:
            try:
                # Use the document ID as the collection name
                app.vectordb_client.delete_collection(document_id)
                logger.info(f"Deleted document collection {document_id} from vector database")
            except Exception as e:
                logger.error(f"Failed to delete document from vector database: {str(e)}")
                # We continue even if vector DB deletion fails
        
        # Return success response
        return {"message": f"Document {document_id} deleted successfully", "document_id": document_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
