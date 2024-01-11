from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from loguru import logger

import requests
from lxml import html
import time
import os

API_HOST = os.environ.get("API_HOST")
API_PORT = os.environ.get("API_PORT")

PREF_FARPOST = "/api/v1/farpost"

get_active_data_close_none = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_active_data_close_none"

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


def parse_html_text(html_code: str) -> list[tuple]:
    html_parce = html.fromstring(html_code)

    list_link_id = [
        i.split("-")[-1].split(".")[0]
        for i in html_parce.xpath(
            """//*[contains(concat( " ", @class, " " ), concat( " ", "bull-item__self-link", " " ))]/@href"""
        )
    ]
    list_item_info = [
        i.split(":")[1].split("-")[0][2:]
        for i in html_parce.xpath(
            """//*[contains(concat( " ", @class, " " ), concat( " ", "bull-item__image-cell", " " ))]/@data-order-key"""
        )
    ]
    data = []
    for i, id_item, price in zip(range(1, len(list_link_id) + 1), list_link_id, list_item_info):
        data.append((i, int(id_item), float(price)))

    return data


def up_rating() -> None:
    list_items_parse = [
        {
            "id": i["abs_id"],
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

        list_data = parse_html_text(html_code)

        logger.info(list_data)

    driver.quit()


if is_api_available(get_active_data_close_none):
    while True:
        up_rating()
else:
    logger.error("API недоступно.")
