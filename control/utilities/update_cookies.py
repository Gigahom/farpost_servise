from apscheduler.schedulers.background import BackgroundScheduler

from requests import get
import importlib

from utilities.const import UrlsEnums

scheduler = BackgroundScheduler(timezone="Asia/Vladivostok")


def prompt() -> None:
    logger = importlib.import_module("main.logger")
    get(UrlsEnums.update_cookies.value)
    logger.info("Куки обновлены для всех пользователей")


scheduler.add_job(prompt, "interval", seconds=10800)
