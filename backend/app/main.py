from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.logger_config import logger
# from api_v1.Elastic.elastic import init_elastic

from app.core.models import Base
from app.core.config import SETTINGS_CONFIG
from app.api_v1.auth import login_router

from app.api_v1 import main_router
from app.core.models.helper import PostgresContext


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup function to create tables

    Args:
        app (FastAPI): main app
    """
    db_context = PostgresContext()
    await db_context.check_connection()
    yield


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# init_elastic()
app.include_router(main_router)
app.include_router(login_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)