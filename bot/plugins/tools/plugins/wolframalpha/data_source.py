import httpx
from urllib.parse import urlencode

import nonebot

from .config import Config


global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

client = httpx.AsyncClient()


async def query_for_short_answer(i: str):
    res = await client.get(
        'https://api.wolframalpha.com/v1/result',
        params={'appid': plugin_config.wa_app_id, 'i': i}
    )
    return res.text


async def query_for_image_url(i: str):
    return 'https://data.huajitech.net:10443/api/wolframalpha/?' \
           + urlencode(
               {'key': plugin_config.wa_hjt_key, 'type': 'full', 'i': i}
           )
