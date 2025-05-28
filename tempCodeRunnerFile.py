import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    driver = "ODBC Driver 18 for SQL Server"
    server = os.getenv("DB_SERVER", "75.119.144.130")
    database = os.getenv("DB_NAME", "univo_db")
    username = os.getenv("DB_USER", "SA")
    password = os.getenv("DB_PASSWORD", "YourStrong!Passw0rd")

    params = quote_plus(
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
    )

    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    DEBUG = False
