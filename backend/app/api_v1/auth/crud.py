from typing import Union

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import jwt, JWTError
from app.api_v1.auth.settings import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

from app.api_v1.auth.hashing import Hasher
from app.api_v1.auth.settings import admin_data

from starlette import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def authenticate_user(
    login: str, password: str):
    if login != admin_data["login"]:
        return
    if password != admin_data["password"]:
        return
    return admin_data

async def get_current_user_from_token(
    authorization: str = Security(api_key_header)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split()[-1]
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        login: str = payload.get("sub")
        print("login extracted is ", login)
        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    if login != admin_data["login"]:
        raise credentials_exception
    return admin_data