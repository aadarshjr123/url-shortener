from app.db.session import SessionLocal
from app.repositories.url_repository import URLRepository
from app.services.url_service import URLService
from app.cache.redis import redis_client
from fastapi import Depends


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_url_service():
    repo = URLRepository()
    return URLService(repo)