import uvicorn
from fastapi import Body, FastAPI


app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

@app.get("/books")
async def read_all_books():
    return BOOKS
# fastapi bersifat chronological, jadi harus urut. kalo mau pake books/blabla (fixed bukan dynamic), berarti harus ditaruh di pertama (taruh ini dulu sebelum pake dynamic)
@app.get("/books/mybook")
async def mybook():
    return{'fav book title':'my fav book'}

#Dynamic parameters, bedanya dengan query, ga bisa return lebih dari 1 buku, dynamic parameter juga ga bisa lebih dari 1 parameter, /books/{hanya 1 dynamic parameter} karena identik
# kecuali habis {dynamic parameter} ada query, baru bisa, atau {dynamic parameter} nya beda, tapi ditambahin query
@app.get("/books/{title_book}")
async def read_book(title_book: str):
    for book in BOOKS:
        if book.get('title').casefold() == title_book.casefold():
            return book

# by query, bisa lebih dari 1 buku untuk ngequery. Perbedaan lainnya harus ditulis dengan akhiran "/", nanti di webnya ditulis :
# http://127.0.0.1:8000/books/?category=math'
# ini juga ga boleh identik, kalau identik, ilang salah satu di docsnya
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

# dynamic parameters () digabung sama query, dynamic parameters-nya (book_author) beda sama single dynamic parameter tanpa query (title_book)
# sama kayak dynamic parameters, ga bisa lebih dari 1 (/books/{dynamic_parameter2}/) karena identik
@app.get("/books/{book_author}/")
async def read_queries(book_author: str, book_category:str):
    queries_dynamic = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == book_category.casefold():
            queries_dynamic.append(book)
            
    return queries_dynamic

# Contoh POST (kalo di CRUD dia masuknya CREATE)
@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)

# Contoh PUT (kalo di CRUD dia masuknya UPDATE)
@app.put("/books/update_book")
async def update_book(buku_terkini=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == buku_terkini.get('title').casefold():
            BOOKS[i] = buku_terkini

# Contoh DELETE (delete 1 key value berdasarkan title)
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break

if __name__ == "__main__":
    uvicorn.run(app, port=8000)