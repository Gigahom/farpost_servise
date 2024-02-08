from requests import get
import importlib

from utilities.competitors import control_competitors, find_item_number
from utilities.const import UrlsEnums
from utilities.tg import send_telegram_message
from loguru import logger

from utilities.logs import custom_sink

logger.add(custom_sink, format="{time} | {message}")


def check_position(position: int, dict_items: dict, abs_id: int, chat_id: int, item: dict) -> None | float | int:
    """Получение цены за позицию"""

    competitor = None
    if item.get("competitor_id"):
        competitor = control_competitors(abs_id=abs_id, dict_items=dict_items, competitor_id=item.get("competitor_id"))

    position_item = dict_items.get(f"{position}")
    position_item_last = dict_items.get(f"{position+1}")

    price_up = None

    if not position_item and not position_item_last:
        price_up = 10.0

    if position_item and int(position_item.get("abs_id")) == abs_id:
        if position_item_last:
            price_up = position_item_last.get("price") + 1
        else:
            price_up = None

    logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(file_name="position_now").info(
        find_item_number(dict_items, abs_id)
    )

    if position_item and int(position_item.get("abs_id")) != abs_id:
        position_now = find_item_number(dict_items, abs_id)
        if position_now and position_now > position:
            if item.get("is_up"):
                subcategories_link = "https://www.farpost.ru/" + item.get("attr")
                message = f"""Приклеенное объявление <a href='{item.get("link")}'>{item.get("name_farpost")}</a> снизилось с {position}-й до {position_now}-й позиции  в разделе <a href='{subcategories_link}'>{item.get("subcategories")}</a>"""
                send_telegram_message(chat_id=chat_id, message=message)
                get(UrlsEnums.stop_tracking.value + item.get("abs_active_id"))

        price_up = position_item.get("price") + 1

    if not position_item:
        price_up = 10

    if not competitor:
        return price_up
    else:
        if price_up > competitor:
            logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(
                file_name="competitor_stop"
            ).info("Обгон конкурента выключен")
            return price_up
        else:
            logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(
                file_name="competitor_start"
            ).info("Обгон конкурента включен")
            return competitor
