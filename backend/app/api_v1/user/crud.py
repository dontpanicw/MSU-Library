"""Module with CRUD for users table in Postgres"""

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User

async def check_user_by_nickname(
    session: AsyncSession,
    nickname: str,
) -> bool:
    statement = select(User.id).where(User.nickname == nickname)
    answer_from_db: Result = await session.execute(statement=statement)
    user = answer_from_db.scalar()
    return True if user else False


async def get_user_by_nickname(
    session: AsyncSession,
    nickname: str,
) -> User | None:
    statement = select(User).where(User.nickname == nickname)
    answer_from_db: Result = await session.execute(statement=statement)
    user = answer_from_db.scalar()
    return user


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    return await session.get(User, user_id)
