"""
Dependencies for endpoints.py
"""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import InvalidTokenError

from app.core.models import User
from app.core.models.helper import PostgresContext
from .utils import decode_jwt, validate_password
from app.api_v1.user.crud import get_user_by_nickname, get_user_by_id


async def validate_auth_user_password(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Helper Function for login route to check a user by password
    """
    invalid_login_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    async with PostgresContext.new_session() as session:
        user_from_db = await get_user_by_nickname(
            session=session, nickname=form_data.username
        )

    # if no user was found by username in db
    if not user_from_db:
        raise invalid_login_exception

    hash_from_db: bytes = user_from_db.pass_hash

    # if passwords dont match
    if not validate_password(form_data.password, hash_from_db):
        raise invalid_login_exception

    return user_from_db


async def validate_access_token(
    access_token: Annotated[str | None, Cookie()] = None,
) -> dict:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user is not logged in",
        )
    token_payload = {}
    try:
        token_payload = decode_jwt(
            token=access_token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # NOTE: REMOVE EXCEPTION IN PROD
            detail=f"invalid access token error: {e}",
        )
    return token_payload


async def get_current_access_token_payload(
    access_token: Annotated[str | None, Cookie()] = None,
) -> dict:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user is not logged in",
        )
    payload = {}
    try:
        payload = decode_jwt(
            token=access_token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # NOTE: REMOVE EXCEPTION IN PROD
            detail=f"invalid access token error: {e}",
        )
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_access_token_payload),
) -> User:
    id: int | None = payload.get("sub")

    async with PostgresContext.new_session() as session:
        # check user in db
        user_from_db = await get_user_by_id(session=session, user_id=id)

    if not user_from_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # NOTE: REMOVE ADDITIONAL INFO IN PROD
            detail="token invalid (user not found)",
        )
    return user_from_db
