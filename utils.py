from io import BytesIO
from PIL import Image
from aiohttp import ClientSession
from nonebot.log import logger


async def open_img_from_url(url: str) -> Image.Image:
    logger.debug(f"start get picture, url: {url}")
    try:
        async with ClientSession() as client:
            resp = await client.get(url)
            logger.debug("picture got!")
            content = await resp.read()
        return Image.open(BytesIO(content)).convert("RGBA")
    except Exception as e:
        logger.error(e)
        return Image.new("RGBA", (0, 0))