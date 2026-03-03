from sqlalchemy.orm import Session
from app.db.models import URL


class URLRepository:

    def create(self, db: Session, original_url: str, expires_at=None) -> URL:
        url = URL(
            original_url=original_url,
            expires_at=expires_at,
            click_count=0,
            short_code="",  # temporary
        )
        db.add(url)
        db.flush()
        return url

    def get_by_short_code(self, db: Session, short_code: str) -> URL | None:
        return db.query(URL).filter(URL.short_code == short_code).first()

    def increment_click(self, short_code: str):
        from app.db.session import SessionLocal

        db = SessionLocal()
        try:
            db.query(URL).filter(URL.short_code == short_code).update(
                {URL.click_count: URL.click_count + 1}
            )
            db.commit()
        finally:
            db.close()