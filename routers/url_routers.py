import hashlib
import random
import string
from typing import Union

from fastapi import APIRouter, Depends, Request, Header, BackgroundTasks
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, RedirectResponse

from db import models
from db.session import get_db, SessionLocal
from docs.responses import SUCCESS_GENERATE_SHORT_URL, SUCCESS_DELETE_SHORT_URL, SUCCESS_GET_URL_INFO
from schemas.url_shcemas import OriginalUrl
from redis_driver.redis import redis_connect

url_router = APIRouter()


def store_guest_url_info(guest_url_info, hashed_url):
    """Parsing the data and separating its different models
        to store in the tables below:
        - guest
        - guest_url
    """
    db = SessionLocal()
    db_url = db.query(models.Url).filter(models.Url.hashed == hashed_url).one_or_none()

    # Check if a visitor exists in the db or not
    db_visitor = db.query(models.Visitor).filter(models.Visitor.ip == guest_url_info['ip'],
                                                 models.Visitor.os == guest_url_info['os'],
                                                 models.Visitor.device == guest_url_info['device'],
                                                 models.Visitor.browser == guest_url_info['browser']).one_or_none()

    if db_visitor:
        # Just add data to the guest_url table
        url_visitor = models.UrlVisitor(url=db_url,
                                        visitor=db_visitor)
        db.add(url_visitor)
        db.commit()
    else:
        # This visitor(guest) is new, add it to its table too
        new_visitor = models.Visitor(ip=guest_url_info['ip'],
                                     device=guest_url_info['device'],
                                     os=guest_url_info['os'],
                                     browser=guest_url_info['browser'])
        db.add(new_visitor)
        db.commit()
        url_visitor = models.UrlVisitor(url=db_url,
                                        visitor=db_visitor)
        db.add(url_visitor)
        db.commit()


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
    redis_client.save()

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


@url_router.get("/ml/{hashed}",
                tags=["redirect_visitor"],
                responses={
                    200: {'description': 'The visitor redirected successfully.'
                          },
                    500: {
                        'description': 'Server failed to redirect.'
                    }
                }
                )
async def redirect_visitor(hashed: str,
                           fast_request: Request,
                           background_tasks: BackgroundTasks,
                           user_agent: Union[str, None] = Header(default=None),
                           db: Session = Depends(get_db), ):
    hashed_url = "ml/" + hashed

    # get visitor info
    # Get User IP using the request's META data
    guest_info = dict()
    user_agent = user_agent.split()
    guest_info['ip'] = fast_request.client.host
    guest_info['os'] = user_agent[1]
    guest_info['browser'] = user_agent[0] + user_agent[-1]
    guest_info['device'] = user_agent[1]  # not sure if its a good thing to do

    # This function will be running in the background using Celery.
    # So visitor will be redirected to the original URL ASAP.
    background_tasks.add_task(store_guest_url_info, guest_info, hashed_url)

    redis_client = redis_connect()
    # Converting Byte to String
    original_url = str(redis_client.get(hashed_url), 'utf-8')
    response = RedirectResponse(url=original_url)

    return response
