import fastapi

from src.settings.const import BASE_URL
from src.apps.FARPOST.router import router as router_farpost
from src.apps.FARPOST.router import tags_metadata_farpost

app = fastapi.FastAPI()
appv1 = fastapi.FastAPI(
    tags_metadata=tags_metadata_farpost,
    title="FARPOST API",
    description="""
    Это API передназначено для автоматизации поднятия объявления\n
    Термины:\n
    + Запись - объявление с фарпоста
    + Активная запись - объявление с фарпоста, которое ли бы работает ли бы работало 
    + Работающая запись - объявление с фарпоста, которое работает внутри системы для одного пользователя доступная одновременно только одна запись
    """,
    version="0.0.1",
)

appv1.include_router(router_farpost)


app.mount(BASE_URL, appv1)
