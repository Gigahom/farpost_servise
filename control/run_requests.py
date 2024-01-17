from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler

import requests
from lxml import html
import time
import os
from typing import Union
from uuid import UUID
import re

API_HOST = os.environ.get("API_HOST")
API_PORT = os.environ.get("API_PORT")
TG_API_KEY = os.environ.get("TG_API_KEY")

PREF_FARPOST = "/api/v1/farpost"

get_active_data_close_none = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_active_data_close_none"
update_cookies = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/update_cookies"
get_user_with_abs_active = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_user_with_abs_active?abs_active_id="
get_cookies_with_user = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_cookies_with_user?login="
get_telegram_chat_id = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_telegram_chat_id?login="

logger.add("log/log_control.log", rotation="2 MB")

scheduler = BackgroundScheduler(timezone="Europe/Moscow")


def prompt() -> None:
    requests.get(update_cookies)
    logger.info("Куки обновлены для всех пользователей")


scheduler.add_job(prompt, "interval", seconds=86400)
scheduler.start()


def send_telegram_message(chat_id: int, message: str):
    """
    Отправляет сообщение пользователю в Telegram.
    """
    if chat_id:
        url = f"https://api.telegram.org/bot{TG_API_KEY}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, json=payload)
        return response.json()


def is_api_available(url: str, max_attempts: int = 5, delay: int = 5) -> bool:
    """Проверяет доступность API.

    Args:
    - url (str): URL API для проверки.
    - max_attempts (int, optional): Максимальное количество попыток. По умолчанию 5.
    - delay (int, optional): Задержка между попытками в секундах. По умолчанию 5.

    Returns:
    - bool: True если API доступен, иначе False.
    """

    for _ in range(max_attempts):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(delay)
    return False


def parse_html_text(html_code: str) -> dict:
    """
    Метод для получения записей на страницы возвращаяет

    [(position, abs_id, position_active), ...]
    """

    html_parce = html.fromstring(html_code)

    list_link_id: list[int] = [
        int(i.split("-")[-1].split(".")[0])
        for i in html_parce.xpath(
            """//*[contains(concat( " ", @class, " " ), concat( " ", "bull-item__self-link", " " ))]/@href"""
        )
    ]
    list_item_price: list[float] = [
        float(i.split(":")[1].split("-")[0][2:])
        for i in html_parce.xpath(
            """//*[contains(concat( " ", @class, " " ), concat( " ", "bull-item__image-cell", " " ))]/@data-order-key"""
        )
    ]
    dict_items: dict = {}

    for i, id_item, price in zip(range(1, len(list_link_id) + 1), list_link_id, list_item_price):
        dict_items[f"{i}"] = {
            "abs_id": id_item,
            "price": price,
        }

    return dict_items


def find_item_number(data: dict, id_item: int) -> int | None:
    """
    Возвращает номер элемента, соответствующего заданному id_item, или None, если элемент не найден.
    """
    for number, item in data.items():
        if item.get("abs_id") == id_item:
            return int(number)
    return None


def check_position(position: int, dict_items: dict, abs_id: int, chat_id: int, item: dict) -> Union[None, float, int]:
    """Получение цены за позицию"""

    position_now = find_item_number(dict_items, abs_id)
    if position_now:
        if position_now > position:
            subcategories_link = "https://www.farpost.ru/" + item.get("attr")
            message = f"""Приклеенное объявление <a href='{item.get("link")}'>{item.get("name_farpost")}</a> снизилось с {position}-й до {position_now}-й позиции  в разделе <a href='{subcategories_link}'>{item.get("subcategories")}</a>"""
            send_telegram_message(chat_id=chat_id, message=message)

    position_item = dict_items.get(f"{position}")
    if position_item:
        if position_item.get("abs_id") != abs_id:
            if position_item.get("price") < 9999:
                return position_item.get("price") + 1
            else:
                return 10
        else:
            return None
    else:
        return None


