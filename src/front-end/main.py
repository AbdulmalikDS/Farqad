from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, UploadFile, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, User, Individual, Admin, Organization, engine, Base
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uuid
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import logging
from contextlib import asynccontextmanager  # Add this import for lifespan
import requests
import httpx
import time
from urllib.parse import urljoin
from config import PORT, HOST
import auth
from auth import router as auth_router

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create in-memory document store
document_store = {
    # Project ID -> list of documents
}

# Add stc.pdf as a special document that's always available
def ensure_stc_document(project_id):
    if project_id not in document_store:
        document_store[project_id] = []
    
    # Check if stc.pdf is already in the list
    stc_exists = any(doc.get("id") == "stc-doc-12345" for doc in document_store[project_id])
    
    # Add stc.pdf if it doesn't exist
    if not stc_exists:
        stc_doc = {
            "id": "stc-doc-12345",
            "filename": "stc.pdf",
            "size": "1.2 MB",
            "date": "Today"
        }
        document_store[project_id].append(stc_doc)
    
    return document_store[project_id]

# Define lifespan context manager (modern replacement for on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables
    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    yield  # This is where the app runs
    
    # Shutdown: Clean up resources if needed
    # No cleanup needed in this case

# Create the FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Include the auth router
app.include_router(auth_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers
)

# Add middleware to prevent caching during development
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Check if it's a static file request
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    
    return response

SECRET_KEY = '9231c9496752f3887965250eeda37e544232680d0b23a760b8caa8d9112d9618'
ALGORITHM = 'HS256'
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/login')

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates setup for HTML rendering
templates = Jinja2Templates(directory=".")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class AdminRegisterRequest(BaseModel):
    adminname: str
    email: str
    password: str

class OrgRegisterRequest(BaseModel):
    org_name: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    userID: str
    name: str
    email: str

# HTML Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/login.html", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register.html", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/chatpage.html", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chatpage.html", {"request": request})

