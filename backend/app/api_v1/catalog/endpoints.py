from typing import Sequence

from fastapi import HTTPException, status
from fastapi.params import Query
from fastapi.routing import APIRouter

from app.core.logger_config import logger
from app.api_v1.add_material.endpoints import router as add_material_router
from app.api_v1.catalog.schemas import DocumentOutDTO
from app.api_v1.catalog.crud import get_documents, get_document, search_by_prompt, get_file_from_s3, \
    check_document_by_id
from app.core.models.helper import PostgresContext
from app.core.string_processor import StringProcessor

router = APIRouter(tags=["Catalog"])

router.include_router(add_material_router)


@router.get("/resources",
            response_model=list[DocumentOutDTO],
            response_description="Results matching criteria",
            responses={
                status.HTTP_400_BAD_REQUEST: {"description": "Bad input parameters"}
            })
async def get_all_documents(subjectArray: str | None = None,
                           semesterArray: str | None = None,
                           teacherArray: str | None = None,
                           subjectTypeArray: str | None = None):
    try:
        async with PostgresContext.new_session() as session:
            return await get_documents(subjectArray.split(',') if subjectArray else None,
                                   [int(x) for x in semesterArray.split(',')] if semesterArray else None,
                                   teacherArray.split(',') if teacherArray else None,
                                   subjectTypeArray.split(',') if subjectTypeArray else None,
                                   session)
    except Exception as e:
        logger.error(f"Problem to get documents. {e.__class__.__name__}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/search", response_model=Sequence[DocumentOutDTO])
async def search_document(prompt: str = Query(...,
                                              title="Поисковый запрос",
                                              description="Строка для поиска документов по названию, предмету, преподавателю и другим атрибутам.",
                                              example="математический анализ"),
                          subjectArray: str | None = Query(None,
                                                      title="Предмет",
                                                      example="Аналитическая геометрия"),
                          teacherArray: str | None = Query(None,
                                                      title="Преподаватель",
                                                      example="Иванов Иван Иванович"),
                          subjectTypeArray: str | None = Query(None,
                                                      title="Категория материала",
                                                      example="Лекция"),
                          semesterArray: str | None = Query(None,
                                                      title="Номер факультета",
                                                      example="1"),
                          limit: int | None = Query(None,
                                                      title="Ограничение количества документов",
                                                    ge=1,
                                                    le=100)) -> Sequence[DocumentOutDTO]:
    async with PostgresContext.new_session() as session:
        if prompt == "":
            if subjectArray == "" and teacherArray == "" and subjectTypeArray == "" and semesterArray == "":
                return []
            else:
                return await get_documents(subjectArray.split(',') if subjectArray else None,
                                   [int(x) for x in semesterArray.split(',')] if semesterArray else None,
                                   teacherArray.split(',') if teacherArray else None,
                                   subjectTypeArray.split(',') if subjectTypeArray else None,
                                   session)

        params = {"prompt": StringProcessor.refactor_string(prompt),
                  "session": session,
                  "subject": subjectArray.split(',') if subjectArray else None,
                  "teacher": teacherArray.split(',') if teacherArray else None,
                  "category": subjectTypeArray.split(',') if subjectTypeArray else None,
                  "semester_num": [int(x) for x in semesterArray.split(',')] if semesterArray else None,
                  "limit": limit}
        logger.debug(f"search parameters: {params}")
        return await search_by_prompt(**params)


@router.get("/resource/{id}",
            response_model=DocumentOutDTO,
            response_description="Pet resource",
            responses={
                status.HTTP_404_NOT_FOUND: {"description": "Document not found", "content": {}},
                status.HTTP_400_BAD_REQUEST: {"description": "Bad input parameter", "content": {}},
            })
async def get_document_by_id(document_id: int):
    try:
        async with PostgresContext.new_session() as session:
            return await get_document(document_id, session)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/get-file/{link:path}")
async def download_file_from_s3(link: str):
    async with PostgresContext.new_session() as session:
        slash_index = link.find('/')
        doc_id = link[:0 if slash_index == -1 else slash_index]
        if not await check_document_by_id(session, int(doc_id)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Link is uncorrect')
    return await get_file_from_s3(link, "resources")