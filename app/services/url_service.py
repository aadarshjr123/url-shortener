from datetime import datetime, timezone
from fastapi import HTTPException
from ..utils import encode_base62
from ..cache import redis_client
from ..repositories import url_repository

import logging
logger = logging.getLogger(__name__)


def shorten_url(db, original_url: str, expires_at=None):
    # Create DB record
    url = url_repository.create_url(db, original_url, expires_at)

    # Generate short code
    short_code = encode_base62(url.id)
    url.short_code = short_code

    db.commit()
    db.refresh(url)

    return short_code


def resolve_url(db, short_code: str):
    # 1️⃣ Check Redis first
    if redis_client:
     cached_url = redis_client.get(short_code)
     if cached_url:
        return cached_url

    # 2️⃣ Query DB
    url = url_repository.get_by_short_code(db, short_code)

    if not url:
        logger.warning(f"Short code not found: {short_code}")
        raise HTTPException(status_code=404, detail="Short URL not found")

    if url.expires_at:
        expires = url.expires_at

        # If DB returned naive datetime, force it to UTC
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        if expires < datetime.now(timezone.utc):
            logger.warning(f"Expired link accessed: {short_code}")
            raise HTTPException(status_code=410, detail="URL expired")
    

    # 4️⃣ Smart caching
    if url.expires_at:
        ttl = int((url.expires_at - datetime.utcnow()).total_seconds())
        if ttl > 0:
            redis_client.set(short_code, url.original_url, ex=ttl)
    else:
        if redis_client:
            redis_client.set(short_code, url.original_url, ex=3600)

    if not url.original_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid redirect URL")
    
    return url.original_url