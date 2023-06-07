from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Path
from models import Todos

from database import SessionLocal
from .auth import get_current_user # bikin authentication dulu

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
user_dependency = Annotated[dict, Depends(get_current_user)] # habis bikin auth dan JWT, tambahin user dependency biar tiap ngelakuin CRUD, authentication ke JWT

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    # Ga ada todo.id karena SQL Alchemy otomatis nambahin id ketika id itu diset jadi Primary Key

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    
    todo_models = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first() # Ditambahin first supaya langsung fetch hasil pertama, jadi ga perlu akses semua id satu-satu
    if todo_models is not None:
        return todo_models
    raise HTTPException(status_code=404, detail='Todo not found')

@router.post('/create_todo', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db: db_dependency,
                      format_todo: TodoRequest):
    
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    
    new_todo = Todos(**format_todo.dict(), owner_id = user.get('id'))
    db.add(new_todo)
    db.commit() # mulai transaksi database
    
@router.put('/todo{todo_id}', status_code=status.HTTP_204_NO_CONTENT) #ga boleh sembarangan ganti APIendpoint (diubah dari /update_todo jadi /todo/{todo_id})
async def update_todo(user: user_dependency,
                      db: db_dependency,
                      format_todo: TodoRequest, # db dependency sama format_todo harus diduluin sebelum kita define Path
                      todo_id: int = Path(gt=0)): 
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    
    todo_models = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_models is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    
    todo_models.title = format_todo.title
    todo_models.description = format_todo.description
    todo_models.priority = format_todo.priority
    todo_models.complete = format_todo.complete
    
    db.add(todo_models)
    db.commit()

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):
    
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    
    todo_models = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    
    if todo_models is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    
    db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).delete()
    
    db.commit()