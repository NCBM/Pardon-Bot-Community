import nonebot
from nonebot.adapters.cqhttp.message import Message

from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent

import random
from userlib.nbtool import chk_banned
from userlib.utils.trig import trig_protect
from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Random",
    "随机数工具",
    "[随机整数] 随机整数 <最小值> <最大值>\n"
    "[随机事件] 随机事件 <事件 1> <事件 2>……"
)

randomint = on_command("随机整数")
randomstr = on_command("随机事件")


@randomint.handle()
async def randomint_escape(bot: Bot, event: MessageEvent):
    msg = event.get_message().extract_plain_text().split()
    if len(msg) < 2:
        m_send = "[随机数工具::随机整数] 需要 2 个参数：<最小值> <最大值>"
    else:
        try:
            m_send = str(random.randint(int(msg[0]), int(msg[1])))
        except ValueError:
            m_send = "非法输入值"
    await bot.send(message=m_send, event=event)


@randomstr.handle()
async def randomstr_escape(bot: Bot, event: MessageEvent):
    await chk_banned(bot, event)
    args = str(event.get_message()).split()
    if len(args) < 2:
        await bot.send(event, "[随机数工具::随机事件] 至少需要 2 个参数：<事件 1> <事件 2>……")
        return
    choice = random.choice(args)
    trig_protect(("[CQ:at,qq=169934352]", "闷砖", "转盘"), choice)
    await bot.send(event, Message(choice))
