from typing import Any
import nonebot
import os

from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message

import userlib

from enum import Enum

import httpx

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo("IPInfo", "IP信息", "IP信息 <IP 地址或域名>")

ipinfo = on_command("IP信息")

_client = httpx.AsyncClient()


class IpKind(Enum):
    UNKNOWN = 0
    PUBLIC = 1
    RESERVED = 2
    PRIVATE = 3


def _getIpKind(status: str, s: str) -> IpKind:
    if status == "success":
        return IpKind.PUBLIC
    if s == "reserved range":
        return IpKind.RESERVED
    if s == "private range":
        return IpKind.PRIVATE

    return IpKind.UNKNOWN


@ipinfo.handle()
async def ipinfo_escape(bot: Bot, event: MessageEvent):
    def boolToString(b: bool) -> str:
        return "是" if b else "否"

    parameters = event.get_message().extract_plain_text().split()

    if len(parameters) != 1:
        await bot.send(event, "[IP信息] 需要一个参数：<IP地址或域名>")
        return

    url = "http://ip-api.com/json/{}?lang=zh-CN&fields=status,message,"\
        "continent,continentCode,country,countryCode,region,regionName,"\
        "city,zip,lat,lon,timezone,currency,isp,org,as,asname,reverse,"\
        "mobile,proxy,hosting,query".format(parameters[0])

    res = await _client.get(url)
    result: dict[str, Any] = res.json()

    if "message" not in result.keys():
        ipKind = IpKind.UNKNOWN
    else:
        ipKind = _getIpKind(result["status"], result["message"])

    if ipKind == IpKind.PUBLIC:
        m_send = """IP {} 信息：
洲：{} ({})
国家：{} ({})
地区：{} ({})
城市：{}
邮政编码：{}
经纬度：{}, {}
时区：{}
货币单位：{}
ISP：{}
所属组织：{}
AS：{} ({})
反向 DNS：{}
移动数据接入：{}
代理：{}
托管/数据中心：{}""".format(
            result["query"], result["continent"], result["continentCode"],
            result["country"], result["countryCode"], result["regionName"],
            result["region"], result["city"], result["zip"], result["lat"],
            result["lon"], result["timezone"], result["currency"],
            result["isp"], result["org"], result["asname"], result["as"],
            result["reverse"], boolToString(result["mobile"]),
            boolToString(result["proxy"]), boolToString(result["hosting"]))
        tmp = userlib.gen_tmp("ipinfo-", ".png")
        userlib.draw_img_from_text((16 * 80, 32 * 24), m_send, (tmp, "png"),
                                   userlib.sarasa_f32)
        try:
            msg = Message("[CQ:image,file=file://{}]".format(tmp))
            await bot.send(message=msg, event=event)
        except:
            raise
        finally:
            os.remove(tmp)
    else:
        await bot.send(event, "IP {} 类型为：{}，无法获取详细信息！".format(
            result["query"], ipKind.name)
        )
