from fastapi.routing import APIRouter

from app.api_v1.catalog import catalog_router
from app.api_v1.user import user_router
# from app.api_v1.add_material import add_material


router = APIRouter(tags=["Main"])

@router.get("/health")
async def healthcheck():
    return {"message": "ok"}



router.include_router(catalog_router)
# router.include_router(user_router)
