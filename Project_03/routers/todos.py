from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Path
from models import Todos
from database import SessionLocal

from starlette import status
from pydantic import BaseModel, Field


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    # Ga ada todo.id karena SQL Alchemy otomatis nambahin id ketika id itu diset jadi Primary Key

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_models = db.query(Todos).filter(Todos.id == todo_id).first() # Ditambahin first supaya langsung fetch hasil pertama, jadi ga perlu akses semua id satu-satu
    if todo_models is not None:
        return todo_models
    raise HTTPException(status_code=404, detail='Todo not found')

@router.post('/create_todo', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, format_todo: TodoRequest):
    new_todo = Todos(**format_todo.dict())
    
    db.add(new_todo)
    db.commit() # mulai transaksi database
    
@router.put('/update_todo', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,
                      format_todo: TodoRequest, # db dependency sama format_todo harus diduluin sebelum kita define Path
                      todo_id: int = Path(gt=0)): 
    todo_models = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_models is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    
    todo_models.title = format_todo.title
    todo_models.description = format_todo.description
    todo_models.priority = format_todo.priority
    todo_models.complete = format_todo.complete
    
    db.add(todo_models)
    db.commit()

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency,
                      todo_id: int = Path(gt=0)):
    todo_models = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_models is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    
    db.commit()