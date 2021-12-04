import nonebot
from nonebot.adapters.cqhttp.event import GroupMessageEvent

from nonebot.plugin import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, Message

import random
from userlib.utils import time2sec

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Mute-me",
    "自闭",
    "[自闭] @ + 我要自闭 <时长>\n"
    "[取消自闭解限] @ + 我不确认\n"
    "[确定自闭解限] @ + 我确认，按我说的做"
)

pre_limit_raid: dict[int, int] = {}

mute = on_command("我要自闭", rule=to_me())
cancel = on_command("我不确认", rule=to_me())
confirm = on_command("我确认，按我说的做", rule=to_me())


@mute.handle()
async def mute_escape(bot: Bot, event: GroupMessageEvent):
    time = event.message.extract_plain_text().strip()
    uid = event.user_id
    if time:
        try:
            mute_secs = int(float(time)) if time.isdecimal() else \
                time2sec(time)
            if mute_secs == -1:
                mute_secs = random.randint(1 * 20 * 60, 24 * 60 * 60)
            assert 5 <= mute_secs <= 86400 * 30
            if mute_secs > 86400:
                global pre_limit_raid
                with open("../muteme_nolimit") as f:
                    nolimit = f.read().split("\n")
                if uid not in nolimit:
                    await bot.send(
                        message="⚠警告：你可能将被禁言超过一天的时间！\n"
                        "该行为有较大风险，请确认你是否要自闭这么长时间。\n"
                        "本次确认后，你将不再受到最高一天的自闭限制。\n"
                        "回复“@ + 我不确认”以取消操作，回复三次“@ + 我确认，按我"
                        "说的做”以解除限制",
                        event=event)
                    pre_limit_raid[uid] = 3
                    return
        except:
            await bot.send(
                message="时间错误！（可用时间范围在 5(5s) 到 "
                "86400 * 30(30d) 之间）",
                event=event)
            raise
    else:
        mute_secs = random.randint(1 * 20 * 60, 24 * 60 * 60)
    try:
        await bot.call_api("set_group_ban", group_id=event.group_id,
                           user_id=uid, duration=mute_secs)
        await bot.send(message=Message("[CQ:at,qq={}]成 功 自 闭！".format(uid)),
                       event=event)
    except:
        await bot.send(
            message=Message("[CQ:at,qq={}]你TM故意找茬是不是？！".format(uid)),
            event=event)
        raise
    pass


@cancel.handle()
async def cancel_escape(bot: Bot, event: GroupMessageEvent):
    global pre_limit_raid
    uid = event.user_id
    try:
        pre_limit_raid.pop(uid)
    finally:
        await bot.send(
            message=Message(
                "[CQ:at,qq={}]你TM故意找茬是不是？！".format(uid)),
            event=event)
        await bot.call_api("set_group_ban", group_id=event.group_id,
                           user_id=uid, duration=10)
        pass


@confirm.handle()
async def confirm_escape(bot: Bot, event: GroupMessageEvent):
    global pre_limit_raid
    uid = event.user_id
    if uid not in pre_limit_raid:
        await bot.send(
            message=Message(
                "[CQ:at,qq={}]你TM故意找茬是不是？！".format(uid)),
            event=event)
        await bot.call_api("set_group_ban", group_id=event.group_id,
                           user_id=uid, duration=10)
        return
    pre_limit_raid[uid] -= 1
    if pre_limit_raid[uid] < 1:
        with open("../muteme_nolimit", "a") as f:
            f.write(str(uid) + "\n")
        await bot.send(
            message=Message(
                "[CQ:at,qq={0}]你现在没有机会反悔了。\n"
                "现在你可以用一些时间思考自己要自闭多长时间。"
                .format(uid)),
            event=event)
    else:
        await bot.send(
            message=Message(
                "[CQ:at,qq={0}]你现在还有 {1} 次机会可以来反悔。\n"
                "现在你可以冷静10秒钟，然后考虑你的回答。"
                "※回复“我不确认”来反悔。".format(uid, pre_limit_raid[uid])),
            event=event)
        await bot.call_api("set_group_ban", group_id=event.group_id,
                           user_id=uid, duration=10)
    pass
