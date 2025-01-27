from nonebot.rule import to_me
from nonebot.plugin import on_command
from nonebot.rule import regex
from nonebot.plugin import on_message
from nonebot import logger
import random

majsouldraw = on_message(rule=regex("雀魂十连"), priority=1, block=False)

@majsouldraw.handle()
async def handle_function():
    logger.info("majsouldraw matched!")
    await majsouldraw.finish(str(random.randint(1,10)))