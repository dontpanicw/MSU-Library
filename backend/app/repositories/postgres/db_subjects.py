# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, joinedload

# from backend.app.core.config import settings
# from sqlalchemy.ext.declarative import declarative_base

# from backend.app.models.Subject import Subject
# from backend.app.repositories.database import DB_URL
# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
# from backend.logger_config import logger

# engine = create_engine(DB_URL, echo=True)
# Session = sessionmaker(bind=engine)


# def get_all_subjects():
#     session = Session()
#     try:
#         subjects = session.query(Subject).all()
#         return subjects
#     except Exception as e:
#         logger.error(f"Failed to get subjects: {e}")
