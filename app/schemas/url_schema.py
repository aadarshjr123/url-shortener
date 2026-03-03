from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class URLRequest(BaseModel):
    original_url: HttpUrl
    expires_at: Optional[datetime] = None


class URLResponse(BaseModel):
    short_url: str