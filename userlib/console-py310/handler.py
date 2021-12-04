from typing import Callable
from dataclasses import dataclass

Handler = Callable[[str], None]
MatcherCondition = Callable[[str], bool]


@dataclass
class Matcher(object):
    condition: MatcherCondition
    handle: Handler


class Console(object):
    handlers: list[Matcher]

    _in: Callable[[], str]
    _out: Callable[[str], None]

    def __init__(
        self,
        _in: Callable[[], str] | None = None,
        _out: Callable[[str], None] | None = None
    ) -> None:
        def _default_out(text: str) -> None:
            print(text, end="")

        self.handlers = list()
        self._in = _in if _in else input
        self._out = _out if _out else _default_out

    def match(self, condition: MatcherCondition):
        def _decorator(func: Handler) -> Handler:
            self.handlers.append(Matcher(condition, func))
            return func

        return _decorator

    def seek(self, prompt: str | None, default: Handler | None = None):
        if prompt:
            self._out(prompt)
        text = self._in()
        handled = False
        for handler in self.handlers:
            if handler.condition(text):
                handler.handle(text)
                handled = True
        if not handled and default:
            default(text)

    def print(self, text: str):
        self._out(text)
