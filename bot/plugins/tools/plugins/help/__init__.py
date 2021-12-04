import nonebot
from nonebot.plugin import get_loaded_plugins, on_command
from nonebot.adapters.cqhttp import Bot, Message
from nonebot.rule import to_me

from userlib.plugin import PluginInfo

import userlib

export = nonebot.export()
export.info = PluginInfo("Help", "帮助菜单", "@ + 帮助")

image = None
help = on_command("帮助", rule=to_me())


@help.handle()
async def help_handle(bot: Bot):
    global image
    if image is None:
        await help.send("第一次使用帮助，正在生成图片，请耐心等待 (〃'▽'〃)")
        image = generate_help_image()

    await help.send(Message("[CQ:image,file=file://%s]" % image))


def generate_help_image() -> str:
    plugins = get_loaded_plugins()

    infos: list[PluginInfo] = [
        plugin.export.info for plugin in plugins if "info" in plugin.export
    ]
    infos.sort(key=lambda info: info.name)

    text = [
        f"● {info.name} ({info.description}):\n" +
        "\n".join([" " * 4 + line for line in info.usage.splitlines(False)])
        for info in infos
    ]

    tmp = userlib.gen_tmp("help-", ".png")
    width = 17 * 80 + 2
    height = 44 * len(text) * 4 + 2
    userlib.draw_img_from_text(
        (width, height), "\n".join(text), (tmp, "png"),
        userlib.sarasa_f32, margin=2
    )
    return tmp
