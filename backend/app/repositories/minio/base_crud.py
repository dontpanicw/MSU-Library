import io
import urllib.parse

from aiobotocore.client import AioBaseClient
from attrs import define
from starlette.responses import StreamingResponse

from app.core.logger_config import logger


@define
class MinioCRUD:
    client: AioBaseClient

    bucket_name: str

    create_buckets: bool = False

    async def get_object(self, link: str, chunk_size: int = 1024 * 1024):
        try:
            await self.client.head_object(Bucket=self.bucket_name, Key=link)
        except Exception as e:
            logger.error(f"Head object failed: {e.__class__.__name__}: {e}")
            raise ValueError("File not found")
        s3_obj = await self.client.get_object(Bucket=self.bucket_name, Key=link)
        i = 1
        file = s3_obj['Body']
        res = b''
        while True:
            chunk = await file.read(chunk_size)  # Чтение по 1 МБ
            logger.debug(i)
            i += 1
            if not chunk:
                break
            res += chunk

        resp = StreamingResponse(io.BytesIO(res), media_type="application/octet-stream")

        filename_encoded = urllib.parse.quote(link[link.find('/') + 1:])
        resp.headers["Content-Disposition"] = f"attachment; filename={filename_encoded}"
        return resp

    async def create_object(self,
                            filename: str,
                            data: bytes):
        await self.client.put_object(Bucket=self.bucket_name, Key=filename, Body=data)
