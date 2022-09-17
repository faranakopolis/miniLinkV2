from fastapi import FastAPI
from core.config import settings
from db.session import engine, Base
from routers.url_routers import url_router

app = FastAPI(docs_url=settings.URL_PREFIX + '/docs/',
              title=settings.PROJECT_NAME,
              description=settings.PROJECT_DESCRIPTION,
              version=settings.PROJECT_VERSION)

app.include_router(url_router,
                   prefix=settings.URL_PREFIX)

Base.metadata.create_all(bind=engine)
