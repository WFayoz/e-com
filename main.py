from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.admin import setup_admin
from app.config.config import settings
from app.models.base_model import db
from app.routers import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_all()
    print('project ishga tushdi')
    yield
    await db.drop_all()
    print('project toxtadi')


app = FastAPI(docs_url='/', root_path='/api', title="E-Com", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
setup_admin(app)
app.include_router(router)
