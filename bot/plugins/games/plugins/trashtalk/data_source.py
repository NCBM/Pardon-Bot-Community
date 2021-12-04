import httpx

client = httpx.AsyncClient()


async def get_trash_talk() -> str:
    res = await client.get("https://api.shadiao.app/nmsl?level=min")
    return res.json()["data"]["text"]
