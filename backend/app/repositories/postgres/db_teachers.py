# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# from backend.app.models.Subject import Subject
# from backend.app.repositories.database import DB_URL
# from backend.logger_config import logger
# from backend.app.models.Teacher import Teacher

# engine = create_engine(DB_URL)
# Session = sessionmaker(bind=engine)


# def get_all_teachers():
#     session = Session()
#     try:
#         teachers = session.query(Teacher).all()
#         return teachers
#     except Exception as e:
#         logger.error(f"Failed to get teachers: {e}")
