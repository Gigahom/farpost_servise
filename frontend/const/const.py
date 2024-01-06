import os
from enum import Enum

API_HOST = os.environ.get("API_HOST")
API_PORT = os.environ.get("API_PORT")
# API_PORT = 5000
# API_HOST = "127.0.0.1"

PREF_FARPOST = "/api/v1/farpost"


class RequstsApi(Enum):
    """
    Класс хронящий все ссылки на api
    """

    Login = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/login"
    Items = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_items"
