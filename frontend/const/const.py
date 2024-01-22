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

    Login = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/login"  # POST
    Items = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_items"  # GET
    Updata = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/update_items_user"  # POST
    AbsActiveWithUser = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_abs_active_by_user_none"  # GET
    AbsActiveWithUserNotNone = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_abs_active_by_user"  # GET
    CreactAbsActive = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/creact_abs_active"  # GET
    StopAbsActive = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/stop_abs_active"  # GET
    AbsInfo = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_abs_info?abs_id="  # GET
    Wallet = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_wallet_user?login="  # GET
    UpdataTg = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/update_user_tg_chat_id?"  # GET
    GetTg = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/get_telegram_chat_id?login="  # GET
    LoginBurp = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/login_burp"