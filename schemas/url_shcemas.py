from pydantic import HttpUrl
from pydantic.main import BaseModel


# This Schema is used in generate_short_url API
class OriginalUrl(BaseModel):
    original: HttpUrl
