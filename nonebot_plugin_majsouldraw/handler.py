from nonebot.rule import to_me
from nonebot.plugin import on_command
from nonebot.rule import regex
from nonebot.plugin import on_message
from nonebot import logger
import random, time, json
from pathlib import Path
import numpy as np
from PIL import Image
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    MessageEvent,
    ActionFailed
)

datadir: Path = Path(__file__).parent / "json"

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
query = on_message(rule=regex(r"抽卡记录"), priority=1, block=False)

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
    result_data = [] # 1：角色，2：装扮，3：紫色礼物，4：绿/蓝礼物
    flag = 0
    for i in range(10):
        p = random.randint(1,100)
        if p <= 5:
            result.append(draw_one(personlist))
            result_data.append(1)
            flag = 1
        elif p <= 20:
            result.append(draw_one(decolist))
            result_data.append(2)
        else:
            p = random.randint(1,10000)
            if p <= 625:
                result.append(draw_one(purplelist))
                result_data.append(3)
                flag = 1
            else:
                result.append(draw_one(giftlist))
                result_data.append(4)
    if not flag:
        result.pop()
        result_data.pop()
        p = random.randint(1,2)
        if p == 1:
            result.append(draw_one(purplelist))
            result_data.append(3)
        else:
            result.append(draw_one(personlist))
            result_data.append(1)
    count = [1, 0, 0, 0, 0]
    for i in result_data:
        count[i] += 1
    return [merge_image(result), count]

def add(data1, data2):
    for i in range(5):
        data1[i] += data2[i]
    return data1

@query.handle()
async def query_function(event: MessageEvent):
    logger.info("majsoul query matched!")
    _time = int(time.strftime("%Y%m%d", time.localtime()))
    uid = str(event.user_id)

    data = {}
    data_today = {}
    
    with open(datadir / "data.json",'r+') as f:
        data = json.load(f)
    with open(datadir / "data_today.json",'r+') as f:
        data_today = json.load(f)

    if "date" not in data_today or data_today["date"] != _time:
        data_today.clear()
        data_today["date"] = _time

    if uid not in data:
        data[uid] = [0, 0, 0, 0, 0]

    if uid not in data_today:
        data_today[uid] = [0, 0, 0, 0, 0]
    
    data = data[uid]
    data_today = data_today[uid]
    
    await majsouldraw.send(f"{event.sender.card or event.sender.nickname or uid}的总抽卡记录：\n十连次数：{data[0]}\n抽出角色数：{data[1]}\n抽出装扮数：{data[2]}\n抽出紫礼物数：{data[3]}\n抽出蓝/绿礼物数：{data[4]}\n")
    await majsouldraw.finish(f"{event.sender.card or event.sender.nickname or uid}的今日抽卡记录：\n十连次数：{data_today[0]}\n抽出角色数：{data_today[1]}\n抽出装扮数：{data_today[2]}\n抽出紫礼物数：{data_today[3]}\n抽出蓝/绿礼物数：{data_today[4]}\n")


@majsouldraw.handle()
async def handle_function(event: MessageEvent):
    logger.info("majsouldraw matched!")

    _time = int(time.strftime("%Y%m%d", time.localtime()))
    uid = str(event.user_id)

    data = {}
    data_today = {}
    
    with open(datadir / "data.json",'r+') as f:
        data = json.load(f)
    with open(datadir / "data_today.json",'r+') as f:
        data_today = json.load(f)

    if "date" not in data_today or data_today["date"] != _time:
        data_today.clear()
        data_today["date"] = _time

    if uid not in data:
        data[uid] = [0, 0, 0, 0, 0]

    if uid not in data_today:
        data_today[uid] = [0, 0, 0, 0, 0]

    [img, result] = draw_ten()

    data[uid] = add(data[uid], result)
    data_today[uid] = add(data_today[uid], result)

    with open(datadir / "data.json",'w+') as f:
        json.dump(data, f, ensure_ascii=False)
    with open(datadir / "data_today.json",'w+') as f:
        json.dump(data_today, f, ensure_ascii=False)

    if img:
        logger.info("draw succeeded")
        await majsouldraw.finish(MessageSegment.image(img.read_bytes()))
    else:
        logger.info("draw failed")
        await majsouldraw.finish("抽卡失败，请联系管理员")