def up_abs(
    abs_id: int, price: float, abs_active_id: UUID, position: int, cookies: dict, chat_id: int, item: dict
) -> None:
    """Поднятия на позицию"""

    while True:
        try:
            requests.get(
                f"https://www.farpost.ru/bulletin/service-configure?auto_apply=1&stickPrice={price}&return_to=&ids={abs_id}&applier=stickBulletin&stick_position%5B{abs_id}%5D=1&already_applied=1",
                cookies=cookies,
            )
            result = requests.get(f"https://www.farpost.ru/bulletin/{abs_id}/newstick?ajax=1", cookies=cookies)
            item_top = html.fromstring(result.text)
            text = item_top.xpath("//strong/text()")
            top = int(re.findall(r"\d+", text[0])[0])
            if top == position:
                break
        except:
            pass

    subcategories_link = "https://www.farpost.ru/" + item.get("attr")
    message = f"""Приклеенное объявление <a href='{item.get("link")}'>{item.get("name_farpost")}</a> поднялось до {position}-й позиции в разделе <a href='{subcategories_link}'>{item.get("subcategories")}</a> цена поднятия : {price}"""
    send_telegram_message(chat_id=chat_id, message=message)

    logger.info(f"Объявление : {abs_id} | Цена поднятия : {price} | Позиция сейчас : {top}")


def checking_position() -> None:
    """Основной цикал"""

    list_items_parse: list[dict] = [
        {
            "abs_id": i["abs_id"],
            "abs_active_id": i["abs_active_id"],
            "position": i["position"],
            "price_limitation": i["price_limitation"],
            "attr": i["category_attribute"],
            "name_farpost": i["name_farpost"],
            "link": i["link"],
            "subcategories": i["subcategories"],
        }
        for i in requests.get(url=get_active_data_close_none).json()
    ]

    for items in list_items_parse:
        common_headers = {
            "Host": "www.farpost.ru",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec_Fetch_Site": "same-origin",
            "Sec_Fetch_Mode": "navigate",
        }
        session = requests.Session()

        params1: dict = {"u": "/sign?return=%252F"}
        headers1: dict = common_headers.copy()
        headers1["Referer"] = "https://www.farpost.ru/verify?r=1&u=%2Fsign%3Freturn%3D%252F"
        session.get("https://www.farpost.ru/verify", params=params1, headers=headers1)

        params2: dict = {"return": "%2Fverify%3Fr%3D1%26u%3D%252Fsign%253Freturn%253D%25252F"}
        headers2: dict = common_headers.copy()
        headers2["Referer"] = "https://www.farpost.ru/verify?r=1&u=%2Fsign%3Freturn%3D%252F"
        session.get("https://www.farpost.ru/set/sentinel", params=params2, headers=headers2)

        user = requests.get(get_user_with_abs_active + items["abs_active_id"]).json()
        cookies = requests.get(get_cookies_with_user + user.get("login")).json()
        chat_id = requests.get(get_telegram_chat_id + user.get("login")).json()["telegram_id"]
        html_code = session.get(f"https://www.farpost.ru/" + items["attr"], cookies=cookies).text

        tree: html.HtmlElement = html.fromstring(html_code)
        title: str = tree.xpath("/html/head/title/text()")

        logger.debug("Название раздела для сбора : " + ",".join(title))

        dict_data = parse_html_text(html_code)

        price_up = check_position(items.get("position"), dict_data, items.get("abs_id"), chat_id, items)
        if price_up:
            if price_up < items.get("price_limitation"):
                up_abs(
                    items.get("abs_id"),
                    price_up,
                    items.get("abs_active_id"),
                    items.get("position"),
                    cookies,
                    chat_id,
                    items,
                )
        else:
            pass


if is_api_available(get_active_data_close_none):
    while True:
        checking_position()
else:
    logger.error("API недоступно.")
