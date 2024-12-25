"""
Endpoints in users router
"""

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
    Response,
    Cookie,
)

from app.core.models import User
from app.api_v1.user.utils import encode_jwt
from app.api_v1.user.schemas import TokenInfo
from app.api_v1.user.dependencies import validate_auth_user_password, validate_access_token, get_current_auth_user


router = APIRouter(prefix="/user", tags=["USER"])


@router.post("/login/", status_code=status.HTTP_200_OK, response_model=TokenInfo)
async def login_user(
    response: Response,
    user: User = Depends(validate_auth_user_password),
) -> TokenInfo:
    # create token and put it to cookie
    access_token_value = encode_jwt(
        payload={"sub": user.id},
    )
    response.set_cookie(
        key="access_token",
        value=f"{access_token_value}",
        httponly=True,
        samesite="lax",
    )
    return TokenInfo(
        access_token=access_token_value,
        token_type="Bearer",
    )


@router.post("/logout/")
async def logout_user(
    response: Response,
    access_token: Annotated[str | None, Cookie()] = None,
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User isnt logged in"
        )
    response.delete_cookie("access_token")
    return {"detail": "Logged out"}


@router.get("/validate/")
async def validate_token(
    token_payload=Depends(validate_access_token),
    user: User = Depends(get_current_auth_user),
):
    return {
        "nickname": user.nickname,
        "email": user.email,
        "exp": token_payload["exp"],
    }
