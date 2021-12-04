from pydantic import BaseSettings


class Config(BaseSettings):
    bdfy_app_id: str
    bdfy_app_key: str

    class Config:
        extra = "ignore"
