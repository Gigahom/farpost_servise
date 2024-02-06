from os import environ
from enum import Enum


API_HOST = environ.get("API_HOST")
API_PORT = environ.get("API_PORT")
TG_API_KEY = environ.get("TG_API_KEY")
TG_API_KEY_2 = environ.get("TG_API_KEY_2")

PREF_FARPOST = "/api/v1/farpost"

class UrlsEnums(Enum):
    get_active_data_close_none = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_active_data_close_none"
    update_cookies = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/update_cookies"
    get_user_with_abs_active = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_user_with_abs_active?abs_active_id="
    get_cookies_with_user = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_cookies_with_user?login="
    get_telegram_chat_id = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_telegram_chat_id?login="
    stop_tracking = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/stop_tracking?abs_active_id="
    get_wallet_user = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_wallet_user?login="