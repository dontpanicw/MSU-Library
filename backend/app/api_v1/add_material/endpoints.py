from fastapi import HTTPException, status, UploadFile, File, Query, Depends
from fastapi.routing import APIRouter
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from app.api_v1.auth.settings import admin_data
from app.api_v1.add_material.crud import add_document, add_file_to_s3
from app.api_v1.add_material.schemas import MaterialAddDTO
from app.api_v1.catalog.crud import check_teacher, check_subject, check_category
from app.core.models import Document
from app.core.models.helper import PostgresContext
from app.api_v1.auth.crud import get_current_user_from_token

router = APIRouter()


@router.post("/resource",
             description="Adds an item to the system",
             status_code=status.HTTP_201_CREATED,
             response_description="Resource created",
             responses={
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid input"},
    status.HTTP_409_CONFLICT: {"description": "An existing item already exists"},
})
async def add_material_page(body: MaterialAddDTO,
                            current_user: admin_data = Depends(get_current_user_from_token)):
    async with PostgresContext.new_session() as session:
        # Check body info
        if not await check_teacher(body.teacher_name, session):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher is not found")
        if not await check_subject(body.subject_name, session):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject is not found")
        if not await check_category(body.category_name, session):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category is not found")

        try:
            await add_document(session,
                               body.name,
                               body.year,
                               body.link,
                               body.is_file,
                               body.subject_name,
                               body.teacher_name,
                               body.category_name,
                               body.semester_num)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An existing item already exists")

@router.post("/file", status_code=status.HTTP_201_CREATED)
async def add_file_s3(document_id: int = Query(...), file: UploadFile = File(...),
                      current_user: admin_data = Depends(get_current_user_from_token)):
    filename = await add_file_to_s3(str(document_id),"resources", file)
    async with PostgresContext.new_session() as session:
        query = update(Document).where(Document.id == document_id).values(link=filename, is_file=True)
        await session.execute(query)