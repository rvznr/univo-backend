import os
import urllib.parse
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    driver = urllib.parse.quote_plus("ODBC Driver 17 for SQL Server")

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{os.getenv('MSSQL_USER')}:{os.getenv('MSSQL_PASSWORD')}@{os.getenv('MSSQL_SERVER')}/{os.getenv('MSSQL_DB')}?driver={driver}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
