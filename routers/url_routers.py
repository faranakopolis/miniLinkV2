import hashlib
import random
import string

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db import models
from db.session import SessionLocal
from docs.responses import SUCCESS_GENERATE_SHORT_URL, SUCCESS_DELETE_SHORT_URL, SUCCESS_GET_URL_INFO
from schemas.url_shcemas import OriginalUrl
from redis_driver.redis import redis_connect

url_router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@url_router.post("/url/",
                 tags=["generate_short_url"],
                 responses={
                     200: {
                         'content': {'application/json': {'example': SUCCESS_GENERATE_SHORT_URL}},
                         'description': 'The shorter url generated and returned to user successfully.'
                     },
                     500: {
                         'description': 'Server failed to return the generated url.'
                     }
                 }
                 )
async def generate_short_url(body: OriginalUrl, db: Session = Depends(get_db)):
    """This function hashes the original URL Using md5.
                To raise security and getting different short links from same URLs
                 the hashed string consists:
                    a random 5 character string +
                    original URL
            """
    mini_link_url = "ml/"
    random_string = ''.join(random.choices(string.ascii_uppercase +
                                           string.digits, k=5))
    # Mix them up
    mixed_string = random_string + body.original

    result = hashlib.md5(mixed_string.encode())

    # Convert to hex
    hashed_url = mini_link_url + result.hexdigest()

    # save url in postgres
    db_url = models.Url(original=body.original,
                        hashed=hashed_url)
    db.add(db_url)
    db.commit()

    # save url in redis
    redis_client = redis_connect()
    redis_client.set(hashed_url, body.original)

    return JSONResponse(status_code=200,
                        content={"short_url": hashed_url})


@url_router.delete("/url/",
                   tags=["delete_short_url"],
                   responses={
                       200: {
                           'content': {'application/json': {'example': SUCCESS_DELETE_SHORT_URL}},
                           'description': 'The shorter url deleted successfully.'
                       },
                       500: {
                           'description': 'Server failed to delete the url.'
                       }
                   }
                   )
async def delete_short_url(hashed_url: str, db: Session = Depends(get_db)):
    # set is_active flag to False in postgres
    db_url = db.query(models.Url).filter(models.Url.hashed == hashed_url).one_or_none()
    if not db_url:
        return None
    db_url.is_active = False
    db.add(db_url)
    db.commit()

    return JSONResponse(status_code=200,
                        content={"message": "deleted"})


@url_router.get("/url/",
                tags=["get_url(s)_info"],
                responses={
                    200: {
                        'content': {'application/json': {'example': SUCCESS_GET_URL_INFO}},
                        'description': 'The url(s) info retrieved and returned to user successfully.'
                    },
                    500: {
                        'description': 'Server failed to get the url(s) info.'
                    }
                }
                )
async def get_url_info(hashed_url: str = None,
                       offset: int = 0,
                       limit: int = 100,
                       db: Session = Depends(get_db)):
    if hashed_url:
        db_url = db.query(models.Url).filter(models.Url.hashed == hashed_url).one_or_none()
        url_visitors = db.query(models.UrlVisitor).filter(models.UrlVisitor.url == db_url).all()
        url_info = {"original": db_url.original,
                    "hashed": db_url.hashed,
                    "is_active": db_url.is_active,
                    "created_at": str(db_url.created_at),
                    "statistics": [{"ip": uv.visitor.ip,
                                    "device": uv.visitor.device,
                                    "browser": uv.visitor.browser,
                                    "os": uv.visitor.os,
                                    "visited_at": uv.created_at} for uv in url_visitors]}
        return JSONResponse(status_code=200,
                            content={"url": url_info})

    urls_info = []
    db_urls = db.query(models.Url).offset(offset).limit(limit).all()

    for i, url in enumerate(db_urls):
        url_visitors = db.query(models.UrlVisitor).filter(models.UrlVisitor.url == url).all()
        urls_info.append({"original": url.original,
                          "hashed": url.hashed,
                          "is_active": url.is_active,
                          "created_at": str(url.created_at),
                          "statistics": [{"ip": uv.visitor.ip,
                                          "device": uv.visitor.device,
                                          "browser": uv.visitor.browser,
                                          "os": uv.visitor.os,
                                          "visited_at": uv.created_at} for uv in url_visitors]})

    return JSONResponse(status_code=200,
                        content={"urls": urls_info})
