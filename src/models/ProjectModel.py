from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger('uvicorn.error')

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        if self.db_client is not None:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            logger.info(f"ProjectModel initialized with collection: {self.collection.name}")
        else:
            logger.error("ProjectModel initialization failed: db_client is None")
            self.collection = None

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        if self.db_client is None:
            logger.error("Cannot initialize collection: db_client is None")
            return
            
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_project(self, project: Project):

        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id

        return project

    async def get_project_or_create_one(self, project_id_str: str) -> Optional[dict]:
        """Gets a project by its string ID, creating it if it doesn't exist."""
        # Check cache first (if implemented)
        # existing_project = self.cache.get(f"project:{project_id_str}")
        # if existing_project: 
        #    return existing_project

        if self.collection is None:
            logger.error(f"Cannot get or create project: collection is None (db_client may be unavailable)")
            return None

        try:
            # Find existing project
            project_data = await self.collection.find_one({"project_id": project_id_str})
            
            if project_data:
                logger.info(f"Found existing project with project_id: {project_id_str}")
                # Return the dict with the original ObjectId
                # self.cache.set(f"project:{project_id_str}", project_data)
                return project_data
            else:
                # Create new project if not found
                logger.info(f"Project with project_id '{project_id_str}' not found. Creating new project.")
                new_project_doc = {
                    "project_id": project_id_str,
                    "name": f"Project {project_id_str[:8]}", # Example name
                    # Add other default fields like created_at, etc.
                    "created_at": datetime.utcnow() 
                }
                insert_result = await self.collection.insert_one(new_project_doc)
                logger.info(f"Created new project. Inserted ID: {insert_result.inserted_id}")
                
                # Retrieve the newly created project to return consistent format
                created_project = await self.collection.find_one({"_id": insert_result.inserted_id})
                if created_project:
                    # Return the dict with the original ObjectId
                    # self.cache.set(f"project:{project_id_str}", created_project)
                    return created_project
                else:
                     logger.error(f"Failed to retrieve newly created project with id: {insert_result.inserted_id}")
                     return None

        except Exception as e:
            logger.exception(f"Error in get_project_or_create_one for project_id '{project_id_str}': {e}")
            return None

    async def get_all_projects(self, page: int=1, page_size: int=10):

        # count total number of documents
        total_documents = await self.collection.count_documents({})

        # calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find().skip( (page-1) * page_size ).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(
                Project(**document)
            )

        return projects, total_pages