import nonebot

from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.rule import to_me

import json
import random

from userlib.nbtool import Source, get_source
from userlib.exceptions import InvalidOperationException

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Idiom Game",
    "成语接龙",
    "[开始/停止成语接龙] 成语接龙\n"
    "[成语接龙状态] 状态\n"
    "[成语接龙] @ + 接龙 <成语>"
)

switch = on_command("成语接龙")
state_get = on_command("成语接龙状态")
received = on_command("接龙", to_me())


class State:
    def __init__(self):
        self.enabled = False
        self.current = ""
        self.usable_idioms = list[str]()

    def clear(self):
        self.__init__()


def _read_file() -> list[str]:
    with open("idiom.json", encoding="utf-8") as fp:
        return json.load(fp)


# def _write_file(idioms: list[str]):
#     with open("idiom.json", encoding="utf-8") as fp:
#         return json.dump(idioms)


_states = dict[Source, State]()
_idioms = _read_file()
# _state_machines = StateMachineCollection()


def _get_state(source: Source) -> State:
    if source in _states.keys():
        return _states[source]

    state = State()
    _states[source] = state
    return state


def _get_usable_idioms(char: str) -> list[str]:
    return [idiom for idiom in _idioms if idiom.startswith(char)]


@switch.handle()
async def switch_escape(bot: Bot, event: MessageEvent):
    def get_idiom() -> tuple[str, list[str]]:
        idiom = random.choice(_idioms)
        usable_idioms = _get_usable_idioms(idiom[-1])
        if len(usable_idioms) < 2:
            return get_idiom()

        return idiom, usable_idioms

    state = _get_state(get_source(event))

    if state.enabled:
        state.clear()
        await bot.send(event, "结束游戏")
    else:
        idiom = get_idiom()

        state.current = idiom[0]
        state.usable_idioms = idiom[1]
        state.enabled = True

        await bot.send(
            event,
            "接龙开始，已经帮你挑选好第一个成语 \"{}\"，请以 \"{}\" 开头"
            "的成语进行接龙（请以 @ + \"接龙\"+成语 格式进行接龙）"
            .format(idiom[0], idiom[0][-1]))


@state_get.handle()
async def state_get_escape(bot: Bot, event: MessageEvent):
    state = _get_state(get_source(event))

    if state.enabled:
        await bot.send(
            event,
            "目前成语为 \"{}\"，请以 \"{}\" 开头的成语进行接龙"
            .format(state.current, state.current[-1]))
    else:
        await bot.send(event, "成语接龙暂未开始，请发送 \"成语接龙\" 开始游戏")


@received.handle()
async def received_escape(bot: Bot, event: MessageEvent):
    msg = event.get_message().extract_plain_text()
    state = _get_state(get_source(event))

    if not state.enabled:
        await bot.send(event, "成语接龙暂未开始，请发送 \"成语接龙\" 开始游戏")
        return

    if state.current == "":
        raise InvalidOperationException(
            "The field 'current' (type 'str') in 'state' is empty")

    if len(state.usable_idioms) == 0:
        raise InvalidOperationException(
            "The field 'usable_idioms' (type 'list[str]') in 'state' is empty")

    if msg in state.usable_idioms:
        char = msg[-1]
        usable_idioms = _get_usable_idioms(char)

        if len(usable_idioms) == 0:
            state.clear()
            await bot.send(event, "无可用成语可继续接龙，游戏结束")
            return

        state.current = msg
        state.usable_idioms = usable_idioms
        await bot.send(event, "接龙成功，请继续以 \"{}\" 开头的成语进行接龙".format(char))
    else:
        char = state.current[-1]
        if msg.startswith(state.current[-1]):
            await bot.send(event, "没有这个成语哦！请继续以 \"{}\" 开头的成语进行接龙".format(char))
        else:
            await bot.send(event, "不是这个开头啦！请继续以 \"{}\" 开头的成语进行接龙".format(char))
