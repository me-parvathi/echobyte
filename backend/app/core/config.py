from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv("../.env")

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EchoByte"
    
    # CORS Configuration
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mssql+pyodbc://username:password@server.database.windows.net:1433/database?driver=ODBC+Driver+18+for+SQL+Server"
    )
    
    # Azure SQL Database specific settings
    AZURE_SQL_SERVER: str = os.getenv("AZURE_SQL_SERVER", "")
    AZURE_SQL_DATABASE: str = os.getenv("AZURE_SQL_DATABASE", "")
    AZURE_SQL_USERNAME: str = os.getenv("AZURE_SQL_USERNAME", "")
    AZURE_SQL_PASSWORD: str = os.getenv("AZURE_SQL_PASSWORD", "")
    AZURE_SQL_PORT: int = int(os.getenv("AZURE_SQL_PORT", "1433"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 