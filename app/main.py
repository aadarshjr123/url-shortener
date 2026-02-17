from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from .database import SessionLocal, engine, Base
from .models import URL
from .utils import encode_base62
from .cache import redis_client



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



@app.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    cached_url = redis_client.get(short_code)
    if cached_url:
        return RedirectResponse(cached_url)
    
    url_entry = db.query(URL).filterURL.short_code == short_code.first()

    if not url_entry:
        return {"error": "URL not found"}
    
    redis_client.set(short_code, url_entry.original_url, ex=3600)  # Cache for 1 hour

    return RedirectResponse(url_entry.original_url)