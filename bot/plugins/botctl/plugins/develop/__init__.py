import nonebot
from nonebot import get_driver

from .config import Config

from nonebot.rule import to_me
from nonebot.plugin import on_command, on_message
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message

import os
import sys
import subprocess
# from apscheduler.schedulers.background import BackgroundScheduler

import userlib

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Development Toolkit",
    "开发工具箱",
    "[状态] @ + 状态\n"
    "[反馈] @ + 如何反馈\n"
    "(开发者) [停机] @ + 停机\n"
    "(开发者) [挂起] @ + 挂起\n"
    "(开发者) [恢复] @ + 恢复\n"
    "(开发者) [切换分支] @ + 切换分支 [目标分支]"
)

global_config = get_driver().config
plugin_config = Config(**global_config.dict())

# 开发者工具

COMMIT_BITS = 8
FEEDBACK_MAIL = """
contact-project+pardon-na-pardon-bot-feedback@proj.zone
"""[1:-1]
# updater = BackgroundScheduler()
# updater.start()
#
#
# def autopush():
#     subprocess.run(["git", "add", "."])
#     subprocess.run(["git", "commit", "-m", "Auto push."])
#     subprocess.run(["git", "push"])
#
#
# updater.add_job(autopush, trigger="cron", id="autopush", day="*",
#                 minute="*/15")

bstop = on_command("停机", rule=to_me())


async def check_perm(bot: Bot, event: MessageEvent):
    if event.user_id not in plugin_config.developers.values()\
            and event.user_id not in plugin_config.extra_manager:
        await bot.send(message="操作失败：权限不足", event=event)
        raise PermissionError()


def get_branch():
    current_b = subprocess.run(["git", "branch"], capture_output=True)
    branches = current_b.stdout.decode().split("\n")
    return [br for br in branches if "*" in br][0][2:]


@bstop.handle()
async def bstop_escape(bot: Bot, event: MessageEvent):
    # 机器人停止运行
    await check_perm(bot, event)
    await bot.send(message="即将停机", event=event)
    # subprocess.run(["sudo", "pkill", "nb"])
    sys.exit(0)

info = on_command("信息", rule=to_me())


@info.handle()
async def status_escape(bot: Bot, event: MessageEvent):
    branch = get_branch()
    m_send = f"目前位于 [{branch}/"
    gst_proc = subprocess.run(["git", "log", "-1", "--pretty=format:%H"],
                              capture_output=True)
    m_send += gst_proc.stdout.decode()[:COMMIT_BITS]
    ver = plugin_config.version
    m_send += "] | 版本 %d.%d.%d.%d\n" % (ver[0], ver[1], ver[2], ver[3])
    pyver = sys.version_info
    m_send += "工作于 Python %d.%d.%d\n" % (pyver.major, pyver.minor, pyver.micro)
    developers = plugin_config.developers.keys()
    m_send += "开发者: " + ", ".join(developers)
    tmp = userlib.gen_tmp("status-", ".png")
    try:
        userlib.draw_img_from_text(
            (8 * 80 + 4, 18 * len(m_send.split("\n")) + 8), m_send,
            (tmp, "png"), userlib.unifont16)
        await bot.send(message=Message(
            "[CQ:image,file=file://{}]".format(tmp)
        ), event=event)
    except Exception:
        raise
    finally:
        os.remove(tmp)

feedback = on_command("如何反馈", rule=to_me())


@feedback.handle()
async def feedback_h(bot: Bot, event: MessageEvent):
    await bot.send(
        event,
        f"现在你可以通过向 {FEEDBACK_MAIL} 发送邮件来进行反馈\n"
        "你可以通过此方式反馈一个 bug 或一个新功能请求"
    )
    pass


hangup = on_message(priority=-1, block=False)


@hangup.handle()
async def hangup_escape(bot: Bot, event: MessageEvent):
    msg = event.get_message().extract_plain_text()
    if event.to_me and msg == "挂起" and not hangup.block:
        await check_perm(bot, event)
        hangup.block = True
        await bot.send(event, "已挂起，直到恢复之前都不会响应消息")
    elif event.to_me and msg == "恢复" and hangup.block:
        await check_perm(bot, event)
        hangup.block = False
        await bot.send(event, "已恢复消息响应")

chbranch = on_command("切换分支", rule=to_me())


@chbranch.handle()
async def chbranch_escape(bot: Bot, event: MessageEvent):
    branch = event.get_message().extract_plain_text()
    if not branch:
        branch = "master"
    await check_perm(bot, event)
    subprocess.run(["git", "checkout", branch])
    cur_branch = get_branch()
    await bot.send(event, f"已尝试切换。\n目前所在的分支为 {cur_branch}")
