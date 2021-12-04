import nonebot
from nonebot.adapters.cqhttp.event import GroupMessageEvent

from nonebot.rule import to_me
from nonebot.plugin import on_message, on_command
from nonebot.adapters.cqhttp import Bot

import time
import string

import asyncio
from apscheduler.schedulers.background import BackgroundScheduler

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Clock",
    "时间",
    "[现在北京时间] @ + （现在）几点了？ (支持几点, 时间, 几时, 何时的模糊匹配)\n"
    "[初始化报时] @ + 初始化报时"
)

clock = BackgroundScheduler()
clock.start()

week2chs = "一二三四五六日"

now = on_message(rule=to_me())
event_init = on_command("初始化报时", rule=to_me())


def clockman15(bot: Bot, event: GroupMessageEvent):
    asyncio.run(bot.send(
        message="喂！三点几嘞！做，做卵啊做！饮茶先啊！三点几，饮，饮茶先啊！"
        "做咁做都冇用嘞，老细唔锡你嘅嘞！喂饮下茶先啦！三点几嘞！做碌狗啊做！",
        event=event
    ))


def clockman19(bot: Bot, event: GroupMessageEvent):
    asyncio.run(bot.send(
        message="喂！朋友！做咩咁多啦！差唔多七点咧，放工啦 唔洗做咁多啦！"
        "做咁多，钱带去边度？差唔多七点咧！放工！焗杯茶先！饮下靓靓个beer！"
        "白啤酒黑啤酒ok？happy下唔洗做咁多！死佐都无用诶，银纸无得带去咧！"
        "happy下！饮酒！ok？！\n（温馨提示：未成年人请勿饮酒！饮酒有害健康！）",
        event=event
    ))


# def _char_swap(text: str, first: str, second: str):
#     assert len(first) == 1 and len(second) == 1
#     result = ""

#     for char in text:
#         if char == first:
#             result += second
#         elif char == second:
#             result += first
#         else:
#             result += char

#     return result


# def _get_prefix(text: str, keywords: list[str]):
#     last_pos = len(text)

#     for keyword in keywords:
#         current_pos = text.find(keyword)
#         if current_pos != -1 and last_pos > current_pos:
#             last_pos = current_pos

#     return _char_swap(text[:last_pos], "你", "我")


@now.handle()
async def now_escape(bot: Bot, event: GroupMessageEvent):
    plain = event.message.extract_plain_text().strip()
    chinese_punctuation = ("！？｡＂＃＄％＆＇（）＊＋－／：；＜＝＞＠［＼］＾＿｀｛｜｝"
                           "～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘'‛“”„‟…‧﹏")

    keywords = ["几点", "时间", "几时", "何时"]
    punctuation = string.punctuation + chinese_punctuation
    contains = True in \
        [word in plain for word in keywords]

    if contains or plain == "现在" or \
        ("现在" in plain and False not in
            [char in punctuation for char in plain.replace("现在", "")]):
        tnow = time.localtime()
        weekd = week2chs[tnow.tm_wday]
        # prefix = _get_prefix(plain, keywords) if contains else "现在"

        await bot.send(message=f"现在是 北京时间 {tnow.tm_year}年{tnow.tm_mon}月"
                       f"{tnow.tm_mday}日（今年第{tnow.tm_yday}天） 星期{weekd} "
                       f"{tnow.tm_hour}时{tnow.tm_min}分{tnow.tm_sec}秒",
                       event=event)


@event_init.handle()
async def event_init_escape(bot: Bot, event: GroupMessageEvent):
    clock.add_job(clockman15, args=(bot, event), trigger="cron", jitter=30,
                  id="3oclock_{}".format(event.group_id), day="*", hour="3,15")
    clock.add_job(clockman19, args=(bot, event), trigger="cron", jitter=30,
                  id="7oclock_{}".format(event.group_id), day="*", hour="7,19")
    await bot.send(message="已在本群初始化 3:00, 7:00, 15:00, 19:00", event=event)
