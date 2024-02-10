from loguru import logger

import requests
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union
from uuid import UUID
from datetime import datetime
from datetime import time as dt_time

from utilities.update_cookies import scheduler
from utilities.tg import send_telegram_message, send_telegram_message_bot_2
from utilities.const import UrlsEnums
from utilities.logs import custom_sink
from utilities.utilities import is_api_available
from utilities.handler_html import parse_html_text
from utilities.price import check_position
from utilities.abstractions import AbsActive

logger.add(custom_sink, format="{time} | {message}")


scheduler.start()


def up_abs(
    abs_id: int, price: float, abs_active_id: UUID, position: int, cookies: dict, chat_id: int, item: AbsActive
) -> None:
    """Поднятия на позицию"""
    i = 0
    result = requests.get(f"https://www.farpost.ru/bulletin/{abs_id}/newstick?ajax=1", cookies=cookies)
    price_req_text = html.fromstring(result.text)
    price_req = float(price_req_text.xpath('//*[(@id = "stickPrice")]/@value')[0])
    if price_req != price:
        now = datetime.now()
        while True:
            i += 1
            try:
                requests.get(
                    f"https://www.farpost.ru/bulletin/service-configure?auto_apply=1&stickPrice={price}&return_to=&ids={abs_id}&applier=stickBulletin&stick_position%5B{abs_id}%5D=1&already_applied=1",
                    cookies=cookies,
                )
                result = requests.get(f"https://www.farpost.ru/bulletin/{abs_id}/newstick?ajax=1", cookies=cookies)
                price_req_text = html.fromstring(result.text)
                price_req = float(price_req_text.xpath('//*[(@id = "stickPrice")]/@value')[0])
                if price_req == price:
                    break
                else:
                    requests.get(
                        f"https://www.farpost.ru/bulletin/service-configure?ids={abs_id}&applier=unStickBulletin&auto_apply=1",
                        cookies=cookies,
                    )
            except:
                pass

            if i > 20:
                logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(
                    file_name="error_up"
                ).error("Объявление не смогло подняться за 20 запросов")
                break

        subcategories_link = "https://www.farpost.ru/" + item.get("attr")
        message = f"""Приклеенное объявление <a href='{item.get("link")}'>{item.get("name_farpost")}</a> поднялось до {position}-й позиции в разделе <a href='{subcategories_link}'>{item.get("subcategories")}</a> цена поднятия : {price}"""
        send_telegram_message(chat_id=chat_id, message=message)
        logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(file_name="abs_up").info(
            datetime.now() - now
        )


def get_html_user_cookies(item: AbsActive):
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

    user = requests.get(UrlsEnums.get_user_with_abs_active.value + item["abs_active_id"]).json()
    cookies = requests.get(UrlsEnums.get_cookies_with_user.value + user.get("login")).json()

    html_code = session.get(f"https://www.farpost.ru/" + item["attr"], cookies=cookies).text
    return html_code, user, cookies


def load_item(item: AbsActive) -> None:
    html_code, user, cookies = get_html_user_cookies(item=item)
    chat_id = requests.get(UrlsEnums.get_telegram_chat_id.value + user.get("login")).json()["telegram_id"]

    tree: html.HtmlElement = html.fromstring(html_code)
    title: str = tree.xpath("/html/head/title/text()")

    logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(file_name="title").debug(title)

    price_up = check_position(
        item.get("position"),
        parse_html_text(html_code, item),
        item.get("abs_id"),
        chat_id,
        item,
    )

    if price_up and price_up < item.get("price_limitation"):
        if price_up < requests.get(UrlsEnums.get_wallet_user.value + user.get("login")).json().get("wallet"):
            up_abs(
                item.get("abs_id"),
                price_up,
                item.get("abs_active_id"),
                item.get("position"),
                cookies,
                chat_id,
                item,
            )
        else:
            # logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(file_name="cashback").debug("Не хватает средст")
            # requests.get(
            #     f"https://www.farpost.ru/bulletin/service-configure?ids={item.get('abs_id')}&applier=unStickBulletin&auto_apply=1",
            #     cookies=cookies,
            # )
            up_abs(
                item.get("abs_id"),
                price_up,
                item.get("abs_active_id"),
                item.get("position"),
                cookies,
                chat_id,
                item,
            )
    elif price_up is None:
        pass
    else:
        if item.get("is_up"):
            logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(file_name="limit").debug("Нельзя выйти за лимит")
            send_telegram_message_bot_2(
                chat_id,
                f"""Приклеенное объявление <a href='{item.get("link")}'>{item.get("name_farpost")}</a> не может подняться увеличте лимит до {price_up*2} !!!!!""",
            )
            requests.get(UrlsEnums.stop_tracking.value + item.get("abs_active_id"))


def run_item(item: AbsActive) -> None:
    datetime_now = datetime.now()
    time_now = dt_time(hour=datetime_now.hour, minute=datetime_now.minute)
    if not item["all_time"]:
        load_item(item)
    elif (
        dt_time.fromisoformat(item.get("start_time")) < time_now
        and dt_time.fromisoformat(item.get("end_time")) > time_now
    ):
        load_item(item)
    else:
        user = requests.get(UrlsEnums.get_user_with_abs_active.value + item["abs_active_id"]).json()
        cookies = requests.get(UrlsEnums.get_cookies_with_user.value + user.get("login")).json()
        abs_id = item.get("abs_id")
        requests.get(
            f"https://www.farpost.ru/bulletin/service-configure?ids={abs_id}&applier=unStickBulletin&auto_apply=1",
            cookies=cookies,
        )

    logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(file_name="time_reaction").debug(
        datetime.now() - datetime_now
    )


def checking_position() -> None:
    list_items_parse: list[AbsActive] = [
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
            "user_id": i["user_id"],
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
    pass
