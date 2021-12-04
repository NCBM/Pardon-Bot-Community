import nonebot
from dataclasses import dataclass
import os
import random
import json
import time

from typing import Any, Iterable, Optional
from nonebot.adapters.cqhttp.event import GroupMessageEvent

from nonebot.plugin import on_command, on_message
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import Message

import userlib
from userlib.nbtool import Source, get_source

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Word Game",
    "单词竞赛",
    "[开始单词竞赛] @ + 单词竞赛\n"
    "[结束单词竞赛] @ + 结束单词竞赛\n"
    "[跳过] @ + 跳过\n"
    "[提示] @ + 提示"
)


@dataclass
class WordMeaning:
    pos: str
    cn: str

    def __init__(self, pos: str, cn: str):
        self.pos = pos
        self.cn = cn

    def __str__(self):
        return "%s %s" % (self.pos, self.cn)


@dataclass
class Word:
    word: str
    phonetic_symbol: str
    meanings: list[WordMeaning]


class State:
    started: bool
    words: list[Word]
    current: Optional[Word]
    used_words: list[Word]
    quescount: int
    tipslevel: int
    marks: dict[int, int]

    def clear(self):
        self.__init__()

    def __init__(self):
        self.started = False
        self.words = []
        self.current = None
        self.used_words = []
        self.quescount = -1
        self.tipslevel = -1
        self.marks = dict[int, int]()

    def init(self, words: list[Word], quescount: int):
        self.clear()
        self.words = words
        self.used_words = list[Word]()
        self.quescount = quescount

    def set_current(self, word: Word):
        self.used_words.append(word)
        self.current = word
        self.tipslevel = -1


def _get_state(source: Source) -> State:
    if source in _states.keys():
        return _states[source]

    _states[source] = State()
    return _states[source]


_states = dict[Source, State]()

start = on_command("单词竞赛", rule=to_me())
stop = on_command("结束单词竞赛", rule=to_me())
skip = on_command("跳过", rule=to_me())
tips = on_command("提示", rule=to_me())
received = on_message()


def _get_words(path: str) -> Iterable[Word]:
    def get_meanings(meanings: list[dict[Any, Any]]) -> Iterable[WordMeaning]:
        for meaning in meanings:
            yield WordMeaning(meaning["pos"], meaning["trans"])

    with open(path, mode="r", encoding="utf-8") as fp:
        words = json.load(fp)
        for word in words:
            yield Word(word["word"], word["phon"],
                       list(get_meanings(word["mean"])))


def _get_word(state: State) -> Word:
    used_words = state.used_words
    words = state.words

    if len(used_words) == len(words):
        raise Exception()

    word = random.choice(words)
    return word if word not in used_words else _get_word(state)


async def _next(bot: Bot, event: MessageEvent, state: State) -> None:
    state.started = False

    if len(state.used_words) == state.quescount:
        await bot.send(event, "游戏结束！")
        await bot.send(event, _get_result(state.marks))
        state.clear()

    else:
        word = _get_word(state)
        state.set_current(word)

        state.started = True

        await bot.send(
            event,
            "下一道题：\n%s"
            "\n发送 \"@ + 跳过\" 即可跳过（发送者禁言 5s）"
            "\n发送 \"@ + 提示\" 即可获取提示"
            % "\n".join([str(meaning) for meaning in word.meanings])
        )


def _get_result(marks: dict[int, int]) -> Message:
    sorted_marks = sorted(
        marks.items(),
        key=lambda marks: marks[1], reverse=True
    )

    member_marks = [
        "[CQ:at,qq=%s] 分数：%s" % (key, value)
        for key, value in sorted_marks
    ]

    return Message("分数榜：\n" + "\n".join(member_marks))


