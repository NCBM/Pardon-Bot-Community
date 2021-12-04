import nonebot
from nonebot import get_driver
from nonebot.adapters.cqhttp.message import Message
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from .config import Config
from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent

from userlib.translation import T_Translator, TranslationError
from userlib.translation.baidu import BaiduTranslator, BaiduTranslatorConfig

import os
import userlib

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Translator",
    "翻译",
    "支持 \"百度翻译\"\n"
    "发送相应翻译器名称即可使用"
)

global_config = get_driver().config
plugin_config = Config(**global_config.dict())


async def _first_handle(
    translator: T_Translator,
    matcher: type[Matcher],
    event: MessageEvent,
    state: T_State
):
    msg = event.get_message().extract_plain_text().strip()
    if "started" not in state:
        state["started"] = True
        await matcher.reject("请输入源语言 (e.g. zh, en) (auto 指示自动识别): ")
    if "src" not in state:
        state["src"] = msg
        await matcher.reject("请输入目标语言 (e.g. zh, en): ")
    if "dest" not in state:
        state["dest"] = msg
        await matcher.reject("请输入待翻译内容: ")

    try:
        src = state["src"]
        result = await translator.translate(
            msg,
            state["dest"],
            None if src == "auto" else src
        )
    except TranslationError as ex:
        await matcher.send(
            "翻译失败(；′⌒`)\n" +
            getattr(ex, "message", "错误状态码：%s" % ex.code)
        )
        raise

    text = result.translated_text

    if len(text) < 128:
        await matcher.finish("翻译结果：\n" + text)
    else:
        await matcher.send("翻译完成！请耐心等待图片生成ヾ(๑╹◡╹)ﾉ\"")
        tmp = userlib.gen_tmp("translator-", ".png")
        try:
            userlib.draw_img_from_text(
                (16 * 80 + 2, int(34 * max(text.count("\n") * 2, 24)) + 1),
                text, (tmp, "png"), userlib.sarasa_f32
            )
            await matcher.send(Message("[CQ:image,file=file://%s]" % tmp))
        except Exception as ex:
            await matcher.send("处理数据时，发生了意料之外的错误/(ㄒoㄒ)/~~")
            await matcher.send(getattr(ex, "message", str(ex)))
            raise
        finally:
            os.remove(tmp)


baidu = on_command("百度翻译")
baidu_translator = BaiduTranslator(BaiduTranslatorConfig(
    plugin_config.bdfy_app_id, plugin_config.bdfy_app_key
))


@baidu.handle()
async def baidu_handle(bot: Bot, event: MessageEvent, state: T_State):
    await _first_handle(baidu_translator, baidu, event, state)
