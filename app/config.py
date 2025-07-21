from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_ROOT_PASSWORD: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    EMBEDDING_MODEL: str
    OPENAI_API_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
