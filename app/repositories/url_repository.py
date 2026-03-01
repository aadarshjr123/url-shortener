from sqlalchemy.orm import Session
from ..models import URL


def create_url(db: Session, original_url: str, expires_at=None):
    url = URL(original_url=original_url, expires_at=expires_at,click_count=0)
    db.add(url)
    db.flush()
    return url


def get_by_short_code(db: Session, short_code: str):
    return db.query(URL).filter(URL.short_code == short_code).first()


def increment_click(db: Session, short_code: str):
    db.query(URL).filter(URL.short_code == short_code).update({
        URL.click_count: URL.click_count + 1
    })
    db.commit()