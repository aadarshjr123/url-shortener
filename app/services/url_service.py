from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.utils.base62 import encode_base62
from app.cache.redis import redis_client
from app.repositories.url_repository import URLRepository
from app.core.config import settings


class URLService:

    def __init__(self, repo: URLRepository):
        self.repo = repo

    def shorten_url(self, db: Session, original_url: str, expires_at=None) -> str:
        with db.begin():
            url = self.repo.create(db, original_url, expires_at)
            short_code = encode_base62(url.id)
            url.short_code = short_code

        return short_code

    def resolve_url(self, db: Session, short_code: str) -> str:

        # 1️⃣ Redis cache
        if redis_client:
            cached = redis_client.get(short_code)
            if cached:
                return cached

        # 2️⃣ DB
        url = self.repo.get_by_short_code(db, short_code)
        if not url:
            raise HTTPException(status_code=404, detail="Short URL not found")

        # 3️⃣ Expiration check
        if url.expires_at:
            expires = url.expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)

            if expires < datetime.now(timezone.utc):
                raise HTTPException(status_code=410, detail="URL expired")

        # 4️⃣ Cache
        if redis_client:
            if url.expires_at:
                ttl = int(
                    (url.expires_at - datetime.now(timezone.utc)).total_seconds()
                )
                if ttl > 0:
                    redis_client.set(short_code, url.original_url, ex=ttl)
            else:
                redis_client.set(short_code, url.original_url, ex=3600)

        return url.original_url