from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum
import logging
import sys
from langchain.docstore.document import Document

class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)
        self.logger = logging.getLogger(__name__)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):

        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )

        self.logger.info(f"[ProcessController.get_file_loader] Checking for file existence at path: {file_path}")
        
        try:
            encoded_path = file_path.encode(sys.getfilesystemencoding(), errors='surrogateescape')
            exists = os.path.exists(encoded_path)
            self.logger.info(f"[ProcessController.get_file_loader] os.path.exists check using encoded path ({sys.getfilesystemencoding()}) returned: {exists}")
        except Exception as encode_err:
            self.logger.warning(f"[ProcessController.get_file_loader] Failed to encode/check path: {encode_err}. Falling back to original path check.")
            exists = os.path.exists(file_path) # Fallback
            self.logger.info(f"[ProcessController.get_file_loader] os.path.exists check using original path returned: {exists}")

        if not exists:
            self.logger.error(f"[ProcessController.get_file_loader] File confirmed NOT FOUND at path: {file_path}")
            return None

        if file_ext == ProcessingEnum.TXT.value:
            # Use encoded path if exists check passed with it, otherwise fallback to original
            loader_path = encoded_path if 'encoded_path' in locals() and exists else file_path
            return TextLoader(loader_path, encoding="utf-8")

        if file_ext == ProcessingEnum.PDF.value:
            # Use encoded path if exists check passed with it, otherwise fallback to original
            loader_path = encoded_path if 'encoded_path' in locals() and exists else file_path
            return PyMuPDFLoader(loader_path)
        
        return None

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()

        return None

    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int=100, overlap_size: int=20):
        """
        Process file content into chunks for indexing
        
        Args:
            file_content: List of Document objects
            file_id: File identifier
            chunk_size: Size of each chunk
            overlap_size: Overlap between chunks
            
        Returns:
            List of chunked documents
        """
        # Log chunk parameters
        self.logger.info(f"Chunking file {file_id} with chunk_size={chunk_size}, overlap_size={overlap_size}")
        self.logger.info(f"Input file_content has {len(file_content)} documents")
        
        # Safety check - ensure we have content to process
        if not file_content or len(file_content) == 0:
            self.logger.error(f"No content to process for file_id: {file_id}")
            return []
        
        # Create text splitter with more robust settings
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
            separators=["\n\n", "\n", " ", ""] # Try different separators
        )

        try:
            # Extract text and metadata from documents
            file_content_texts = []
            file_content_metadata = []
            
            for rec in file_content:
                # Skip empty documents
                if not rec.page_content or len(rec.page_content.strip()) == 0:
                    continue
                    
                file_content_texts.append(rec.page_content)
                
                # Ensure metadata includes page info for traceability
                metadata = rec.metadata.copy() if hasattr(rec, 'metadata') and rec.metadata else {}
                if not metadata.get('source') and hasattr(rec, 'metadata') and rec.metadata.get('source'):
                    metadata['source'] = rec.metadata.get('source')
                if not metadata.get('page') and hasattr(rec, 'metadata') and rec.metadata.get('page'):
                    metadata['page'] = rec.metadata.get('page')
                
                file_content_metadata.append(metadata)
            
            self.logger.info(f"Prepared {len(file_content_texts)} non-empty documents for chunking")
            
            # Handle empty content
            if not file_content_texts:
                # Create at least one default chunk so we don't fail completely
                self.logger.warning(f"No valid text content found in file_id: {file_id}, creating fallback chunk")
                default_chunk = Document(
                    page_content="[This document appears to contain no extractable text content]",
                    metadata={"source": file_id, "empty_content": True}
                )
                return [default_chunk]
            
            # Create chunks
            chunks = text_splitter.create_documents(
                file_content_texts,
                metadatas=file_content_metadata
            )
            
            # Handle case where chunking produced no results
            if not chunks or len(chunks) == 0:
                self.logger.warning(f"Chunking produced no results for file_id: {file_id}, trying larger chunk size")
                
                # Try again with larger chunk size
                large_text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size * 2,  # Double chunk size
                    chunk_overlap=overlap_size,
                    length_function=len,
                )
                
                chunks = large_text_splitter.create_documents(
                    file_content_texts,
                    metadatas=file_content_metadata
                )
                
                # If still no chunks, create one chunk per page
                if not chunks or len(chunks) == 0:
                    self.logger.warning(f"Still no chunks with larger size for file_id: {file_id}, creating one chunk per page")
                    chunks = []
                    for i, (text, metadata) in enumerate(zip(file_content_texts, file_content_metadata)):
                        chunks.append(Document(
                            page_content=text,
                            metadata=metadata
                        ))
            
            self.logger.info(f"Successfully created {len(chunks)} chunks for file_id: {file_id}")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error during chunking for file_id: {file_id}: {str(e)}", exc_info=True)
            
            # Create fallback chunks - one per page to avoid complete failure
            self.logger.warning(f"Creating fallback chunks (one per page) for file_id: {file_id}")
            fallback_chunks = []
            
            for i, rec in enumerate(file_content):
                if not rec.page_content or len(rec.page_content.strip()) == 0:
                    continue
                    
                # Create one chunk per page
                metadata = rec.metadata.copy() if hasattr(rec, 'metadata') and rec.metadata else {}
                metadata['fallback_chunk'] = True
                metadata['original_page'] = i
                
                fallback_chunks.append(Document(
                    page_content=rec.page_content,
                    metadata=metadata
                ))
            
            # If we still have no chunks, create one default chunk
            if not fallback_chunks:
                self.logger.warning(f"No content available for fallback chunks in file_id: {file_id}, creating default chunk")
                fallback_chunks = [Document(
                    page_content="[This document could not be processed properly]",
                    metadata={"source": file_id, "processing_error": True}
                )]
            
            self.logger.info(f"Created {len(fallback_chunks)} fallback chunks for file_id: {file_id}")
            return fallback_chunks


    