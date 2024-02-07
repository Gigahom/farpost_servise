from loguru import logger

import requests
from lxml import html
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union
from uuid import UUID
import re
from datetime import datetime
from datetime import time as dt_time

from utilities.update_cookies import scheduler
from utilities.tg import send_telegram_message, send_telegram_message_bot_2
from utilities.const import UrlsEnums

logger.add("log/log_control.log", rotation="2 MB")


scheduler.start()


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
        if price < 10_000:
            dict_items[f"{i}"] = {
                "abs_id": id_item,
                "price": price,
            }

    logger.info(str(dict_items))

    return dict_items


def find_item_number(data: dict, id_item: int) -> int | None:
    """
    Возвращает номер элемента, соответствующего заданному id_item, или None, если элемент не найден.
    """

    for number, item in data.items():
        if item.get("abs_id") == id_item:
            return int(number)
    return None


def control_competitors(abs_id: int, dict_items: dict, competitor_id: int) -> Union[None, float, int]:
    ads_position = find_item_number(dict_items, abs_id)
    ads_competitor_position = find_item_number(dict_items, competitor_id)

    if not ads_position or not ads_competitor_position:
        return None

    if ads_position < ads_competitor_position:
        return None

    return dict_items.get(f"{ads_competitor_position}").get("price") + 1


def check_position(position: int, dict_items: dict, abs_id: int, chat_id: int, item: dict) -> Union[None, float, int]:
    """Получение цены за позицию"""

    if item.get("competitor_id"):
        competitor = control_competitors(abs_id=abs_id, dict_items=dict_items, competitor_id=item.get("competitor_id"))
        if competitor:
            return competitor

    # competitor = control_competitors(abs_id=abs_id, dict_items=dict_items)
    # if competitor:
    #     subcategories_link = "https://www.farpost.ru/" + item.get("attr")
    #     message = f"""Приклеенное объявление <a href='{item.get("link")}'>{item.get("name_farpost")}</a> в режиме обгона конкурента в категории<a href='{subcategories_link}'>{item.get("subcategories")}</a>"""
    #     send_telegram_message(chat_id=chat_id, message=message)
    #     return competitor

    position_item = dict_items.get(f"{position}")
    position_item_last = dict_items.get(f"{position+1}")

    if position_item is None and position_item_last is None:
        return 10

    if position_item and int(position_item.get("abs_id")) == abs_id:
        if position_item_last:
            return position_item_last.get("price") + 1
        else:
            logger.info(position_item_last)
            return None

    if position_item and int(position_item.get("abs_id")) != abs_id:
        position_now = find_item_number(dict_items, abs_id)
        if position_now and position_now > position:
            if item.get("is_up"):
                subcategories_link = "https://www.farpost.ru/" + item.get("attr")
                message = f"""Приклеенное объявление <a href='{item.get("link")}'>{item.get("name_farpost")}</a> снизилось с {position}-й до {position_now}-й позиции  в разделе <a href='{subcategories_link}'>{item.get("subcategories")}</a>"""
                logger.debug(f"{abs_id} | {position_now} | {position}")
                send_telegram_message(chat_id=chat_id, message=message)
                requests.get(UrlsEnums.stop_tracking.value + item.get("abs_active_id"))

        return position_item.get("price") + 1

    if position_item is None:
        return 10


def up_abs(
    abs_id: int, price: float, abs_active_id: UUID, position: int, cookies: dict, chat_id: int, item: dict
) -> None:
    """Поднятия на позицию"""
    i = 0
    result = requests.get(f"https://www.farpost.ru/bulletin/{abs_id}/newstick?ajax=1", cookies=cookies)
    price_req_text = html.fromstring(result.text)
    price_req = float(price_req_text.xpath('//*[(@id = "stickPrice")]/@value')[0])
    if price_req != price:
        while True:
            i += 1
            logger.info(f"Обьявление пытаеться подняться | {abs_id}")
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
                else:
                    requests.get(
                        f"https://www.farpost.ru/bulletin/service-configure?ids={abs_id}&applier=unStickBulletin&auto_apply=1",
                        cookies=cookies,
                    )
            except:
                pass

            if i > 20:
                logger.info(f"Обьявление не смогло подняться | {abs_id}")
                break

        subcategories_link = "https://www.farpost.ru/" + item.get("attr")
        message = f"""Приклеенное объявление <a href='{item.get("link")}'>{item.get("name_farpost")}</a> поднялось до {position}-й позиции в разделе <a href='{subcategories_link}'>{item.get("subcategories")}</a> цена поднятия : {price}"""
        send_telegram_message(chat_id=chat_id, message=message)

        logger.info(f"Объявление : {abs_id} | Цена поднятия : {price} | Позиция сейчас : {top}")


