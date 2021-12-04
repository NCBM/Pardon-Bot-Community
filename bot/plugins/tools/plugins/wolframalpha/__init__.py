import nonebot
from nonebot import Bot
from nonebot.adapters.cqhttp import MessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment
from nonebot.rule import to_me
from nonebot.typing import T_State

from .data_source import query_for_short_answer, query_for_image_url

from userlib.translation.baidu import BaiduTranslationError, BaiduTranslator, \
    BaiduTranslatorConfig

from .config import Config

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "WolframAlpha",
    "Wolfram|Alpha",
    "[获取短结果] 发送 \"@ + query + 查询内容 (英文)\"\n"
    "[获取带翻译的短结果] 发送 \"@ + 查询 + 查询内容 (任意语言)\"\n"
    "[获取详细结果] 发送 \"@ + fullquery + 查询内容 (英文)\""
)

query = nonebot.on_command('query', rule=to_me())
query_with_translation = nonebot.on_command('查询', rule=to_me())
query_full = nonebot.on_command('fullquery', rule=to_me())


global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())


@query.handle()
async def handle_query(bot: Bot, event: MessageEvent, state: T_State):
    i = str(event.get_message()).strip()
    if not i:
        await query.reject(
            MessageSegment.reply(event.message_id) +
            'What do you want to know about?'
        )
    await query.finish(
        MessageSegment.reply(event.message_id) +
        await query_for_short_answer(i)
    )


@query_with_translation.handle()
async def handle_query_with_translation(
    bot: Bot, event: MessageEvent, state: T_State
):
    i = str(event.get_message()).strip()
    if not i:
        await query_with_translation.reject(
            MessageSegment.reply(event.message_id) + '你想知道什么呢？'
        )

    try:
        translator = BaiduTranslator(BaiduTranslatorConfig(
            plugin_config.bdfy_app_id,
            plugin_config.bdfy_app_key
        ))
        input_translation_result = await translator.translate(i, 'en')
        answer = await query_for_short_answer(str(input_translation_result))

        await query_with_translation.finish(
            MessageSegment.reply(event.message_id) +
            str(await translator.translate(
                answer, input_translation_result.source_language
            ))
        )
    except BaiduTranslationError as ex:
        await query_with_translation.finish(
            MessageSegment.reply(event.message_id) +
            '翻译失败: ' + ex.message
        )


@query_full.handle()
async def handle_query_full(bot: Bot, event: MessageEvent, state: T_State):
    i = str(event.get_message()).strip()
    if not i:
        await query_full.reject(
            MessageSegment.reply(event.message_id) +
            'What do you want to know about?'
        )
    await query_full.finish(
        MessageSegment.reply(event.message_id) +
        MessageSegment.image(await query_for_image_url(i))
    )
