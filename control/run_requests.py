from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from loguru import logger

import requests
from lxml import html
import time
import os
from typing import Union
from uuid import UUID
import re

API_HOST = os.environ.get("API_HOST")
API_PORT = os.environ.get("API_PORT")

PREF_FARPOST = "/api/v1/farpost"

get_active_data_close_none = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_active_data_close_none"
get_user_with_abs_active = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_user_with_abs_active?abs_active_id="

logger.add("log/log_control.log", rotation="2 MB")

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")
options.add_argument("--start-maximized")


def is_api_available(url: str, max_attempts: int = 5, delay: int = 5) -> bool:
    """Проверяет доступность API.

    Args:
        url (str): URL API для проверки.
        max_attempts (int, optional): Максимальное количество попыток. По умолчанию 5.
        delay (int, optional): Задержка между попытками в секундах. По умолчанию 5.

    Returns:
        bool: True если API доступен, иначе False.
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


def check_position(position: int, dict_items: dict, abs_id: int) -> Union[None, float]:
    position_item = dict_items.get(f"{position}")
    if position_item:
        if position_item.get("abs_id") != abs_id:
            return position_item.get("price") + 1
        else:
            return None
    else:
        return None


def up_abs(abs_id: int, price: float, abs_active_id: UUID, position: int) -> None:
    user = requests.get(get_user_with_abs_active+abs_active_id).json()
    
    driver = webdriver.Chrome(options=options)
    driver.set_network_conditions(
        offline=False,
        latency=5,
        download_throughput=500 * 1024,
        upload_throughput=500 * 1024,
        connection_type="wifi",
    )
    driver.get("https://www.farpost.ru")
    time.sleep(0.01)

    driver.get("https://www.farpost.ru/sign")
    element = driver.find_element(By.NAME, "sign")
    element.send_keys(user.get("login"))
    element = driver.find_element(By.NAME, "password")
    element.send_keys(user.get("password"))
    driver.find_element(By.ID, "signbutton").click()

    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}

    driver.quit()

    while True:
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

    logger.info(f"Объявление : {abs_id} | Цена поднятия : {price} | Позиция сейчас : {top}")


def checking_position() -> None:
    list_items_parse: list[dict] = [
        {
            "abs_id": i["abs_id"],
            "abs_active_id": i["abs_active_id"],
            "position": i["position"],
            "price_limitation": i["price_limitation"],
            "attr": i["category_attribute"],
        }
        for i in requests.get(url=get_active_data_close_none).json()
    ]

    driver = webdriver.Chrome(options=options)
    driver.set_network_conditions(
        offline=False,
        latency=5,
        download_throughput=500 * 1024,
        upload_throughput=500 * 1024,
        connection_type="wifi",
    )
    driver.get("https://www.farpost.ru")
    time.sleep(0.01)

    for items in list_items_parse:
        driver.get(f"https://www.farpost.ru/" + items["attr"])
        html_code = driver.page_source

        dict_data = parse_html_text(html_code)

        price_up = check_position(items.get("position"), dict_data, items.get("abs_id"))
        if price_up:
            if price_up < items.get("price_limitation"):
                up_abs(items.get("abs_id"), price_up, items.get("abs_active_id"), items.get("position"))
        else:
            pass

    driver.quit()


if is_api_available(get_active_data_close_none):
    while True:
        checking_position()
else:
    logger.error("API недоступно.")
