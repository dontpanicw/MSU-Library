from typing import Annotated
from annotated_types import MinLen, MaxLen

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base model for user"""

    nickname: Annotated[str, MinLen(4), MaxLen(15)]
    email: EmailStr | None


class UserIn(UserBase):
    """Model for creating a user"""

    password: Annotated[str, MinLen(6)]


class UserOut(UserBase): ...


class TokenInfo(BaseModel):
    access_token: str
    token_type: str
