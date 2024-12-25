from datetime import datetime, timedelta

import jwt
import bcrypt

from app.core.config import SETTINGS_CONFIG


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


def encode_jwt(
    payload: dict,
    private_key: str = SETTINGS_CONFIG.private_key_path.read_text(),
    algorithm: str = SETTINGS_CONFIG.algorithm,
    expire_minutes: int = SETTINGS_CONFIG.access_token_expire_minutes,
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire, iat=now)
    encoded = jwt.encode(to_encode, private_key, algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = SETTINGS_CONFIG.public_key_path.read_text(),
    algorithm: str = SETTINGS_CONFIG.algorithm,
) -> dict:
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded
