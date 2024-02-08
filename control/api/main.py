import fastapi

from src.settings.const import BASE_URL
from src.apps.control.router import router as router_farpost_statistics
from src.apps.control.router import tags_metadata_statistics

description_farpost = """
Может тут будет описание а может и нет
"""
summary_farpost = """
Это API передназначено для выгрузки данных о объявление
"""

app = fastapi.FastAPI()
appv1 = fastapi.FastAPI(
    tags_metadata=tags_metadata_statistics,
    title="FARPOST API Statistics",
    summary=summary_farpost,
    description=description_farpost,
    version="0.0.1",
    contact={
        "name": "Neko1313",
        "url": "https://github.com/Neko1313",
        "email": "nikita.ribalchencko@yandex.ru",
    },
)

appv1.include_router(router_farpost_statistics)


app.mount(BASE_URL, appv1)
