from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import Optional
from fastapi.responses import RedirectResponse
from datetime import datetime
from .database import SessionLocal, engine, Base
from .models import URL
from .utils import encode_base62
from .cache import redis_client

app = FastAPI()
Base.metadata.create_all(bind=engine)

class URLRequest(BaseModel):
    original_url: HttpUrl
    expires_at: Optional[datetime] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def increment_click(db: Session, short_code: str):
    db.query(URL).filter(URL.short_code == short_code).update({URL.click_count: URL.click_count +1})
    db.commit() 

def check_rate_limit(client_ip:str):
    key=f"rate_limit:{client_ip}"

    request_count = redis_client.incr(key)
    if request_count == 1:
        redis_client.expire(key,60)

    if request_count > 10:
        raise HTTPException(status_code=429,details="Too many requests. Try again later.")


@app.post("/shorten/")
def shorten_url(url_request: URLRequest,request: Request, db: Session = Depends(get_db)):

    client_ip = request.client.host
    check_rate_limit(client_ip)
    
    new_url = URL(
        original_url=str(url_request.original_url),
        expires_at=url_request.expires_at
    )

    db.add(new_url)
    db.flush()

    short_code = encode_base62(new_url.id)
    new_url.short_code = short_code

    db.commit()
    db.refresh(new_url)

    return {"short_url": f"http://localhost:8000/{short_code}"}


@app.get("/{short_code}")
def redirect_url(short_code: str,background_tasks: BackgroundTasks, db: Session = Depends(get_db)):


    # 1️⃣ Check Redis
    cached_url = redis_client.get(short_code)
    if cached_url:
        return RedirectResponse(url=cached_url)

    # 2️⃣ DB Lookup
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # 3️⃣ Expiration Check
    if url_entry.expires_at and url_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="URL has expired")

    # 4️⃣ Smart Cache TTL
    if url_entry.expires_at:
        ttl = int((url_entry.expires_at - datetime.utcnow()).total_seconds())
        if ttl > 0:
            redis_client.set(short_code, url_entry.original_url, ex=ttl)
    else:
        redis_client.set(short_code, url_entry.original_url, ex=3600)

    background_tasks.add_task(increment_click,db,short_code)
    return RedirectResponse(url=url_entry.original_url)