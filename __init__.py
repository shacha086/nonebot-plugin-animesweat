import base64
from io import BytesIO
import traceback
from typing import List
from pathlib import Path
import nonebot
import animeface
from PIL import Image
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.adapters.onebot.v11.event import Reply
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11.helpers import extract_image_urls

from plugins.nonebot_plugin_animesweat.utils import open_img_from_url
matcher = nonebot.on_command("流汗")

@matcher.handle()
async def _(bot: Bot, event: MessageEvent):
    if not event.reply:
        return
    
    reply: Message = event.reply.message
    image_urls: List[str]
    if not (image_urls:=extract_image_urls(reply)):
        await matcher.finish("你没发图🙂")

    images: List[Image.Image] = [await open_img_from_url(image) for image in image_urls]

    has_least_one_face = False
    for image in images:
        faces = animeface.detect(image)
        if not faces:
            continue
        has_least_one_face = True
        for face in faces:
            droplet = Image.open(Path(__file__).parent.absolute()/"droplet.png")
            PROPORTION = 0.4
            max_width = face.face.pos.width * PROPORTION
            max_height = face.face.pos.height * PROPORTION
            ratio = max(max_width / droplet.width, max_height / droplet.height)
            droplet = droplet.resize(
                (int(droplet.width * ratio), int(droplet.height * ratio)), 
                resample=Image.ANTIALIAS
            )

            left_eye_x = face.left_eye.pos.x
            left_eye_y = face.left_eye.pos.y
            droplet_x = int(left_eye_x + face.left_eye.pos.width * 0.4)
            droplet_y = int(left_eye_y - face.left_eye.pos.height * 1.3)
            image.alpha_composite(
                droplet,
                (droplet_x, droplet_y)
            )
    
    if not has_least_one_face:
        await matcher.finish("这张图片里面没有识别到任何脸，换一张试试？")
    
    message = Message()
    for image in images:
        buffer = BytesIO()
        image.save(buffer, 'PNG')
        message += MessageSegment.image(buffer)

    await matcher.finish(message=message)