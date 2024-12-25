from contextlib import asynccontextmanager
from typing import TypeVar, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import db_config
from app.core.logger_config import logger

PostgresCRUD = TypeVar('PostgresCRUD', bound=Any)

class PostgresContext[PostgresCRUD]:
    """ Класс для работы с СУБД PostgreSQL """

    #: CRUD для взаимодействия с таблицей
    _crud: PostgresCRUD | None = None

    #: Движок к СУБД
    engine: AsyncEngine = create_async_engine(f"{db_config.driver}://{db_config.username}:{db_config.password}@{db_config.host}{f':{db_config.port}' if db_config.port else ''}/{db_config.database}")

    #: Фабрика соединений
    _sessionmaker: async_sessionmaker[AsyncSession] | None = async_sessionmaker(engine)

    @property
    def crud(self) -> PostgresCRUD:
        if self._crud:
            return self._crud
        else:
            raise ValueError('CRUD object has not been initialized')

    @crud.setter
    def crud(self, crud: PostgresCRUD):
        self._crud = crud

    @classmethod
    @asynccontextmanager
    async def new_session(cls):
        """ Fabric to create new session with database """
        async with cls._sessionmaker() as session:
                yield session
                await session.commit()

    async def check_connection(self):
        logger.info("Try to connect to PostgreSQL")
        try:
            async with self.new_session() as session:
                await session.execute(text('SELECT 1'))
            logger.info("Connection to PostgreSQL is successful!")
        except Exception as e:
            logger.error(f"Connection to PostgreSQL failed: {e.__class__.__name__} - {e}")
            raise ConnectionError("Connection to PostgreSQL failed!")

    def __init__(self, *,
                 engine: AsyncEngine | None = None,
                 crud: PostgresCRUD | None = None,
                 ):
        if engine:
            self.engine = engine

        self._sessionmaker = async_sessionmaker(self.engine)

        if crud:
            self._crud = crud