def get_html_user_cookies(items):
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

    user = requests.get(UrlsEnums.get_user_with_abs_active.value + items["abs_active_id"]).json()
    cookies = requests.get(UrlsEnums.get_cookies_with_user.value + user.get("login")).json()

    html_code = session.get(f"https://www.farpost.ru/" + items["attr"], cookies=cookies).text
    return html_code, user, cookies


def load_item(items):
    html_code, user, cookies = get_html_user_cookies(items=items)
    chat_id = requests.get(UrlsEnums.get_telegram_chat_id.value + user.get("login")).json()["telegram_id"]

    tree: html.HtmlElement = html.fromstring(html_code)
    title: str = tree.xpath("/html/head/title/text()")

    logger.error("Название раздела для сбора : " + ",".join(title))

    price_up = check_position(
        items.get("position"),
        parse_html_text(html_code),
        items.get("abs_id"),
        chat_id,
        items,
    )

    if price_up and price_up < items.get("price_limitation"):
        if price_up < requests.get(UrlsEnums.get_wallet_user.value + user.get("login")).json().get("wallet"):
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
            requests.get(
                f"https://www.farpost.ru/bulletin/service-configure?ids={items.get('abs_id')}&applier=unStickBulletin&auto_apply=1",
                cookies=cookies,
            )
    elif price_up is None:
        pass
    else:
        if items.get("is_up"):
            send_telegram_message_bot_2(
                chat_id,
                f"""Приклеенное объявление <a href='{items.get("link")}'>{items.get("name_farpost")}</a> не может подняться увеличте лимит до {price_up*2} !!!!!""",
            )
            requests.get(UrlsEnums.stop_tracking.value + items.get("abs_active_id"))


def run_item(items):
    datetime_now = datetime.now()
    time_now = dt_time(hour=datetime_now.hour, minute=datetime_now.minute)
    logger.error(items["all_time"])
    if not items["all_time"]:
        load_item(items)
    elif (
        dt_time.fromisoformat(items.get("start_time")) < time_now
        and dt_time.fromisoformat(items.get("end_time")) > time_now
    ):
        load_item(items)
    else:
        user = requests.get(UrlsEnums.get_user_with_abs_active.value + items["abs_active_id"]).json()
        cookies = requests.get(UrlsEnums.get_cookies_with_user.value + user.get("login")).json()
        abs_id = items.get("abs_id")
        requests.get(
            f"https://www.farpost.ru/bulletin/service-configure?ids={abs_id}&applier=unStickBulletin&auto_apply=1",
            cookies=cookies,
        )


def checking_position():
    list_items_parse: list[dict] = [
        {
            "abs_id": i["abs_id"],
            "abs_active_id": i["abs_active_id"],
            "position": i["position"],
            "price_limitation": i["price_limitation"],
            "attr": i["category_attribute"],
            "name_farpost": i["name_farpost"],
            "link": i["link"],
            "start_time": i["start_time"],
            "end_time": i["end_time"],
            "subcategories": i["subcategories"],
            "all_time": i["all_time"],
            "is_up": i["is_up"],
            "competitor_id": i["competitor_id"],
        }
        for i in requests.get(url=UrlsEnums.get_active_data_close_none.value).json()
    ]

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Создание списка будущих выполнений
        futures = [executor.submit(run_item, item) for item in list_items_parse]

        # Ожидание завершения всех задач и обработка результатов по мере их выполнения
        for future in as_completed(futures):
            try:
                result = future.result()
                # Обработка результата
            except Exception as e:
                # Обработка исключения
                print(f"Произошла ошибка: {e}")


if is_api_available(UrlsEnums.get_active_data_close_none.value):
    while True:
        checking_position()
else:
    logger.error("API недоступно.")
