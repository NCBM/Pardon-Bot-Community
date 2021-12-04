from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here

    developers: dict[str, int]
    extra_manager = [
        3403388302,  # Miku
    ]
    version: tuple[int, int, int, int]

    class Config:
        extra = "ignore"
