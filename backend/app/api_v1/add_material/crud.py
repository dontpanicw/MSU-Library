import time

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Document
from app.core.logger_config import logger
from app.repositories.minio import MinioCRUD
from app.repositories.minio.minio_context import S3Context


async def add_document(
    session: AsyncSession,
    name: str,
    year: int,
    link: str | None,
    is_file: bool,
    subject_name: str,
    teacher_name: str | None,
    category_name: str,
    semester_num: int,
):
    try:
        new_document = Document(
            name=name,
            year=str(year),
            link=link,
            is_file=is_file,
            subject_name=subject_name,
            teacher_name=teacher_name,
            category_name=category_name,
            semester_num=semester_num
        )

        session.add(new_document)
        await session.commit()
        await session.refresh(new_document)
        document_id = new_document.id
        logger.info(f"Документ добавлен успешно: {new_document.name}")
        return document_id
    except SQLAlchemyError as e:
        # Откатываем изменения при возникновении ошибки
        await session.rollback()
        logger.error(f"Ошибка при добавлении документа: {e}")
        return None

async def add_file_to_s3(document_id: str, bucket_name: str, file: UploadFile) -> str:
    try:
        async with S3Context.new_client() as client:
            s3_context = S3Context(crud=MinioCRUD(client=client, bucket_name=bucket_name))
            s3_filename = f'{document_id}/{file.filename}'
            await s3_context.crud.create_object(s3_filename, await file.read())
            return s3_filename
    except Exception as e:
        logger.error(f"Failed to add file. {e.__class__.__name__}: {e}")
        raise