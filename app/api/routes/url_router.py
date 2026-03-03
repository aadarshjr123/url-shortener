from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.schemas.url_schema import URLRequest, URLResponse
from app.api.deps import get_db, get_url_service
from app.repositories.url_repository import URLRepository
from app.core.config import settings
from app.cache.redis import redis_client
from fastapi import HTTPException

router = APIRouter()


def rate_limit(key: str, limit: int, window: int):
    if not redis_client:
        return

    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, window)

    if count > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


@router.post("/shorten", response_model=URLResponse)
def shorten(
    payload: URLRequest,
    request: Request,
    db: Session = Depends(get_db),
    service=Depends(get_url_service),
):
    client_ip = request.client.host
    rate_limit(f"shorten:{client_ip}", 10, 60)

    short_code = service.shorten_url(
        db, str(payload.original_url), payload.expires_at
    )

    return URLResponse(
        short_url=f"{settings.BASE_URL}/{short_code}"
    )


@router.get("/{short_code}")
def redirect(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    service=Depends(get_url_service),
):
    client_ip = request.client.host
    rate_limit(f"redirect:{client_ip}", 200, 60)

    original_url = service.resolve_url(db, short_code)

    repo = URLRepository()
    background_tasks.add_task(repo.increment_click, short_code)

    return RedirectResponse(url=original_url)