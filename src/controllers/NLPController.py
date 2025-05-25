from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List, Optional
import json
import logging
from qdrant_client.http import models as rest_models
import uuid
import re # Import regular expression module

class NLPController(BaseController):

    def __init__(self, db_client, vectordb_client, generation_client, 
                 embedding_client, template_parser, logger):
        super().__init__()
        self.logger = logger

        # Store all dependencies
        self.db_client = db_client
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    def index_into_vector_db(self, project_identifier_str: str, chunks: List[DataChunk],
                                   do_reset: bool = False):
        
        self.logger.info(f"[NLPController.index_into_vector_db] Called for project_identifier_str {project_identifier_str}. Number of chunks: {len(chunks)}")
        # step1: get collection name using the provided ID
        collection_name = self.create_collection_name(project_id=project_identifier_str)

        # step2: manage items
        texts = []
        metadata_list = []
        for chunk in chunks:
            texts.append(chunk.chunk_text)
            # Ensure metadata includes the asset_id
            current_chunk_meta = chunk.chunk_metadata.copy() # Start with original loader metadata
            current_chunk_meta['asset_id'] = str(chunk.chunk_asset_id) # Add the asset_id (as string)
            metadata_list.append(current_chunk_meta) # Append to the correctly named list
        
        # Re-enable original embedding code:
        vectors = [
            self.embedding_client.embed_text(text=text, 
                                             document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]
        self.logger.info(f"[NLPController.index_into_vector_db] Generated embeddings. Example vector length: {len(vectors[0]) if vectors else 'N/A'}")

        # step3: create collection if not exists
        self.logger.info(f"[NLPController.index_into_vector_db] Attempting to create/ensure collection: {collection_name}")
        collection_created_or_exists = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # step4: insert into vector db
        # Extract ObjectIds from the chunk objects and generate UUIDs for Qdrant
        record_ids_uuid = [str(uuid.uuid4()) for chunk in chunks]
        self.logger.info(f"[NLPController.index_into_vector_db] Generated UUIDs for Qdrant records. Example: {record_ids_uuid[0] if record_ids_uuid else 'N/A'}")

        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata_list, # Use the list with asset_id included
            vectors=vectors,
            record_ids=record_ids_uuid, # Use the generated UUID list
        )

        return True

    def search_vector_db_collection(
        self,
        project_identifier_str: str,
        query_text: str,
        limit: int = 5,
        file_id: Optional[str] = None,
        score_threshold: Optional[float] = None,
    ) -> list[dict]:
        """Searches the vector DB for a given project and query, optionally filtering by file_id."""
        self.logger.info(
            f"[NLPController.search_vector_db_collection] Searching project {project_identifier_str} "
            f"for '{query_text[:50]}...', limit: {limit}, file_id: {file_id}, threshold: {score_threshold}"
        )

        # Use the embed_text method, consistent with indexing logic (assuming single text input)
        query_embedding = self.embedding_client.embed_text(text=query_text)
        # Note: Ensure embed_text returns the embedding directly for a single text input.
        # If it expects a list and returns a list, adjust accordingly:
        # query_embedding = self.embedding_client.embed_text(texts=[query_text])[0] # If it needs list input

        # Prepare the filter for Qdrant if file_id is provided
        # This assumes the metadata field in Qdrant is named 'file_id' or 'asset_id'
        # We need to ensure this matches what's used during indexing.
        # Let's assume it's 'asset_id' as per ChunkSchema.
        query_filter = None
        # <<< TEMPORARILY COMMENT OUT FILTER LOGIC FOR OPTION A >>>
        # if file_id:
        #     query_filter = rest_models.Filter(
        #         must=[
        #             rest_models.FieldCondition(
        #                 key="asset_id",
        #                 match=rest_models.MatchValue(value=file_id),
        #             )
        #         ]
        #     )
        #     self.logger.info(f"Applying Qdrant filter for asset_id: {file_id}")
        self.logger.warning("TEMPORARILY DISABLED asset_id FILTERING for Option A testing.")
        # <<< END TEMPORARY COMMENT OUT >>>

        try:
            # Perform the search with the filter enabled again
            # self.logger.info("DEBUG: About to call search_by_vector...") # REMOVE Log before call
            results = self.vectordb_client.search_by_vector(
                collection_name=f"collection_{project_identifier_str}",
                vector=query_embedding,
                limit=limit,
                query_filter=query_filter, # Use the filter again
                score_threshold=score_threshold,
            )
            # self.logger.info(f"DEBUG: search_by_vector returned. Type: {type(results)}") # REMOVE Log right after call

            # Handle case where the underlying client search returns None
            if results is None:
                self.logger.info("VectorDB search returned None (no results found).")
                return [] # Return empty list if no results
                
            self.logger.info(f"VectorDB search returned {len(results)} results.")

            # Convert search results (RetrievedDocument) to the expected dictionary structure
            processed_results = []
            # self.logger.info("DEBUG: About to process results in list comprehension...") # REMOVE Log before processing
            for hit in results:
                try:
                    # Adjust to use available attributes: score, text
                    processed_results.append({
                        # "id": hit.id, # ID is not available in RetrievedDocument
                        "score": hit.score,
                        "text": hit.text, # Directly access text
                        "metadata": {}, # Metadata is not available in RetrievedDocument
                    })
                except AttributeError as ae:
                    # Keep this specific logging in case the structure changes again
                    self.logger.error(f"AttributeError processing hit: {ae}")
                    self.logger.error(f"Problematic hit type: {type(hit)}")
                    self.logger.error(f"Problematic hit attributes: {dir(hit)}")
                    try:
                        self.logger.error(f"Problematic hit object: {hit}")
                    except Exception as log_e:
                         self.logger.warning(f"Could not log the full problematic hit object: {log_e}")
                    # Don't re-raise, just skip the problematic hit for now
                    # raise ae 
            return processed_results

        except Exception as e:
            self.logger.error(f"Error during VectorDB search for project {project_identifier_str}: {e}", exc_info=True)
            # Depending on the Qdrant client, specific exceptions like ValueError for collection not found might be raised.
            # Handle gracefully or re-raise as appropriate.
            # For now, return empty list if search fails.
            if "Collection" in str(e) and "not found" in str(e):
                 self.logger.warning(f"Collection collection_{project_identifier_str} not found during search.")
            return [] # Return empty list on exception
    
    def answer_rag_question(
        self,
        project_identifier_str: str,
        question: str,
        file_id: Optional[str] = None,
        conversation_history: list = None,
    ) -> tuple[str, str, list, Optional[str], Optional[list[dict]]]:
        """Answers a question using RAG, optionally filtering by file_id.
        
        Args:
            project_identifier_str: The project identifier.
            question: The user's question.
            file_id: Optional file ID to limit search to.
            conversation_history: Optional list of previous message objects with 'role' and 'content'.
            
        Returns:
            A tuple of (answer_text, full_prompt, chat_history, extracted_data, extracted_table)
        """
        self.logger.info(
            f"[NLPController.answer_rag_question] Called for project_identifier_str: {project_identifier_str}, "
            f"question: '{question[:50]}...', file_id: {file_id}, history_len: {len(conversation_history) if conversation_history else 0}"
        )

        # 1. Retrieve relevant documents from VectorDB
        retrieved_documents = self.search_vector_db_collection(
            project_identifier_str=project_identifier_str,
            query_text=question,
            limit=5, 
            file_id=file_id
        )

        self.logger.info(f"Retrieved {len(retrieved_documents)} documents from vector search.")

        if not retrieved_documents or len(retrieved_documents) == 0:
            self.logger.warning(f"No relevant documents found in vector DB for project {project_identifier_str}, file {file_id}, query '{question[:50]}...'")
            answer = "I couldn't find relevant information in the uploaded documents to answer that question. I can only answer based on the content you provide."
            return answer, "No RAG prompt generated.", [], None, None # MODIFIED: Add None for table_data
        
        # step2: Construct LLM prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")
        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": doc["text"],
            })
            for idx, doc in enumerate(retrieved_documents)
        ])
        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": question
        })

        # Log the constructed prompts for debugging
        self.logger.info(f"System prompt: {system_prompt[:100]}...")
        self.logger.info(f"Documents prompt length: {len(documents_prompts)}")
        self.logger.info(f"Footer prompt: {footer_prompt[:100]}...")

        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        # Add conversation history if provided
        if conversation_history and isinstance(conversation_history, list):
            self.logger.info(f"[NLPController.answer_rag_question] Adding {len(conversation_history)} messages from conversation history")
            for msg in conversation_history:
                if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                    continue
                role = self.generation_client.enums.USER.value
                if msg['role'] == 'assistant':
                    role = self.generation_client.enums.ASSISTANT.value
                chat_history.append(
                    self.generation_client.construct_prompt(
                        prompt=msg['content'],
                        role=role
                    )
                )

        # Join the documents and footer prompts with double newlines
        full_prompt = "\n\n".join([documents_prompts, footer_prompt])

        # Add fallback mechanism in case template loading fails
        if not system_prompt or not documents_prompts or not footer_prompt:
            self.logger.error("Critical error: Failed to load one or more required templates")
            fallback_system = """You are a helpful assistant that analyzes documents and answers questions based on their content."""
            fallback_prompt = f"""
            I have a question about these documents: {question}
            
            Here are the relevant document chunks:
            {chr(10).join([doc["text"] for doc in retrieved_documents])}
            
            Please answer my question based only on this information.
            """
            chat_history = [
                self.generation_client.construct_prompt(
                    prompt=fallback_system,
                    role=self.generation_client.enums.SYSTEM.value,
                )
            ]
            full_prompt = fallback_prompt
            self.logger.warning("Using fallback prompts due to template loading failure")

        # step4: Retrieve the Answer
        try:
            answer_text = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

            if not answer_text or answer_text.strip() == "":
                self.logger.error("LLM returned empty response")
                answer_text = "I processed your request but encountered an issue generating a response. Please try rephrasing your question."
        except Exception as e:
            self.logger.error(f"Error generating response from LLM: {str(e)}")
            answer_text = f"I'm sorry, I encountered an error while processing your request: {str(e)}"

        # Parse single numerical data from <extracted_data> tag
        extracted_numerical_data = None
        if answer_text:
            # Regex for <extracted_data>VALUE</extracted_data>
            # It looks for patterns like: "is $X", "is X", "are: X", "figure is X", "Income: $X"
            # It tries to capture the number, stripping common currency symbols and commas.
            # MODIFIED Regex to be simpler and target the tag directly
            match_single_data = re.search(r"<extracted_data>(.*?)<\/extracted_data>", answer_text)
            if match_single_data:
                try:
                    num_str_cleaned = match_single_data.group(1).replace(",", "")
                    if "." in num_str_cleaned:
                        extracted_numerical_data = str(float(num_str_cleaned))
                    else:
                        extracted_numerical_data = str(int(num_str_cleaned))
                    self.logger.info(f"Extracted single numerical data: {extracted_numerical_data}")
                except ValueError:
                    self.logger.warning(f"Could not convert extracted data to number: {match_single_data.group(1)}")

        # Parse structured table data from <table_data> tag
        extracted_table_data = None
        if answer_text:
            # <<< Log the raw answer text before attempting regex >>>
            self.logger.info(f"Attempting to find table_data tag in raw answer_text: '{answer_text}'")
            # <<< End Log >>>

            # MODIFIED Regex: Allow whitespace around tags, case-insensitive, dot matches newline
            table_match = re.search(r"<table_data\s*>\s*(.*?)\s*<\/table_data\s*>", 
                                  answer_text, re.DOTALL | re.IGNORECASE)
            if table_match:
                table_json_str = table_match.group(1)
                self.logger.info(f"Regex Matched! Extracted table_json_str: '{table_json_str}'") # LOG 1
                try:
                    parsed_json = json.loads(table_json_str)
                    if isinstance(parsed_json, list):
                        extracted_table_data = parsed_json
                        self.logger.info(f"Successfully parsed <table_data> JSON: {extracted_table_data}") # LOG 2
                    else:
                        self.logger.warning(f"<table_data> content was valid JSON but not a list: {type(parsed_json)}") # LOG 3
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to decode JSON from <table_data>: {e}. Content snippet: '{table_json_str[:500]}...'") # LOG 4
            else:
                self.logger.info("No <table_data> tag found by regex.") # LOG 5

        # Return answer, prompt, history, extracted single numerical data, and extracted table data
        return answer_text, full_prompt, chat_history, extracted_numerical_data, extracted_table_data # MODIFIED
        
    def direct_llm_query(self, question: str, conversation_history: list = None) -> str:
        """Sends a direct query to the LLM without using RAG context.
        
        Args:
            question: The user's question or message.
            conversation_history: Optional list of previous message objects with 'role' and 'content'.
            
        Returns:
            The generated response from the LLM.
        """
        self.logger.info(f"[NLPController.direct_llm_query] Processing query: '{question[:50]}...'")
        
        try:
            # Construct a system prompt for general chat
            system_prompt = self.template_parser.get("general", "system_prompt", fallback="You are a helpful financial assistant that provides clear and concise answers.")
            self.logger.info(f"[NLPController.direct_llm_query] Using system prompt: '{system_prompt[:50]}...'")
            
            # Create chat history with system prompt
            chat_history = [
                self.generation_client.construct_prompt(
                    prompt=system_prompt,
                    role=self.generation_client.enums.SYSTEM.value,
                )
            ]
            
            # Add conversation history if provided
            if conversation_history and isinstance(conversation_history, list):
                self.logger.info(f"[NLPController.direct_llm_query] Adding {len(conversation_history)} messages from conversation history")
                
                for msg in conversation_history:
                    if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                        continue
                        
                    # Map role from frontend to LLM client roles
                    role = self.generation_client.enums.USER.value
                    if msg['role'] == 'assistant':
                        role = self.generation_client.enums.ASSISTANT.value
                        
                    chat_history.append(
                        self.generation_client.construct_prompt(
                            prompt=msg['content'],
                            role=role
                        )
                    )
            
            # Generate response directly from the LLM
            self.logger.info(f"[NLPController.direct_llm_query] Calling generation_client.generate_text with {len(chat_history)} messages in history")
            response = self.generation_client.generate_text(
                prompt=question,
                chat_history=chat_history
            )
            
            if not response:
                self.logger.warning(f"[NLPController.direct_llm_query] LLM returned empty response for query: '{question[:50]}...'")
                return "I'm sorry, I couldn't generate a response for your query. Please try asking a different question."
            
            self.logger.info(f"[NLPController.direct_llm_query] Generated response: '{response[:50]}...'")
            return response
            
        except Exception as e:
            self.logger.error(f"[NLPController.direct_llm_query] Error in direct_llm_query: {e}", exc_info=True)
            return "I encountered an error while processing your request. Please try again with a simpler question or check back later." 