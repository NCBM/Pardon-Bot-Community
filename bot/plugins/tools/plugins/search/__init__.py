import nonebot

from nonebot.adapters.cqhttp import Bot, MessageEvent, Message
from nonebot.plugin import on_command
from urllib import parse

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Search",
    "搜索",
    "[百度搜索] 搜 <关键词>\n"
    "[必应搜索] 必应搜 <关键词> (必应)"
)

SEARCH_ENGINES = {
    "百度": "https://www.baidu.com/s?wd=",
    "必应": "https://www.bing.com/search?q="
}

search = on_command("搜")
bing_search = on_command("必应搜")


def generic_processor(engine: str, content: str):
    if len(content) < 1:
        m_send = "[搜索] 需要参数：<搜索内容>"
    else:
        m_send = "[CQ:share,url={},title={}一下，你就知道,content={}]"\
            .format(
                SEARCH_ENGINES[engine] + parse.quote(content),
                engine, content)
    return m_send


@search.handle()
async def search_escape(bot: Bot, event: MessageEvent):
    msg = event.get_message().extract_plain_text()
    m_send = generic_processor("百度", msg)
    await bot.send(message=Message(m_send), event=event)


@bing_search.handle()
async def bing_search_escape(bot: Bot, event: MessageEvent):
    msg = event.get_message().extract_plain_text()
    m_send = generic_processor("必应", msg)
    await bot.send(message=Message(m_send), event=event)
