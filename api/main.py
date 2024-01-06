import fastapi

from src.settings.const import BASE_URL
from src.apps.FARPOST.router import router as router_farpost

app = fastapi.FastAPI()
appv1 = fastapi.FastAPI()

appv1.include_router(router_farpost)


app.mount(BASE_URL, appv1)
