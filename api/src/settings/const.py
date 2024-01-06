from enum import Enum


BASE_URL = "/api/v1"


class ConstHeader(Enum):
    """
    Используемые констатные заголовки
    """

    Host = "www.farpost.ru"
    Cache_Control = "max-age=0"
    Upgrade_Insecure_Requests = "1"
    User_Agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
    Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    Sec_Fetch_Site = "same-origin"
    Sec_Fetch_Mode = "navigate"

    @property
    def custom_name(self):
        return self.name.replace("_", "-")


class ConstUrl(Enum):
    """
    Все ссылки используемые для запросов на farpost
    """

    URL1 = "https://www.farpost.ru/verify"
    URL2 = "https://www.farpost.ru/set/sentinel"
    URL_SING = "https://www.farpost.ru/sign?return=%2F"
    URL_LOGIN = "https://www.farpost.ru/sign?login_by_password=1"
    URL_ITEMS = "https://www.farpost.ru/personal/actual/bulletins"
