from pydantic import BaseSettings


# pydantic will parse the environment variables in a case sensitive way
class Settings(BaseSettings):
    data: str = "data"


settings = Settings()
