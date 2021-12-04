from typing import Any
import nonebot
from .data_source import get_chicken_soup

from nonebot.rule import to_me
from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message
import userlib
import time
import os
from random import randint

from userlib.plugin import PluginInfo

import json

export = nonebot.export()
export.info = PluginInfo("Sign-in", "签到", "[签到] @ + 签到")

RAW_MSG_SEND_LIMIT = 32
PATH = "../signin.json"

signin = on_command("签到", rule=to_me())


async def gen_msg(date: str, event: MessageEvent, continuous: bool):
    chicken_soup = await get_chicken_soup()
    msg = f"[CQ:at,qq={event.user_id}]"
    msg += f"成功在 {date} 签到\n"
    if continuous:
        msg += "今天是勤奋的连续签到的你！加油！\n"
    msg += "今天的占卜结果是：五行缺" + \
        ["德", "打", "钱", "智商", "心眼"][randint(0, 4)] + "\n"
    msg += "每日鸡汤：" + chicken_soup
    return msg


@signin.handle()
async def signin_escape(bot: Bot, event: MessageEvent):
    action_t = time.localtime()
    date = f"{action_t.tm_year}年{action_t.tm_mon}月{action_t.tm_mday}日"
    # *** OLD IMPLEMENT ***
    # targetf = "../signin_stamps/{}".format(event.user_id)
    # if not exists(targetf):
    #     ftouch(targetf)
    #     msg = await gen_msg(date, event, False)
    # else:
    #     file_t = localtime(fgetmtime(targetf))
    #     f_date = (file_t.tm_year, file_t.tm_yday)
    #     if a_date != f_date:
    #         ftouch(targetf)
    #         msg = await gen_msg(
    #             date, event,
    #             a_date[1] - f_date[1] == 1 or
    #             a_date[0] - f_date[0] == 1
    #         )
    #     else:
    #         date_s = f"{file_t.tm_year}年{file_t.tm_month}月{file_t.tm_mday}日"
    #         msg = "[CQ:at,qq={}]似乎已经在 {} 签过到了……"\
    #             .format(event.user_id, date_s)
    msg = None
    infos = None
    if os.path.exists(PATH):
        with open(PATH, "r") as file:
            try:
                infos = json.load(file)
            except:
                pass
    if infos is None:
        infos = list[dict[str, Any]]()
    with open(PATH, "w") as file:
        uid = event.user_id
        for info in infos:
            if info["uid"] == uid:
                record_time = time.localtime(info["time"])
                if (record_time.tm_year, record_time.tm_yday) \
                        == (action_t.tm_year, action_t.tm_yday):
                    msg = "[CQ:at,qq={}]似乎已经签过到了……".format(event.user_id)
                else:
                    info["time"] = int(time.time())
                    msg = await gen_msg(
                        date,
                        event,
                        action_t.tm_yday - record_time.tm_yday == 1
                    )
        if msg is None:
            infos.append({"uid": uid, "time": int(time.time())})
            msg = await gen_msg(date, event, False)
        json.dump(infos, file)
    tmp = userlib.gen_tmp("fortune-", ".png")
    try:
        await bot.send(message=Message(msg), event=event)
    except:
        msgerr = "[签到] 发生运行时错误\n"
        userlib.draw_img_from_text((16 * 80 + 2, 33 * 8 + 1),
                                   msgerr, (tmp, "png"), userlib.sarasa_f32)
        msg = Message("[CQ:image,file=file://{}]".format(tmp))
        await bot.send(message=msg, event=event)
        raise
    finally:
        # Remove tmp, Bot strong!
        # shout it out when you play the music 'Serbia strong'.
        os.remove(tmp)
