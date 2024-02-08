from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from requests import get
import importlib

from utilities.const import UrlsEnums
from utilities.logs import custom_sink

logger.add(custom_sink, format="{time} | {message}")


scheduler = BackgroundScheduler(timezone="Asia/Vladivostok")


def prompt() -> None:
    get(UrlsEnums.update_cookies.value)
    logger.info("Куки обновлены для всех пользователей")


scheduler.add_job(prompt, "interval", seconds=10800)
