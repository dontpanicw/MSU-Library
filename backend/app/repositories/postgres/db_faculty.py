# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# from backend.app.models.Subject import Subject
# from backend.app.repositories.database import DB_URL
# from backend.logger_config import logger
# from backend.app.models.Faculty import Faculty

# engine = create_engine(DB_URL)
# Session = sessionmaker(bind=engine)


# def get_faculty_by_id(faculty_id: int):
#     session = Session()
#     try:
#         faculty = session.query(Faculty).filter(Faculty.id == faculty_id).first()
#         return faculty
#     except Exception as e:
#         logger.error(f"Failed to get categories: {e}")
