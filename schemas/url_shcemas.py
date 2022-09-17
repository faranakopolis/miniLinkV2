from pydantic.main import BaseModel


class OriginalUrl(BaseModel):
    original: str
