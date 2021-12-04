import nonebot
from nonebot.adapters.cqhttp.message import Message
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent

import userlib
import os

from userlib.wiki import EntryInfoBase, WikiBase
from userlib.wiki.baidu import BaiduWiki
# from userlib.wiki.moegirl import MoegirlWiki

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Wiki",
    "百科",
    "支持 \"百度百科\"\n"
    "发送 \"相应百科名称 + 词条名\" 即可使用"
)


async def _send_as_image(matcher: type[Matcher], message: str, times: float):
    tmp = userlib.gen_tmp("wiki-", ".png")
    try:
        userlib.draw_img_from_text(
            (16 * 80 + 2, int(34 * max(message.count("\n") * times, 24)) + 1),
            message, (tmp, "png"), userlib.sarasa_f32
        )
        await matcher.send(Message("[CQ:image,file=file://%s]" % tmp))
    except Exception as ex:
        await matcher.send("处理数据时，发生了意料之外的错误/(ㄒoㄒ)/~~")
        await matcher.send(getattr(ex, "message", str(ex)))
        raise
    finally:
        os.remove(tmp)


async def _first_handle(
    wiki: WikiBase,
    matcher: type[Matcher],
    event: MessageEvent,
    state: T_State
):
    name = event.get_message().extract_plain_text()

    try:
        infos = await wiki.get_entries(name)
    except Exception as ex:
        await matcher.send(
            "请求时发生错误，错误信息：\n" +
            getattr(ex, "message", str(ex))
        )
        raise

    if not infos:
        await matcher.finish("未找到名字为 %s 的词条" % name)
    elif len(infos) == 1:
        state["index"] = 1
    else:
        await matcher.send(
            "%s 为多义词，请选择所需查询词条的编号，如需取消操作发送 \"取消\" 即可:\n（请等待图片处理……）" % name
        )

        await _send_as_image(
            matcher,
            "\n".join([
                "%s. %s" % (index, info.field)
                for index, info in enumerate(infos, 1)
            ]),
            1.2
        )

    state["infos"] = infos


async def _arg_handle(matcher: type[Matcher], state: T_State):
    index_raw = state["index"]
    if (index_raw == "取消"):
        await matcher.finish("已取消操作")

    try:
        index = int(index_raw)
    except ValueError:
        await matcher.reject("输入的值与期望类型 int 不符合\n输入“取消”以取消操作")
        raise

    if index < 1 or index > len(state["infos"]):
        await matcher.reject("输入的值超出所预期的范围\n输入“取消”以取消操作")

    info: EntryInfoBase = state["infos"][index - 1]
    await matcher.send("链接：" + info.link)

    try:
        entry = await info.get_content()
    except Exception as ex:
        await matcher.send("请求时发生错误，错误信息：\n" + getattr(ex, "message", str(ex)))
        raise

    await _send_as_image(
        matcher,
        "%s\n简介：\n%s\n\n基本信息：\n%s" %
        (
            "%s（%s）" % (entry.name, info.field) if info.field else entry.name,
            entry.summary,
            "\n".join([
                " " * 4 + "%s: %s" % (key, value)
                for key, value in entry.basic_infos.items()
            ])
        ),
        2
    )

baidu = on_command("百度百科")
baidu_wiki = BaiduWiki()


@baidu.handle()
async def baidu_handle(bot: Bot, event: MessageEvent, state: T_State):
    await _first_handle(baidu_wiki, baidu, event, state)


@baidu.got("index")
async def baidu_arg_handle(bot: Bot, event: MessageEvent, state: T_State):
    await _arg_handle(baidu, state)

# moegirl = on_command("萌娘百科")
# moegirl_wiki = MoegirlWiki()


# @moegirl.handle()
# async def moegirl_handle(bot: Bot, event: MessageEvent, state: T_State):
#     await _first_handle(moegirl_wiki, moegirl, event, state)


# @moegirl.got("index")
# async def moegirl_arg_handle(bot: Bot, event: MessageEvent, state: T_State):
#     await _arg_handle(moegirl, state)
