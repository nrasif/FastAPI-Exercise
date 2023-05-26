import uvicorn

from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, HTTPException, Path
import models
from models import Todos
from database import engine, SessionLocal

from starlette import status
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

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

@app.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@app.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_models = db.query(Todos).filter(Todos.id == todo_id).first() # Ditambahin first supaya langsung fetch hasil pertama, jadi ga perlu akses semua id satu-satu
    if todo_models is not None:
        return todo_models
    raise HTTPException(status_code=404, detail='Todo not found')

@app.post('/create_todo', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, format_todo: TodoRequest):
    new_todo = Todos(**TodoRequest.dict())
    
    db.add(new_todo)
    db.commit() # mulai transaksi database


if __name__ == "__main__":
    uvicorn.run(app, port=8010)