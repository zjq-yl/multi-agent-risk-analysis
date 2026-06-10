from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="Financial Risk Agent", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    mysql_host: str = Field(default="localhost", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="root", alias="MYSQL_USER")
    mysql_password: str = Field(default="", alias="MYSQL_PASSWORD")
    mysql_database: str = Field(default="financial_risk_agent", alias="MYSQL_DATABASE")

    faiss_index_path: str = Field(default="./data/faiss_index", alias="FAISS_INDEX_PATH")
    knowledge_docs_path: str = Field(default="./docs", alias="KNOWLEDGE_DOCS_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()