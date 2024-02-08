from fastapi import APIRouter

from datetime import datetime
import requests

from src.settings.const import BASE_URL_LOG, URL_API
from src.apps.control.schemas import CountSchema, PositeonTimeSchema, PositeonTimeALLSchema, PositeonTimeALL

router: APIRouter = APIRouter(
    prefix="/farpost_statistics",
)

tags_metadata_statistics = [
    {
        "name": "Статистика",
        "description": "Данные для графиков",
        "externalDocs": {
            "description": "",
        },
    },
]


@router.get("/get_position_time", tags=["Статистика"], summary="Время в позиции")
async def get_position_time(login: str, abs_id: int) -> PositeonTimeALL:
    user_id = requests.get(URL_API + f"get_user_id?login={login}").json()
    print(user_id)
    with open(BASE_URL_LOG + f"{user_id}/{abs_id}/info/position_now.log") as file:
        lines = [line.rstrip() for line in file]

    time_deltas_multiple_keys = {}

    for line in lines:
        datetime_str, key = line.split(" | ")
        key = int(key)
        current_date = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f%z")

        if key not in time_deltas_multiple_keys:
            time_deltas_multiple_keys[key] = {"total_time": 0, "prev_date": current_date}
        else:
            delta = current_date - time_deltas_multiple_keys[key]["prev_date"]
            time_deltas_multiple_keys[key]["total_time"] += delta.total_seconds()
            time_deltas_multiple_keys[key]["prev_date"] = current_date

    final_results = [PositeonTimeALLSchema(*{k: v["total_time"] / 3600}) for k, v in time_deltas_multiple_keys.items()]

    return PositeonTimeALL(positeon_time=final_results)


@router.get("/get_position_time_all", tags=["Статистика"], summary="Позиция со временим")
async def get_position_time_all(login: str, abs_id: int) -> PositeonTimeSchema:
    user_id = requests.get(URL_API + f"get_user_id?login={login}").json()
    with open(BASE_URL_LOG + f"{user_id}/{abs_id}/info/position_now.log") as file:
        lines = [line.rstrip() for line in file]

    list_positeon = []
    list_time = []

    for line in lines:
        datetime_str, key = line.split(" | ")
        key = int(key)
        current_date = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        list_positeon.append(key)
        list_time.append(current_date)

    return PositeonTimeSchema(positeon=list_positeon, time=list_time)


@router.get("/count_up", tags=["Статистика"], summary="Количество поднятий")
async def count_up(login: str, abs_id: int) -> CountSchema:
    user_id = requests.get(URL_API + f"get_user_id?login={login}").json()
    with open(BASE_URL_LOG + f"{user_id}/{abs_id}/info/abs_up.log") as file:
        lines = [line.rstrip() for line in file]

    return CountSchema(count=len(lines))
