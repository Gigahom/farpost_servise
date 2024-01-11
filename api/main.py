import fastapi

from src.settings.const import BASE_URL
from src.apps.FARPOST.router import router as router_farpost
from src.apps.FARPOST.router import tags_metadata_farpost

description_farpost = """
Термины:\n
* Запись - объявление с фарпоста
* Активная запись - объявление с фарпоста, которое ли бы работает ли бы работало 
* Работающая запись - объявление с фарпоста, которое работает внутри системы для одного пользователя доступная одновременно только одна запись
"""
summary_farpost = """
Это API передназначено для автоматизации поднятия объявления
"""

app = fastapi.FastAPI()
appv1 = fastapi.FastAPI(
    tags_metadata=tags_metadata_farpost,
    title="FARPOST API",
    summary=summary_farpost,
    description=description_farpost,
    version="0.0.1",
    contact={
        "name" : "Neko1313",
        "url" : "https://github.com/Neko1313",
        "email" : "nikita.ribalchencko@yandex.ru",
    },
)

appv1.include_router(router_farpost)


app.mount(BASE_URL, appv1)
