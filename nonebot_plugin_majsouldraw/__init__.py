from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

from .handler import majsouldraw

__plugin_meta__ = PluginMetadata(
    name="majsouldraw",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

