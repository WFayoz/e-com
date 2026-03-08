from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models.base_model import db
from app.routers import router



@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.create_all()
    print('project ishga tushdi')
    yield
    # await db.drop_all()
    print('project toxtadi')


app = FastAPI(docs_url='/', root_path='/api', title="E-Com", lifespan=lifespan)
app.include_router(router)
