from pydantic import HttpUrl
from pydantic.main import BaseModel


class OriginalUrl(BaseModel):
    original: HttpUrl