@start.handle()
async def start_escape(bot: Bot, event: MessageEvent) -> None:
    state = _get_state(get_source(event))

    if state.started:
        await bot.send(event, "游戏已经开始啦！")
        return

    params = event.message.extract_plain_text().split()
    count = len(params)

    books = [file.rstrip(".json") for file in os.listdir("wordbooks")]
    books.sort()

    tmp = userlib.gen_tmp("wordgame-", ".png")
    if count < 1 or count > 2:
        try:
            m_send = "用法：单词竞赛 <单词本名称> [题目数量（默认值 20）] \n"\
                     "目前支持的单词本：\n" + "\n".join(books)
            userlib.draw_img_from_text(
                (16 * 60, 34 * (len(books) + 6)), m_send, (tmp, "png"),
                userlib.sarasa_f32)
            await bot.send(
                event,
                Message("[CQ:image,file=file://{}]".format(tmp))
            )
        finally:
            os.remove(tmp)
        return

    book = params[0]

    if book not in books:
        await bot.send(
            event,
            "所指定的单词本 %s 不存在\n"
            "回复“单词竞赛”查看所有可用的单词本\n" % book
        )
        return

    quescount = 20 if count < 2 else int(params[1])
    words = list(_get_words(os.path.join("wordbooks", "%s.json" % book)))

    if quescount < 1 or quescount > len(words):
        await bot.send(event, "指定题目数量超出所预期的范围。")
        return

    state.init(words, quescount)

    word = _get_word(state)
    state.set_current(word)

    await bot.send(
        event,
        "游戏开始！现在来看第一道题目：\n%s"
        "\n回复 \"跳过\" 即可跳过（发送者禁言 5s）"
        "\n回复 \"提示\" 即可获取提示"
        "\n回复 \"结束单词竞赛\" 即可结束游戏"
        % "\n".join([str(meaning) for meaning in word.meanings])
    )

    state.started = True


@stop.handle()
async def stop_escape(bot: Bot, event: MessageEvent) -> None:
    state = _get_state(get_source(event))

    if not state.started:
        await bot.send(event, "游戏还没开始，就想结束啦？")
        return

    state.started = False

    await bot.send(event, _get_result(state.marks))
    state.clear()


@received.handle()
async def received_escape(bot: Bot, event: MessageEvent) -> None:
    state = _get_state(get_source(event))

    if not state.started:
        return

    text = event.message.extract_plain_text().strip()
    uid = event.user_id

    if text == state.current.word:
        state.started = False
        await bot.send(
            event,
            Message(
                "[CQ:at,qq=%s] 好耶，答对了，答案是：%s！"
                % (uid, state.current.word)
            )
        )

        marks = state.marks

        if uid in marks:
            marks[uid] += 1
        else:
            marks[uid] = 1

        time.sleep(1.5)
        await _next(bot, event, state)


@skip.handle()
async def skip_escape(bot: Bot, event: MessageEvent) -> None:
    state = _get_state(get_source(event))

    if not state.started:
        return

    state.started = False

    await bot.send(event, "答案是：%s 呀！" % state.current.word)

    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "set_group_ban", group_id=event.group_id,
            user_id=event.user_id, duration=8
        )

    await _next(bot, event, state)


@tips.handle()
async def tips_escape(bot: Bot, event: MessageEvent) -> None:
    state = _get_state(get_source(event))

    if not state.started:
        return

    state.tipslevel += 1

    current = state.current

    if state.tipslevel == 0:
        await bot.send(event, "这个单词的首字母是：" + current.word[0])
        return

    if state.tipslevel == 1:
        if len(current.word) > 3:
            await bot.send(event, "这个单词的前三个字母是：" + current.word[:3])
            return
        else:
            state.tipslevel += 1

    if state.tipslevel == 2:
        if len(current.word) > 2:
            await bot.send(event, "这个单词的最后一个字母是：" + current.word[-1])
            return
        else:
            state.tipslevel += 1

    if state.tipslevel == 3:
        await bot.send(event, "这个单词的音标是：/%s/" % current.phonetic_symbol)
        return

    await bot.send(event, "没有提示了www")
