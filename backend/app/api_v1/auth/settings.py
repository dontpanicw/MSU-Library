from dotenv import load_dotenv
import os
from envparse import Env

env = Env()
load_dotenv()

admin_login = os.environ.get("admin_login")
admin_password = os.environ.get("admin_password")

admin_data = {
    f"login": "admin",
    "password": "admin"
}

SECRET_KEY: str = env.str("SECRET_KEY", default="secret_key")
ALGORITHM: str = env.str("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=9999999)
