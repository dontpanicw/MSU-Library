from typing import Annotated
from jwt import InvalidTokenError

from fastapi import Cookie

from app.api_v1.user.utils import decode_jwt


async def validate_access_token(
    access_token: Annotated[str | None, Cookie()] = None,
) -> dict:
    if not access_token:
        return {}
    token_payload = {}
    try:
        token_payload = decode_jwt(
            token=access_token,
        )
    except InvalidTokenError as e:
        return {}
    return token_payload

