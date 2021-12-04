"""
Global User Library for Game
"""


from typing import Optional


class Scoreboard():
    """Scoreboard for storaging scores"""
    def __init__(self, title: str = "计分板", sc_prefix: str = "",
                 sc_suffix: str = "", default_score: int = 0,
                 reverse: bool = False):
        self.title = title
        self.sc_prefix = sc_prefix
        self.sc_suffix = sc_suffix
        self.default_score = default_score
        self.reverse = reverse
        self.data = dict[str, int]()

    def to_list(self) -> list[tuple[str, int]]:
        return sorted(self.data.items(), reverse=self.reverse)

    def __str__(self):
        export = self.title + "\n"
        export += "\n".join(["%s %s%d%s" %
                             (n, self.sc_prefix, s, self.sc_suffix)
                             for n, s in self.to_list()])
        return export

    def __repr__(self):
        return "Scoreboard(%s\n)" % self.__str__()

    def insert(self, name: str, score: Optional[int] = None):
        if score is None:
            score = self.default_score
        if name:
            self.data[name] = score

    def add_score(self, name: str, add: int = 0,
                  insert_if_not_exist: bool = False):
        if name not in self.data:
            if insert_if_not_exist:
                self.insert(name)
            else:
                raise KeyError("No name called '%s'" % name)
        self.data[name] += add
