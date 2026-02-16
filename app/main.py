from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import URL
from pydantic import BaseModel
from .utils import encode_base62

app = FastAPI()
Base.metadata.create_all(bind=engine)

class URLRequest(BaseModel):
    original_url: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/shorten/")
def shorten_url(url_request: URLRequest, db: Session = Depends(get_db)):
    # Generate a unique short code (for simplicity, using the ID)
    new_url = URL(original_url=url_request.original_url)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    short_code = encode_base62(new_url.id)
    new_url.short_code = short_code
    db.commit()

    return {"short_url": f"http://localhost:8000/{short_code}"}