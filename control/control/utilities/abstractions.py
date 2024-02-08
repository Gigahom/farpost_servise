from typing import TypedDict
from uuid import uuid4
from datetime import time as dt_time


class AbsActive(TypedDict):
    abs_id: int
    abs_active_id: uuid4
    position: int
    price_limitation: float
    attr: str
    name_farpost: str
    link: str
    start_time: dt_time
    end_time: dt_time
    subcategories: str
    all_time: bool
    is_up: bool
    competitor_id: bool
    user_id: uuid4
