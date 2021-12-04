import abc
from dataclasses import dataclass


@dataclass
class Entry(object):
    name: str
    basic_infos: dict[str, str]
    summary: str


@dataclass
class EntryInfoBase(abc.ABC):
    name: str
    field: str
    link: str

    @abc.abstractmethod
    async def get_content(self) -> Entry:
        raise NotImplementedError


class WikiBase(abc.ABC):
    @abc.abstractmethod
    async def get_entries(self, name: str) -> list[EntryInfoBase]:
        raise NotImplementedError