@app.get("/admin_login.html", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.get("/admin_register.html", response_class=HTMLResponse)
async def admin_register_page(request: Request):
    return templates.TemplateResponse("admin_register.html", {"request": request})

@app.get("/org_login.html", response_class=HTMLResponse)
async def org_login_page(request: Request):
    return templates.TemplateResponse("org_login.html", {"request": request})

@app.get("/org_register.html", response_class=HTMLResponse)
async def org_register_page(request: Request):
    return templates.TemplateResponse("org_register.html", {"request": request})

@app.get("/main.html", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/admin_dashboard.html", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

# Individual User API Endpoints
@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    print("Register endpoint called")
    if db.query(User).filter((User.email == request.email) | (User.name == request.name)).first():
        raise HTTPException(status_code=400, detail="User with this email or name already exists")
    user = Individual(
        userID=str(uuid.uuid4()),
        name=request.name,
        email=request.email,
        password=bcrypt_context.hash(request.password),
        type='individual'
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}

@app.post("/api/login")
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        # Parse the JSON body from the request
        form_data = await request.json()
        print(f"Login attempt for: {form_data.get('email')}")
        
        # Find the user by email
        user = db.query(User).filter(User.email == form_data.get("email")).first()
        
        # Validate password
        if not user or not bcrypt_context.verify(form_data.get("password"), user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create and return token
        token = create_access_token(user.email, user.userID)
        return {"token": token, "username": user.name}
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

# Admin API Endpoints
@app.post("/api/admin/register", status_code=status.HTTP_201_CREATED)
def admin_register(request: AdminRegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    admin = Admin(
        userID=str(uuid.uuid4()),
        name=request.adminname,
        email=request.email,
        password=bcrypt_context.hash(request.password),
        type='admin'
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return {"message": "Admin registered successfully"}

@app.post("/api/admin/login")
async def admin_login(request: Request, db: Session = Depends(get_db)):
    try:
        # Parse the JSON body from the request
        form_data = await request.json()
        print(f"Admin login attempt for: {form_data.get('email')}")
        
        # Find the admin by email
        admin = db.query(Admin).filter(Admin.email == form_data.get("email")).first()
        
        # Validate password
        if not admin or not bcrypt_context.verify(form_data.get("password"), admin.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create and return token
        token = create_access_token(admin.email, admin.userID)
        return {"token": token, "adminname": admin.name}
    except Exception as e:
        print(f"Admin login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

# Organization API Endpoints
@app.post("/api/org/register", status_code=status.HTTP_201_CREATED)
def org_register(request: OrgRegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    org = Organization(
        userID=str(uuid.uuid4()),
        name=request.org_name,
        email=request.email,
        password=bcrypt_context.hash(request.password),
        type='organization',
        organizationName=request.org_name,
        organizationEmail=request.email
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return {"message": "Organization registered successfully"}

@app.post("/api/org/login")
async def org_login(request: Request, db: Session = Depends(get_db)):
    try:
        # Parse the JSON body from the request
        form_data = await request.json()
        print(f"Organization login attempt for: {form_data.get('email')}")
        
        # Find the organization by email
        org = db.query(Organization).filter(Organization.email == form_data.get("email")).first()
        
        # Validate password
        if not org or not bcrypt_context.verify(form_data.get("password"), org.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create and return token
        token = create_access_token(org.email, org.userID)
        return {"access_token": token, "org_name": org.name}
    except Exception as e:
        print(f"Organization login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

def create_access_token(email: str, userID: str):
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode = {"sub": email, "id": userID, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        userID: str = payload.get("id")
        if email is None or userID is None:
            raise HTTPException(status_code=401, detail="Could not validate user")
        return {"email": email, "userID": userID}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate user")

@app.get("/api/user", response_model=UserResponse)
def get_user(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userID == current_user["userID"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(userID=user.userID, name=user.name, email=user.email)

# Admin dashboard API endpoints
@app.get("/api/admin/stats")
def get_admin_stats():
    """
    Get statistics for admin dashboard
    """
    try:
        # Create database session
        db = SessionLocal()
        
        # Get counts from database
        total_users = db.query(Individual).count()
        total_orgs = db.query(Organization).count()
        total_admins = db.query(Admin).count()
        
        # For demo purposes, generate some random stats
        import random
        # Current date for consistent random values
        from datetime import datetime, timedelta
        
        today = datetime.now()
        
        # Generate daily stats for the last 7 days
        daily_stats = []
        for i in range(7):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Generate random but consistent daily stats
            seed = int(date.strftime("%Y%m%d"))
            random.seed(seed)
            
            daily_stats.append({
                "date": date_str,
                "new_users": random.randint(1, 10),
                "chats": random.randint(10, 50),
                "documents": random.randint(5, 20),
                "active_users": random.randint(10, total_users + total_orgs)
            })
        
        # Recent activities (normally would come from a log or activity table)
        recent_activities = [
            {"type": "login", "user": "John Doe", "time": "5 minutes ago"},
            {"type": "document", "user": "Acme Corp", "time": "15 minutes ago"},
            {"type": "chat", "user": "Jane Smith", "time": "30 minutes ago"},
            {"type": "signup", "user": "New User", "time": "1 hour ago"},
            {"type": "login", "user": "Admin", "time": "2 hours ago"}
        ]
        
        # Return statistics
        return {
            "total_users": total_users,
            "total_organizations": total_orgs,
            "total_admins": total_admins,
            "total_accounts": total_users + total_orgs + total_admins,
            "chats_today": daily_stats[0]["chats"],
            "documents_processed": sum(day["documents"] for day in daily_stats),
            "avg_response_time": round(random.uniform(0.8, 2.5), 1),
            "daily_stats": daily_stats,
            "recent_activities": recent_activities,
            "active_users": [
                {"name": "John Doe", "type": "Individual", "status": "active"},
                {"name": "Acme Corp", "type": "Organization", "status": "active"},
                {"name": "Jane Smith", "type": "Individual", "status": "active"},
                {"name": "Tech Solutions", "type": "Organization", "status": "inactive"},
                {"name": "Mike Johnson", "type": "Individual", "status": "active"}
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching admin stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching admin stats: {str(e)}")
    finally:
        db.close()

# File upload proxy endpoint
@app.post("/api/v1/data/upload/{project_id}")
async def upload_file_proxy(project_id: str, file: UploadFile):
    """
    Proxy file uploads to the backend server
    """
    import io
    
    try:
        # Read the file content
        content = await file.read()
        
        # Create a new file object for the backend request
        backend_file = {"file": (file.filename, io.BytesIO(content), file.content_type)}
        
        # Send the file to the backend server - use the correct API path
        logger.info(f"Proxying file upload to backend: {file.filename} (size: {len(content)} bytes)")
        
        # Use a much longer timeout for large files
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            # The backend route is under /api/v1/data/upload/{project_id}
            try:
                response = await client.post(
                    f"http://localhost:8000/api/v1/data/upload/{project_id}",
                    files=backend_file
                )
                
                # Check if response is successful
                if response.status_code == 200:
                    logger.info(f"Backend upload successful: {response.status_code}")
                    
                    # Parse the response JSON
                    try:
                        response_data = response.json()
                        logger.info(f"Response data: {response_data}")
                        
                        # Ensure we always use the backend's project_id for consistency
                        actual_project_id = response_data.get("project_id", project_id)
                        logger.info(f"Using project_id from backend response: {actual_project_id}")
                        
                        # Always ensure we have a file_id from the response
                        # The backend may return asset_id instead of file_id
                        if "file_id" not in response_data and "asset_id" in response_data:
                            response_data["file_id"] = response_data["asset_id"]
                            logger.info(f"Using asset_id as file_id: {response_data['file_id']}")
                        elif "file_id" not in response_data:
                            # If somehow no file_id or asset_id is provided, use a fallback ID
                            response_data["file_id"] = f"doc_{time.time()}"
                            logger.warning(f"No file_id or asset_id in response, using fallback: {response_data['file_id']}")
                        
                        # Always use backend project_id
                        response_data["project_id"] = actual_project_id
                            
                        # Add to our document store
                        new_doc = {
                            "id": response_data["file_id"],
                            "filename": file.filename,
                            "size": f"{len(content) / 1024:.1f} KB",
                            "date": "Today"
                        }
                        
                        if actual_project_id not in document_store:
                            document_store[actual_project_id] = []
                        
                        # Add document if it doesn't already exist
                        doc_ids = [doc["id"] for doc in document_store[actual_project_id]]
                        if new_doc["id"] not in doc_ids:
                            document_store[actual_project_id].append(new_doc)
                        
                        logger.info(f"Successfully processed upload. Project ID: {actual_project_id}, File ID: {response_data['file_id']}")
                        return response_data
                    except Exception as json_error:
                        logger.error(f"Error parsing response JSON: {str(json_error)}")
                        # Return a basic response with file_id and project_id
                        return {
                            "status": "success",
                            "message": "File uploaded successfully",
                            "file_id": project_id,
                            "project_id": project_id
                        }
                else:
                    logger.error(f"Backend returned error: {response.status_code}")
                    try:
                        error_content = response.text
                        logger.error(f"Response content: {error_content}")
                        raise HTTPException(status_code=response.status_code, detail=error_content)
                    except Exception as e:
                        logger.error(f"Error reading response content: {str(e)}")
                        raise HTTPException(status_code=response.status_code, detail="Backend error")
            except httpx.TimeoutException:
                logger.error("Request to backend timed out")
                return {
                    "status": "success",
                    "message": "File processing in progress",
                    "file_id": project_id,
                    "project_id": project_id
                }
    except httpx.RequestError as e:
        logger.error(f"Error proxying file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to backend: {str(e)}")
    except Exception as e:
        logger.error(f"Error proxying file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error proxying file upload: {str(e)}")

# NLP proxy endpoints
@app.post("/api/v1/nlp/index/answer/{project_id}")
async def nlp_answer_proxy(project_id: str, request: Request):
    """
    Proxy NLP answer requests to the backend server
    """
    try:
        # Get the request body
        body = await request.json()
        logger.info(f"Proxying NLP answer request for project {project_id}: {body}")
        
        # Forward the request to the backend
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                f"http://localhost:8000/api/v1/nlp/index/answer/{project_id}",
                json=body
            )
            
            # Return the response directly
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error proxying NLP answer request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error proxying NLP answer request: {str(e)}")

@app.post("/api/v1/nlp/general/answer")
async def nlp_general_answer_proxy(request: Request):
    """
    Proxy general NLP answer requests to the backend server
    """
    try:
        # Get the request body
        body = await request.json()
        logger.info(f"Proxying general NLP answer request: {body}")
        
        # Forward the request to the backend
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/nlp/general/answer",
                json=body
            )
            
            # Return the response directly
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error proxying general NLP answer request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error proxying general NLP answer request: {str(e)}")

@app.get("/api/v1/nlp/index/info/{project_id}")
async def nlp_index_info_proxy(project_id: str):
    """
    Proxy NLP index info requests to the backend server
    """
    try:
        logger.info(f"Proxying NLP index info request for project {project_id}")
        
        # Forward the request to the backend
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(
                f"http://localhost:8000/api/v1/nlp/index/info/{project_id}"
            )
            
            # Return the response directly
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error proxying NLP index info request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error proxying NLP index info request: {str(e)}")

@app.get("/api/v1/data/documents/{project_id}")
async def get_documents(project_id: str):
    """Get list of documents in a project"""
    try:
        # Try to get from backend if available
        backend_url = f"http://localhost:8000/api/v1/data/documents/{project_id}"
        try:
            response = requests.get(backend_url)
            if response.status_code == 200:
                logger.info(f"Got documents from backend for project {project_id}")
                backend_docs = response.json()
                
                # Update our local document store with backend data
                if "documents" in backend_docs and len(backend_docs["documents"]) > 0:
                    # Get existing documents first (including stc.pdf)
                    docs = ensure_stc_document(project_id)
                    
                    # Add any backend documents that aren't already in our local store
                    existing_ids = [doc["id"] for doc in docs]
                    for backend_doc in backend_docs["documents"]:
                        if backend_doc["id"] not in existing_ids:
                            docs.append(backend_doc)
                            existing_ids.append(backend_doc["id"])
                    
                    # Update document store
                    document_store[project_id] = docs
                    
                return {"documents": document_store[project_id]}
        except Exception as e:
            # If backend call fails, use fallback logic
            logger.warning(f"Error connecting to backend: {e}")
        
        # Check if we have documents in our local store
        if project_id in document_store and document_store[project_id]:
            # Make sure stc.pdf is included
            ensure_stc_document(project_id)
            logger.info(f"Returning documents from local store for project {project_id}: {document_store[project_id]}")
            return {"documents": document_store[project_id]}
        
        # If we reach here, we need to initialize the document list
        docs = ensure_stc_document(project_id)
        
        # Add the project document if it's not already there
        if not any(doc.get("id") == project_id for doc in docs):
            docs.append({
                "id": project_id,
                "filename": f"Document-{project_id}.pdf",
                "size": "Unknown",
                "date": "Today"
            })
        
        logger.info(f"Returning documents for project {project_id}: {document_store[project_id]}")
        return {"documents": document_store[project_id]}
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/data/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the system"""
    try:
        logger.info(f"Received request to delete document: {document_id}")
        
        # Special case - don't actually delete stc.pdf from the store
        # This ensures it's always available
        if document_id == "stc-doc-12345":
            logger.info("Attempted to delete stc.pdf document - this will be ignored")
            return {"status": "success", "message": "The stc.pdf document cannot be permanently deleted"}
        
        # Update our local document store
        deleted = False
        for project_id in document_store:
            # Get current documents for this project
            project_docs = document_store[project_id]
            
            # Find the document index (if it exists)
            doc_index = None
            for i, doc in enumerate(project_docs):
                if doc.get("id") == document_id:
                    doc_index = i
                    break
            
            # If found, remove it
            if doc_index is not None:
                del project_docs[doc_index]
                deleted = True
                
                # Make sure stc.pdf is still there
                ensure_stc_document(project_id)
        
        # Try to delete from backend if available
        try:
            # Connect to backend service to delete the document
            backend_url = f"http://localhost:8000/api/v1/data/documents/{document_id}"
            response = requests.delete(backend_url)
            
            if response.status_code == 200:
                logger.info(f"Document {document_id} deleted successfully via backend")
                return {"status": "success", "message": f"Document {document_id} deleted successfully"}
            else:
                logger.warning(f"Backend returned non-200 status for deletion: {response.status_code}")
                logger.warning(f"Response content: {response.text}")
        except Exception as e:
            # If backend call fails, log it but continue with our fallback
            logger.warning(f"Error connecting to backend for deletion: {e}")
        
        # Return success response
        logger.info(f"Document {document_id} deleted from local store: {deleted}")
        return {"status": "success", "message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.route('/api/v1/documents/list')
async def list_documents(request: Request):
    """Endpoint to list documents associated with a project."""
    try:
        # Get the query parameter from the request
        project_id = request.query_params.get('projectId', '0')
        if not project_id:
            return JSONResponse(
                status_code=400,
                content={'error': 'Project ID is required'}
            )
            
        logger.info(f"Listing documents for project: {project_id}")
        
        # Try to get documents from our local document store
        if project_id in document_store:
            docs = ensure_stc_document(project_id)
            logger.info(f"Returning {len(docs)} documents from local store for project {project_id}")
            return JSONResponse(content={"documents": docs})
            
        # If project doesn't exist in local store, try to get from backend API
        try:
            async with httpx.AsyncClient() as client:
                backend_url = f"http://localhost:8000/api/v1/data/documents/{project_id}"
                response = await client.get(backend_url)
                
                if response.status_code != 200:
                    logger.error(f"Backend API error: {response.status_code}")
                    # Create a new empty document list with just STC
                    docs = ensure_stc_document(project_id)
                    return JSONResponse(content={"documents": docs})
                    
                return JSONResponse(content=response.json())
        except Exception as e:
            logger.error(f"Error connecting to backend: {str(e)}")
            # Initialize with STC document as fallback
            docs = ensure_stc_document(project_id)
            return JSONResponse(content={"documents": docs})
            
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={'error': str(e)}
        )

# Add this if you want to run the server directly with "python main.py"
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)

  
