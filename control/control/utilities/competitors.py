def find_item_number(data: dict, id_item: int) -> int | None:
    """
    Возвращает номер элемента, соответствующего заданному id_item, или None, если элемент не найден.
    """

    for number, item in data.items():
        if item.get("abs_id") == id_item:
            return int(number)
    return None


def control_competitors(abs_id: int, dict_items: dict, competitor_id: int) -> None | float | int:
    ads_position = find_item_number(dict_items, abs_id)
    ads_competitor_position = find_item_number(dict_items, competitor_id)

    if not ads_position or not ads_competitor_position:
        return None

    if ads_competitor_position:
        return dict_items.get(f"{ads_competitor_position}").get("price") + 1
