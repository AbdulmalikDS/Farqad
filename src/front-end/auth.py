from datetime import timedelta, datetime
from typing import Annotated, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal, User, Individual, Admin, Organization
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
import secrets
from passlib.context import CryptContext
import uuid

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '9231c9496752f3887965250eeda37e544232680d0b23a760b8caa8d9112d9618'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUserRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.email == request.email) | (User.name == request.name)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or name already exists")
    create_user_model = User(
        userID=str(uuid.uuid4()),
        name=request.name,
        email=request.email,
        password=bcrypt_context.hash(request.password),
        type='individual'
    )
    db.add(create_user_model)
    db.commit()
    return {"message": "User created successfully"}

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token = create_access_token(user.email, user.userID, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_access_token(email: str, userID: str, expire_delta: timedelta):
    encode = {'sub': email, 'id': userID}
    expires = datetime.utcnow() + expire_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        userID: str = payload.get('id')
        if email is None or userID is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'email': email, 'userID': userID}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')






