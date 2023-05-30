from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from starlette import status

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from models import Users

from passlib.context import CryptContext

router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post('/auth', status_code=status.HTTP_201_CREATED)
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