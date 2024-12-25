from contextlib import asynccontextmanager

from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session, AioSession

from app.core.config import s3_config
from app.core.logger_config import logger
from app.repositories.minio import MinioCRUD

class S3Context:

    crud: MinioCRUD

    _session_fabric: AioSession = get_session()

    @classmethod
    @asynccontextmanager
    async def new_client(cls) -> AioSession:
        try:
            async with cls._session_fabric.create_client("s3",
                                                  aws_access_key_id=s3_config.access_key,
                                                  aws_secret_access_key=s3_config.secret_key,
                                                  endpoint_url=s3_config.uri) as s3_client: #type: AioBaseClient
                yield s3_client
                logger.debug("Client is closed!")
                await s3_client.close()
        except Exception as e:
            logger.error(f"Failed to execute operations. {e.__class__.__name__}: {e}")
            raise e


    def __init__(self,
                 *,
                 crud: MinioCRUD,
                 create_buckets: bool = False):
        self.crud = crud

        self.create_buckets = create_buckets
