import nonebot

from nonebot.rule import to_me
from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message

import subprocess
import re
import os
# from wcwidth import wcswidth

import userlib

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Qalculate calculator",
    "计算器",
    "[计算] @ + 计算 <表达式>\n"
    "[更新汇率] @ + 更新汇率"
)


# def wc_max(*args):
#     """计算最长行长度（只针对等宽字体）"""
#     if len(args) == 1:
#         args = args[0]
#     lines = [wcswidth(s) for s in args]
#     return max(lines)


fchs_conv = [
    [r"（", r"("], [r"）", r")"], [r"＝", r"="], [r"\r", r""],
    [r"！", r"!"], [r"＜", r"<"], [r"＞", r">"], [r"＋", r"+"],
    [r"－", r"-"], [r"　", r" "], [r"＾", r"^"], [r"arc", r"a"]
]  # 字符转换映射关系

calc = on_command("计算", rule=to_me())
currency = on_command("更新汇率", rule=to_me())


@calc.handle()
async def calc_escape(bot: Bot, event: MessageEvent):
    msg = event.get_message().extract_plain_text()
    if len(msg) < 1:
        m_send = "[计算器] 需要一个参数：<计算内容>"
    elif len(msg) > 145:
        m_send = "[计算器] 拒绝计算：过长的算式（超过145个字符）\n"
    else:
        m_send = ""
        if msg == "帮助":
            msg = "help"
        # 为避免可能的意外影响，这里通过重初始化复制字符串
        msg_ = str(msg)
        for src, dst in fchs_conv:
            # 逐步替换全角符号为半角符号
            msg_ = re.sub(src, dst, msg_)
        if msg_ != msg:
            m_send += "警告：发生输入转换！可能是使用了默认不被支持的全角符号，"\
                "其会被转换为受支持的半角符号……\n"
        # 通过命令行调用 qalc
        proc = subprocess.run(["bash", "-c", "LANG=zh_CN.UTF-8 qalc -u8"],
                              input=msg_.encode(), capture_output=True)
        if "exit" not in m_send:
            m_send += proc.stdout.decode()[:-3]
        else:
            m_send += proc.stdout.decode()[:-1]
        if "\033" in m_send:
            m_send = "警告：暂不支持 ANSI 字符样式，可能会出现显示异常\n" + m_send
    tmp = userlib.gen_tmp("calc-", ".png")
    try:
        # 生成图片
        userlib.draw_img_from_text(
            (8 * 84 + 4, 16 * len(m_send.split("\n")) + 4), m_send,
            (tmp, "png"), userlib.unifont16
        )
        await bot.send(message=Message(
            "[CQ:image,file=file://{}]".format(tmp)
        ), event=event)
    except:
        raise
    finally:
        os.remove(tmp)


@currency.handle()
async def currency_escape(bot: Bot, event: MessageEvent):
    await bot.send(message="正在更新汇率，这可能需要一段时间", event=event)
    # 调用更新汇率
    status = userlib.utils.qalc_update_exchange_rates()
    if status == 0:
        await bot.send(message="汇率更新成功", event=event)
    else:
        await bot.send(message="汇率更新失败", event=event)
