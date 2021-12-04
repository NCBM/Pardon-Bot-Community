import abc
from dataclasses import dataclass
from typing import Optional


class TranslatorConfigBase(abc.ABC):
    pass


T_TranslatorConfig = TranslatorConfigBase


@dataclass(frozen=True)
class TranslationResult:
    translated_text: str
    source_language: str

    def __str__(self):
        return self.translated_text


class TranslatorBase(abc.ABC):
    config: T_TranslatorConfig

    def __init__(self, config: T_TranslatorConfig):
        self.config = config

    @abc.abstractmethod
    async def translate(
        self,
        text: str,
        dest_lang: str,
        src_lang: Optional[str] = None
    ) -> TranslationResult:
        raise NotImplementedError


T_Translator = TranslatorBase


class TranslationError(Exception):
    code: int

    def __init__(self, code: int):
        self.code = code
