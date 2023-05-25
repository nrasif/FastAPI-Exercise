import uvicorn

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    
    def __init__(self, id: int, title: str, author: str, description: str, rating: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating

class BookRequest(BaseModel): #pydentic, biar ada data validation (biar ga semena mena ngisi data)
    id: Optional[int] = Field(title='ID is not needed')
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6) #gt artinya greater than, lt artinya lower than

    class Config: #Config supaya lebih jelas deskripsinya
        schema_extra = {
            'example': {
                'title': 'A new book',
                'author': 'codingwithrasif',
                'description': 'A new description of a book',
                'rating': 5
            }
        }

BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1)
]

# Ambil semua data buku
@app.get('/books')
async def read_all_books():
    return BOOKS

# Ambil buku berdasarkan id (karena id itu unique, maka pake dynamic parameter (cuma ambil 1 buku))
@app.get('/books/{book_id}')
async def read_book_by_id(book_id: int):
    for i in BOOKS:
        if i.id == book_id:
            return i

# Ambil buku berdasarkan rating (karena rating itu macem macem, pake query (ambil lebih dari 1 buku))
@app.get('/books/')
async def read_book_by_rating(book_rating: int):
    list_rating = []
    for i in BOOKS:
        if i.rating == book_rating:
            list_rating.append(i)
    return list_rating

# Bikin buku baru, tapi formatnya harus ngikutin BookRequest
@app.post('/create-book')
async def create_book(format_buku: BookRequest):
    new_book = Book(**format_buku.dict())
    BOOKS.append(find_book_id(new_book))

# biar id nya otomatis increment walaupun ga dimasukin input
def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book

# Update buku berdasarkan kesamaan id
@app.put('/books/update_book')
async def update_book(book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book

# Delete buku
@app.delete('/books/{book_id}')
async def delete_book(book_id: int):
    for i in BOOKS:
        if i.id == book_id:
            BOOKS.pop(i)
            break

if __name__ == "__main__":
    uvicorn.run(app, port=8010)