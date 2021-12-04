import nonebot
from nonebot.plugin import on_command  # , on_message
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.adapters.cqhttp.message import Message
from nonebot.typing import T_State

from .gamecore import gen_num, GNum

from os.path import exists
from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "1A2B",
    "猜数字",
    "[开始游戏] @ + 1A2B\n"
    "[结束游戏] 结束\n"
    "[统计信息] @ + 统计"
)

start = on_command("1A2B", rule=to_me())
achievement = on_command("统计", rule=to_me())


def save_data(uid: int, times: int):
    with open(f"../1a2b_hist/{uid}", "a") as f:
        f.write(str(times) + "\n")


def read_data(uid: int):
    with open(f"../1a2b_hist/{uid}", "r") as f:
        data = [int(d) for d in f.read().split("\n")[:-1]]
    return (len(data), min(data), max(data), sum(data) / len(data))


@start.handle()
async def start_hook(bot: Bot, event: MessageEvent, state: T_State):
    if not state.get("started", False):
        state["started"] = True
        state["count"] = 0
        await start.send(
            Message(
                f"[CQ:at,qq={event.user_id}]欢迎来到 1A2B 猜数字游戏！\n"
                "如果你不熟悉这个游戏，你可以自行搜索教程。\n"
                "请注意：在游戏结束之前，你的消息都会被我处理。\n"
                "回复 \"结束\" 来退出游戏。"
            )
        )
        state["base"] = gen_num()
        await start.reject("我已经准备好了一个 4 位的随机数字！来猜猜吧！")
    else:
        base = state["base"]
        msg = event.get_message().extract_plain_text().strip()
        if msg == "结束":
            await start.send(
                Message(f"[CQ:at,qq={event.user_id}]成功退出！")
            )
            count = state["count"]
            await start.finish(
                Message(
                    f"[CQ:at,qq={event.user_id}](´╥ω╥`))\n"
                    f"我准备的数字是 {int(base)}\n"
                    f"你一共猜了 {count} 次"
                )
            )
        try:
            inn = GNum(int(msg))
            stat = base.test(inn)
            state["count"] += 1
            # print(str(stat))
            if stat.same == 4:
                count = state["count"]
                save_data(event.user_id, count)
                await start.finish(
                    Message(
                        f"[CQ:at,qq={event.user_id}]成功！ヾ(●´∇｀●)ﾉ哇～\n"
                        f"我准备的数字是 {int(base)}\n"
                        f"你一共猜了 {count} 次"
                    )
                )
            await start.reject(
                Message(f"[CQ:at,qq={event.user_id}]{str(stat)}")
            )
        except (TypeError, AttributeError, ValueError):
            await start.reject(
                Message(f"[CQ:at,qq={event.user_id}]输入无效，请重试！")
            )
    pass


@achievement.handle()
async def output_achievement(bot: Bot, event: MessageEvent):
    fp = f"../1a2b_hist/{event.user_id}"
    if not exists(fp):
        await achievement.finish(
            Message(
                f"[CQ:at,qq={event.user_id}]你还没有玩过猜数游戏呢！(ฅ>ω<*ฅ)\n"
                "不如搓几把看看？（（（"
            )
        )
    total, best, worst, average = read_data(event.user_id)
    await achievement.finish(
        Message(
            f"[CQ:at,qq={event.user_id}]总共进行了 {total} 把游戏_(:з」∠)_\n"
            f"平均：{average} 次；最好：{best} 次；最坏：{worst} 次"
        )
    )
