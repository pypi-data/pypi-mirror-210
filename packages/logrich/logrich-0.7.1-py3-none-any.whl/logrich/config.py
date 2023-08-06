import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Server config settings
    """

    LOG_LEVEL: int | str = 5
    # макисмальная длина текста чтобы разместить его на одной линии с уровнем лога
    MAX_WITH_LOG_OF_OBJ: int = 120
    # https://loguru.readthedocs.io/en/stable/resources/recipes.html#adapting-colors-and-format-of-logged-messages-dynamically
    # https://docs-python.ru/standart-library/modul-string-python/klass-template-modulja-string/
    # https://loguru.readthedocs.io/en/stable/api/logger.html#color
    # https://rich.readthedocs.io/en/stable/style.html

    LOGURU_EXCEPTION_FORMAT_LONG: str = "{extra[msg]}\n{exception}\n"
    LOGURU_DATETIME_FORMAT: str = "%b-%d %H:%M"
    LOGURU_DATETIME_SHOW: bool = False
    LOGURU_DIAGNOSE: str = "NO"

    @property
    def MIN_WIDTH_COMPUTED(cls):
        if cls.LOGURU_DATETIME_SHOW:
            return cls.MIN_WIDTH + 3
        return cls.MIN_WIDTH

    MIN_WIDTH: int = 12
    MAX_WIDTH: int = 15
    RATIO_MAIN: int = 80
    RATIO_FROM: int = 40


config = Settings(_env_file=os.getenv("_env_file", default="./.env"))
