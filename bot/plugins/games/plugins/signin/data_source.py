import httpx
import json

client = httpx.AsyncClient()


async def get_chicken_soup() -> str:
    res = await client.get("http://api.lkblog.net/ws/api.php")
    content = json.loads(res.text)
    return content["data"]
