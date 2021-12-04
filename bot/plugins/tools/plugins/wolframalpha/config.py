from pydantic import BaseSettings


class Config(BaseSettings):
    wa_app_id: str
    bdfy_app_id: str
    bdfy_app_key: str
    wa_hjt_key: str

    class Config:
        extra = "ignore"
