from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from fastapi.responses import JSONResponse
import os

from ..database import SessionLocal
from ..services import url_service
from ..repositories import url_repository
from ..cache import redis_client
from app.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


RATE_LIMITS = {
    "shorten": {
        "limit": 10,
        "window": 60
    },
    "redirect": {
        "limit": 200,
        "window": 60
    }
}

class URLRequest(BaseModel):
    original_url: HttpUrl
    expires_at: Optional[datetime] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_rate_limit(client_ip, endpoint):
    # If Redis not available → skip rate limiting
    if not redis_client:
        return None

    key = f"rate_limit:{endpoint}:{client_ip}"

    request_count = redis_client.incr(key)

    if request_count == 1:
        redis_client.expire(key, 60)

    if request_count > 60:
        return {"error": "Rate limit exceeded"}

    return None

@router.post("/shorten/")
def shorten(
    url_request: URLRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host
    rate_limit_response = check_rate_limit(client_ip, "shorten")
    if rate_limit_response:
        return rate_limit_response

    short_code = url_service.shorten_url(
        db,
        str(url_request.original_url),
        url_request.expires_at
    )

    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    logger.info(f"Short URL created: {short_code}")
    return {"short_url": f"{BASE_URL}/{short_code}"}

@router.get("/{short_code}")
def redirect(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host
    rate_limit_response = check_rate_limit(client_ip, "redirect")
    if rate_limit_response:
        return rate_limit_response

    # 2️⃣ Resolve URL (cache + DB + expiration logic)
    original_url = url_service.resolve_url(db, short_code)

    # 3️⃣ Async click increment
    background_tasks.add_task(
        url_repository.increment_click,
        db,
        short_code
    )
    

    logger.info(f"Redirect requested for {short_code}")
    # 4️⃣ Redirect
    return RedirectResponse(url=original_url)