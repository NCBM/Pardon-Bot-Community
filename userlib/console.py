"""
console support
"""
from typing import Any, Callable


def command_not_found(tree: "CommandTree", cmd: str, _: str):
    """Internal command-not-found trigger."""
    print(f"{cmd}: command not found")


def logout(tree: "CommandTree", *_):
    """Internal 'logout' trigger."""
    tree.terminated = True


def input_s(prompt: str = "", interrupt: str = "", eof: str = "logout") -> str:
    """
    Like Python's built-in ``input()``, but it will give a string instead of
    raising an error when a user cancel(^C) or an end-of-file(^D on Unix-like
    or Ctrl-Z+Return on Windows) is received.

      prompt
        The prompt string, if given, is printed to standard output without a
        trailing newline before reading input.
      interrupt
        The interrupt string will be returned when a KeyboardInterrupt occurs.
      eof
        The end-of-file string will be returned when an EOFError occurs.

    Note: This implement keeps trailing a new line even when KeyboardInterrupt
    or EOFError is raised.
    """
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print()
        return interrupt
    except EOFError:
        print()
        return eof


class CommandTree:
    terminated: bool

    def __init__(self):
        self._funcs = dict[str, Callable[[Any], None]]()
        self.terminated = False
        self._funcs["logout"] = logout

    def add_command(self, command: str)\
            -> Callable[[Callable[[Any], None]], None]:
        """
        Add a command to the CommandTree.

          command
            Command name used for recognising.

        Example:
        >>> tree = console.CommandTree()
        >>> @tree.add_command("hello")
        >>> def hello(tree, cmd, arg):
        >>>     print("Hello world!")
        >>>
        """
        def _decorator(func: Callable[[Any], None]) -> Callable[[Any], None]:
            self._funcs[command] = func
            return func
        return _decorator

    def list_command(self) -> list[str]:
        """Return all registered command."""
        return list(self._funcs)

    def find_command(self, keyword: str = None) -> list[str]:
        """
        Return a list of command that matches the keyword.

          keyword
            Used for searching command. This will be an empty string if keyword
            is omitted, and it works just like ``CommandTree.list_command()``.
        """
        cmds = self.list_command()
        if keyword is None:
            keyword = ""
            return cmds
        result = []
        for cmd in cmds:
            if cmd.find(keyword) == 0:
                result.append(cmd)
        return result

    def run_command(self, command: str, arg: str) -> None:
        """
        Run a command that is added to the command tree.

          command
            Command name used for recognising.
          arg
            Argument of the command.

        Example:
        (see previous example code and continue.)
        >>> tree.run_command("hello")
        Hello world!
        >>> tree.run_command("logout")
        >>>
        """
        self._funcs.get(command, command_not_found)(self, command, arg)

    def wait_input(
        self,
        prompt: str = ">>> ",
        interrupt: str = "",
        eof: str = "logout"
    ):
        """Receive an input and process."""
        input_c = input_s(prompt, interrupt, eof)
        cmd, _, arg = input_c.partition(" ")
        if len(cmd) > 0:
            self.run_command(cmd, arg)

    def interactive(
        self,
        prompt: str = ">>> ",
        interrupt: str = "",
        eof: str = "logout"
    ):
        """Run in interactive mode."""
        while not self.terminated:
            self.wait_input(prompt, interrupt, eof)
