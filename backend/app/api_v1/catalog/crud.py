import asyncio
from typing import Sequence, Any

from sqlalchemy import select, text, case, func
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.catalog.schemas import DocumentOutDTO
from app.core.models import Document
from app.core.logger_config import logger
from app.repositories.minio import MinioCRUD
from app.repositories.minio.minio_context import S3Context


async def check_teacher(teacher_name: str, session: AsyncSession) -> bool:
    teacher_query = select(Document.teacher_name).where(Document.teacher_name == teacher_name)

    result = await session.execute(teacher_query)
    if len(result.scalars().all()) > 0:
        return True
    else:
        return False


async def check_subject(subject_name: str, session: AsyncSession) -> bool:
    subject_query = select(Document.subject_name).where(Document.subject_name == subject_name)

    result = await session.execute(subject_query)
    if len(result.scalars().all()) > 0:
        return True
    else:
        return False


async def check_category(category_name: str, session: AsyncSession) -> bool:
    category_query = select(Document.category_name).where(Document.category_name == category_name)

    result = await session.execute(category_query)
    if len(result.scalars().all()) > 0:
        return True
    else:
        return False


DOCUMENT_QUERY = select(
            Document.id.label('document_id'),
            Document.name,
            Document.year,
            Document.link,
            Document.is_file,
            Document.subject_name,
            Document.teacher_name,
            Document.category_name,
            Document.semester_num
        )

async def get_documents(subject_list: list[str] | None,
                            semester_list: list[str] | None,
                            teacher_list: list[str] | None,
                            subject_type_list: list[str] | None,
                            session: AsyncSession) -> Sequence[DocumentOutDTO]:
    try:
        docs_stmt = DOCUMENT_QUERY

        if subject_list:
            docs_stmt = docs_stmt.filter(Document.subject_name.in_(subject_list))
        if semester_list:
            docs_stmt = docs_stmt.filter(Document.semester_num.in_(semester_list))
        if teacher_list:
            docs_stmt = docs_stmt.filter(Document.teacher_name.in_(teacher_list))
        if subject_type_list:
            docs_stmt = docs_stmt.filter(Document.category_name.in_(subject_type_list))

        result: Result = await session.execute(docs_stmt)
        docs = [DocumentOutDTO.model_validate(row._mapping) for row in result.all()]
        return docs
    except Exception as e:
        logger.error(f"Failed to get documents: {e.__class__.__name__}: {e}")
        raise e

async def get_document(document_id: int, session: AsyncSession) -> DocumentOutDTO:
    try:
        document_query = DOCUMENT_QUERY.where(Document.id == document_id)
        result: Result = await session.execute(document_query)
        if document := result.all():
            document = DocumentOutDTO.model_validate(document[0]._mapping)
            logger.debug(f"Document found: {document}")

            return document
        else:
            raise ValueError("Can't find document")
    except Exception as e:
        logger.error(f"Failed to get document: {e.__class__.__name__}: {e}")
        raise e

def _get_array(array: list[Any]):
    return str(tuple(array)) if len(array) > 1 else str(tuple(array))[:-2] + ')'

async def search_by_prompt(prompt: str,
                           session: AsyncSession,
                           *,
                           subject: list[str] | None = None,
                           teacher: list[str] | None = None,
                           category: list[str] | None = None,
                           semester_num: list[int] | None = None,
                           limit: int | None = None) -> Sequence[DocumentOutDTO] | None:

    accur_query = text('SET pg_trgm.similarity_threshold = 0.2;')
    try:
        await session.execute(accur_query)
    except Exception as e:
        logger.error(f"Failed to search by prompt: {e.__class__.__name__}: {e}")
        raise e

    rank = f"(ts_rank(combined_string_tsv, plainto_tsquery('russian', '{prompt}')) * 0.8 + similarity(combined_string, '{prompt}') * 0.2)"

    search_query = f"""
    SELECT document_id, {rank} AS final_rank
    FROM document_search_view
    WHERE (combined_string_tsv @@ plainto_tsquery('russian', '{prompt}')
    OR combined_string % '{prompt}')
    AND {rank} >= 0.3
"""

    if subject:
        search_query += f"""\nAND subject_name IN {_get_array(subject)}"""
    if teacher:
        search_query += f"""\nAND teacher_name IN {_get_array(teacher)}"""
    if category:
        search_query += f"""\nAND category_name IN {_get_array(category)}"""
    if semester_num:
        search_query += f"""\nAND semester_num IN {_get_array(semester_num)}"""

    search_query += f"\nORDER BY {rank} DESC;"

    if limit:
        search_query = search_query[:-1] + f"\nLIMIT {limit};"
    search_query = text(search_query)

    try:
        logger.debug(f"Search query: {search_query}")
        result: Result = await session.execute(search_query)
        docs = result.all()
        docs_ids, docs_ranks = [], []

        for row in docs:
            docs_ids.append(row.document_id)
            docs_ranks.append(row.final_rank)

        logger.debug(f'Document rank info: {docs_ranks}')
        logger.debug(f'Document ids info: {docs_ids}')
    except Exception as e:
        logger.error(f"Failed to search documents IDs: {e.__class__.__name__}: {e}")
        raise e

    if len(docs_ids) > 0:
        order_mapping = {id_: index for index, id_ in enumerate(docs_ids)}
        order_case = case(order_mapping, value=Document.id, else_=len(docs_ids))

        docs_query = DOCUMENT_QUERY.where(Document.id.in_(docs_ids)).order_by(order_case)

        try:
            result: Result = await session.execute(docs_query)
            docs = [DocumentOutDTO.model_validate(row._mapping) for row in result.all()]
        except Exception as e:
            logger.error(f"Failed to search documents: {e.__class__.__name__}: {e}")
            raise e
    else:
        logger.debug(f"No documents found")

    logger.debug(f"Search '{prompt}' is successful!")
    return docs

async def get_file_from_s3(link: str, bucket_name: str):
    try:
        async with S3Context.new_client() as client:
            s3_context = S3Context(crud=MinioCRUD(client, bucket_name))
            return await s3_context.crud.get_object(link, 1024*1024)
    except Exception as e:
        logger.error(f"Failed to add file. {type(e)}{e.__class__.__name__}: {e}")
        raise

async def check_document_by_id(
    session: AsyncSession,
    doc_id: int,
) -> bool:
    statement = select(Document.id).where(Document.id == doc_id)
    answer_from_db: Result = await session.execute(statement=statement)
    user = answer_from_db.scalar()
    return True if user else False

if __name__ == '__main__':
    asyncio.run(get_file_from_s3('1/IMG_2137.pdf', 'resources'))