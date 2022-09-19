from typing import Union

from sqlalchemy.exc import IntegrityError

from db import models
from db.models import Url
from db.session import SessionLocal

db = SessionLocal()


def add_url(original_url: str, hashed_url: str) -> bool:
    try:
        # Store the url in postgres db
        db_url = models.Url(original=original_url,
                            hashed=hashed_url)
        db.add(db_url)
        db.commit()
        return True
    except Exception as e:
        return False

