import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Union
from fastapi.staticfiles import StaticFiles

# from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from app.schema import Book as SchemaBook
from app.schema import Author as SchemaAuthor

from app.schema import Book
from app.schema import Author

from app.models import Book as ModelBook
from app.models import Author as ModelAuthor

import os
from dotenv import load_dotenv



load_dotenv('.env')

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


@app.get("/", response_class=HTMLResponse)
async def home():
   return templates.TemplateResponse("index.html", 
            {"data":["One","two","three"]})  


@app.post('/book/', response_model=SchemaBook)
async def book(book: SchemaBook):
   db_book = ModelBook(title=book.title, rating=book.rating, author_id = book.author_id)
   db.session.add(db_book)
   db.session.commit()
   return db_book

@app.get('/books/')
async def book():
   book = db.session.query(ModelBook).all()
   return book


@app.post('/author/', response_model=SchemaAuthor)
async def author(author:SchemaAuthor):
   db_author = ModelAuthor(name=author.name, age=author.age)
   db.session.add(db_author)
   db.session.commit()
   return db_author

@app.get('/authors/')
async def author():
   author = db.session.query(ModelAuthor).all()
   return author


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
engine = create_engine('postgresql://postgres:password123@postgres/fastapi')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/templates/index2/', response_class=HTMLResponse)
async def get_html(request: Request,db=Depends(get_db)):
   books =  db.query(Book).all()
   data = [book.__dict__ for book in books]  # Replace with your model data
   return templates.TemplateResponse("index.html", {"request": request, "data": data})

    
# To run locally
if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8000)

