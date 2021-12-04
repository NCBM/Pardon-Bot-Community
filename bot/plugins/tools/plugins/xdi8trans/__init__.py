import nonebot

from nonebot.rule import to_me
from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message

import re
from Xdi8Translator import Translator
import userlib

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Xdi8Translator",
    "希顶翻译",
    "希顶翻译 <翻译方向> <文本>\n"
    "可用的翻译方向：\n"
    "方向               含义\n"
    "h-x    汉希        汉字→希顶语\n"
    "x-h    希汉        希顶语→汉字\n"
    "x-i    希I         希顶语→IPA\n"
    "h-x-i  汉希I       汉字→希顶语→IPA"
)

tr = Translator()
tr_init = True

xdi8tr = on_command("希顶翻译", rule=to_me())


@xdi8tr.handle()
async def xdi8tr_handle(bot: Bot, event: MessageEvent):
    # help(event.get_message())
    msg = event.get_message().extract_plain_text().split(" ")
    # msg = ""
    if len(msg) > 0 and (msg[0] == "帮助" or msg[0] == "help"):
        await bot.send(message="[希顶翻译] 用法：希顶翻译 <翻译方向> <文本>\n"
                       "可用的翻译方向：\n"
                       "  方向      含义\n"
                       "  h-x 汉希 汉字→希顶语\n  x-h 希汉 希顶语→汉字\n"
                       "  x-i 希I 希顶语→IPA\n  h-x-i 汉希I 汉字→希顶语→IPA"
                       "",
                       event=event)
    elif len(msg) < 2:
        await bot.send(message="[希顶翻译] 需要两个参数：<翻译方向> <文本>",
                       event=event)
        # await bot.send(message="接收到内容：" + str(msg), event=event)
    else:
        tr_cmd = msg[0]
        tr_text = " ".join(msg[1:])
        global tr_init
        if tr_init:
            tr_init = False
            await bot.send(
                message="[希顶翻译] 翻译器首次使用需要初始化一段时间，请稍等",
                event=event
            )
        if tr_cmd == "h-x" or tr_cmd == "汉希":
            m_send = tr.hanzi2xdi8(tr_text)
            m_send_c = ""
        elif tr_cmd == "x-h" or tr_cmd == "希汉":
            m_send = ""
            m_send_c = tr.xdi82hanzi(tr_text)
        elif tr_cmd == "x-i" or tr_cmd == "希音":
            m_send = ""
            m_send_c = tr.xdi82IPA(tr_text)
        elif tr_cmd == "h-x-i" or tr_cmd == "汉希音":
            m_send = ""
            m_send_c = tr.xdi82IPA(tr.hanzi2xdi8(tr_text))
        else:
            m_send = ""
            m_send_c = "暂不支持的转换类型。发送 “希顶翻译 帮助” 获取帮助信息。"
        tmp = userlib.gen_tmp("xdi8-", ".png")
        if m_send:
            userlib.draw_img_from_text(
                (16 * 80 + 8, 32 * len(m_send) // 8 + 8),
                re.sub(r"\x08", r"", m_send), (tmp, "png"),
                userlib.fira_xdi8_32)
            await bot.send(message=Message(
                f"[CQ:image,file=file://{tmp}]"
            ), event=event)
        else:
            userlib.draw_img_from_text(
                (16 * 80 + 8, max(
                    32 * len(m_send_c) // 40 + 16,
                    32 * len(m_send_c.split("\n")) + 8
                )),
                re.sub(r"\x08", r"", m_send_c), ("xdi8.png", "png"),
                userlib.sarasa_f32)
            await bot.send(message=Message(
                f"[CQ:image,file=file://{tmp}]"
            ), event=event)
