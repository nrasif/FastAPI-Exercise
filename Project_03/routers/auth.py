from datetime import timedelta, datetime
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from models import Users
from database import SessionLocal


from passlib.context import CryptContext
from jose import jwt

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'b71fdc3636c5e199c3ad6ac247291b32d24785a06def822a82a59b3e72fa3a16'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    mastiin_user = db.query(Users).filter(Users.username == username).first()
    if not mastiin_user:
        return False
    if not bcrypt_context.verify(password, mastiin_user.hashed_password):
        return False
    return mastiin_user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role':role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user')
        return {'username':username, 'id': user_id, 'user_role':user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user')

@router.post('/', status_code=status.HTTP_201_CREATED)
async def get_user(db: db_dependency,
                   format_user: CreateUserRequest):
    
    user_baru = Users(
        email = format_user.email,
        username = format_user.username,
        first_name = format_user.first_name,
        last_name = format_user.last_name,
        role = format_user.role,
        hashed_password = bcrypt_context.hash(format_user.password),
        is_active = True
    )
    
    db.add(user_baru)
    db.commit()
    
@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail = 'Could not validate user')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    
    return {'access_token': token, 'token_type': 'bearer'}
    
    # return 'Sucessfully Authentication'