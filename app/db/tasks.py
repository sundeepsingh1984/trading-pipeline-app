from fastapi import FastAPI
from databases import Database
from app.config import DATABASE_URL,DATABASE_URL_ASYNC,DATABASE_URL_ALPACA_ASYNC,DATABASE_URL_ALPACA
import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


logger = logging.getLogger(__name__)








async def connect_to_db(app: FastAPI) -> None:
    database = Database(DATABASE_URL, min_size=2, max_size=10)  # these can be configured in config as well

    try:
        await database.connect()
        app.state._db = database
    except Exception as e:
        logger.warn("--- DB CONNECTION ERROR ---")
        logger.warn(e)
        logger.warn("--- DB CONNECTION ERROR ---")


async def close_db_connection(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
    except Exception as e:
        logger.warn("--- DB DISCONNECT ERROR ---")
        logger.warn(e)
        logger.warn("--- DB DISCONNECT ERROR ---")



def database_session(source) :

    if source == "Alpaca":

        database_url_async=DATABASE_URL_ALPACA_ASYNC
        database_url=DATABASE_URL_ALPACA

    else:
        database_url_async=DATABASE_URL_ASYNC
        database_url=DATABASE_URL

    try:

        async_engine = create_async_engine(str(database_url_async),echo=False)
        async_session=sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
        engine=create_engine(str(database_url))
        session=sessionmaker(engine,expire_on_commit=False)
        return (async_session,session)
   
    except Exception as e:
        logger.warn("--- DB CONNECTION ERROR ---")
        logger.warn(e)
        logger.warn("--- DB CONNECTION ERROR ---")
        raise e


