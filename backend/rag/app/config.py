from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    aws_region: str = "ap-south-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    pinecone_api_key: str = ""
    pinecone_index_name: str = "voyonata-travel"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
