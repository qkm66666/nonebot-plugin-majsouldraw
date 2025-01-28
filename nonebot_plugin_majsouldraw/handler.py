from nonebot.rule import to_me
from nonebot.plugin import on_command
from nonebot.rule import regex
from nonebot.plugin import on_message
from nonebot import logger
import random
from pathlib import Path
import numpy as np
from PIL import Image
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    MessageEvent,
    ActionFailed
)

imagedir: Path = Path(__file__).parent / "Images"

jeweldir: Path = imagedir / "jewel"
jewellist: list[Path] = [i for i in jeweldir.rglob(r'*')]

decodir: Path = imagedir / "decoration"
decolist: list[Path] = [i for i in decodir.rglob(r'*')]

giftdir: Path = imagedir / "gift"
giftlist: list[Path] = [i for i in giftdir.rglob(r'*')]

persondir: Path = imagedir / "person"
personlist: list[Path] = [i for i in persondir.rglob(r'*')]

purpledir: Path = imagedir / "purplegift"
purplelist: list[Path] = [i for i in purpledir.rglob(r'*')]

majsouldraw = on_message(rule=regex(r"雀魂十连"), priority=1, block=False)

def draw_one(srclist):
    if not srclist:
        return None
    else:
        return random.choice(srclist)

img_size = 170

def merge_image(result):
    result_img = Image.new("RGB", (img_size * 5, img_size * 2))
    for i in range(2):
        for j in range(5):
            id = i * 5 + j
            img = Image.open(result[id])
            img = img.resize((img_size, img_size))
            result_img.paste(img, (j * img_size, i * img_size))
    result_img.save(imagedir / "result.jpg")
    return imagedir / "result.jpg"

def draw_ten():
    result = []
    flag = 0
    for i in range(10):
        p = random.randint(1,100)
        if p <= 5:
            result.append(draw_one(personlist))
            flag = 1
        elif p <= 20:
            result.append(draw_one(decolist))
        else:
            p = random.randint(1,10000)
            if p <= 625:
                result.append(draw_one(purplelist))
                flag = 1
            else:
                result.append(draw_one(giftlist))
    if not flag:
        result.pop()
        p = random.randint(1,2)
        if p == 1:
            result.append(draw_one(purplelist))
        else:
            result.append(draw_one(personlist))
    return merge_image(result)

@majsouldraw.handle()
async def handle_function():
    logger.info("majsouldraw matched!")
    img = draw_ten()
    if img:
        logger.info("draw succeeded")
        await majsouldraw.finish(MessageSegment.image(img.read_bytes()))
    else:
        logger.info("draw failed")
        await majsouldraw.finish("抽卡失败，请联系管理员")