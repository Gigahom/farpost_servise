from lxml import html
import importlib

from loguru import logger

from utilities.abstractions import AbsActive
from utilities.logs import custom_sink

logger.add(custom_sink, format="{time} | {message}")


def parse_html_text(html_code: str, item: AbsActive) -> dict:
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

    for i, j in dict_items.items():
        logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(
            file_name="position_all_abs"
        ).debug(f"{j.get('abs_id')} | {i} | {j.get('price')}")

    logger.bind(abs_id=item.get("abs_id")).bind(login=item.get("user_id")).bind(file_name="position_all_abs").debug(
        "\n"
    )

    return dict_items
