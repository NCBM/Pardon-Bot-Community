"""
Nonebot2 Custom Tools

Provide a series of tools for using nonebot2
"""
from random import choice

from nonebot.adapters.cqhttp.bot import Bot


with open("../fortune/banned") as ban:
    BANNED = ban.read().split("\n")


try:
    # import nonebot
    from dataclasses import dataclass
    from nonebot.adapters.cqhttp.event import GroupMessageEvent, \
        PrivateMessageEvent
    from nonebot.adapters.cqhttp import MessageEvent, Message

    @dataclass
    class Source:
        event_type: str
        number: int

        def __hash__(self) -> int:
            return hash(self.event_type + "." + str(self.number))

    def get_source(event: MessageEvent) -> Source:
        if isinstance(event, GroupMessageEvent):
            return Source("GroupMessageEvent", event.group_id)
        elif isinstance(event, PrivateMessageEvent):
            return Source("PrivateMessageEvent", event.user_id)
        else:
            raise Exception("Invalid event type.")

    async def chk_banned(bot: Bot, event: MessageEvent):
        # 检查用户是否被禁止
        if str(event.user_id) in BANNED:
            await bot.send(
                message=Message(
                    f"[CQ:at,qq={event.user_id}]"
                    + choice(["我不整！", "你给我滚！", "去你的！", "草",
                              "就离谱"])
                ),
                event=event
            )
            # await bot.call_api("set_group_ban", group_id=event.group_id,
            #                    user_id=event.user_id, duration=5)
            raise Exception("fuck it.")
except ImportError:
    print("[nbtool] Failed to import 'nonebot', skipped.")
