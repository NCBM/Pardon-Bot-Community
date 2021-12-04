import nonebot
from .data_source import get_trash_talk

from nonebot.rule import to_me
from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo("TrashTalk", "垃圾话", "[垃圾话] @ + 垃圾话")

trashtalk = on_command("垃圾话", rule=to_me())


@trashtalk.handle()
async def trashtalk_handle(bot: Bot):
    await trashtalk.send(await get_trash_talk())
