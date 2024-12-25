# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# from core.models.Subject import Subject
# from core.config import settings
# from core.logger_config import logger
# from core.models.Category import Category


# def get_all_categories():
#     session = Session()
#     try:
#         categories = session.query(Category).all()
#         return categories
#     except Exception as e:
#         logger.error(f"Failed to get categories: {e}")
