from enum import Enum


BASE_URL = "/api/v1"


class TestUserEnum(Enum):
    """Тестовый пользоаатель"""

    login = "79246763737"
    password = "Neko"
    abs_id = "115194290"
    abs_active_id = "1820e4ea-a04a-446d-a1b6-4ed3bdc740a7"
    headers = {
        "Server": "nginx",
        "Date": "Tue, 09 Jan 2024 11:42:13 GMT",
        "Content-Type": "text/html; charset=windows-1251",
        "Transfer-Encoding": "chunked",
        "Connection": "keep-alive",
        "Keep-Alive": "timeout=120",
        "Vary": "Accept-Encoding, Accept-Encoding, Accept-Encoding",
        "Set-Cookie": "ring=b01dbdbfff21e51d50fa1402d25af90f; expires=Wed, 12-Feb-2025 11:42:13 GMT; Max-Age=34560000; path=/; domain=.farpost.ru; secure; SameSite=None, boobs=797ae541601ec8f50da01020d0611ed293ab089d65d81aa490f8c77f46232611u16fd509; expires=Wed, 08-May-2024 11:42:13 GMT; Max-Age=10368000; path=/; domain=.farpost.ru; secure; HttpOnly; SameSite=Lax, pony=4d6a51784d4459794e446b3du944e10748ca972ae1179f8d77bfed2f4; expires=Wed, 08-May-2024 11:42:13 GMT; Max-Age=10368000; path=/; domain=.farpost.ru; secure; HttpOnly; SameSite=Lax, protected_deals_top_line=0; expires=Tue, 09-Jan-2024 11:52:13 GMT; Max-Age=600; path=/; domain=.farpost.ru",
        "Content-Security-Policy": "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://*.google-analytics.com https://www.googletagmanager.com https://www.googleadservices.com https://*.google.com https://translate.googleapis.com https://translate-pa.googleapis.com https://googleads.g.doubleclick.net https://www.googleoptimize.com https://api-maps.yandex.ru https://*.maps.yandex.net https://mc.yandex.ru https://yastatic.net https://top-fwz1.mail.ru https://connect.facebook.net https://www.youtube.com https://bs-dante.ru https://*.farpost.ru https://www.dvhab.ru https://*.drom.ru https://*.rdrom.ru https://*.vl.ru https://*.jivo.ru https://*.jivosite.com; connect-src 'self' https://bs-dante.ru https://*.bs-dante.ru https://*.google-analytics.com https://*.google.ru https://*.google.com https://translate.googleapis.com https://stats.g.doubleclick.net https://api-maps.yandex.ru https://mc.yandex.ru https://mc.yandex.az https://mc.yandex.by https://mc.yandex.co.il https://mc.yandex.com https://mc.yandex.com.am https://mc.yandex.com.ge https://mc.yandex.com.tr https://mc.yandex.ee https://mc.yandex.fr https://mc.yandex.kg https://mc.yandex.kz https://mc.yandex.lt https://mc.yandex.lv https://mc.yandex.md https://mc.yandex.tj https://mc.yandex.tm https://mc.yandex.ua https://mc.yandex.uz https://mc.webvisor.com https://mc.webvisor.org https://yastatic.net https://top-fwz1.mail.ru https://www.facebook.com https://counter.yadro.ru wss://*.farpost.ru wss://*.drom.ru wss://*:444 https://api2.nrg-tk.ru https://*.vl.ru https://*.drom.ru https://*.farpost.ru https://www.dvhab.ru https://*.jivo.ru https://*.jivosite.com wss://*.jivo.ru",
        "Cache-control": "no-store, no-cache",
        "Accept-CH": "Sec-CH-UA-Full-Version, Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version, Sec-CH-UA-Model, Sec-CH-UA-Arch, Sec-CH-UA-Bitness",
        "Content-Encoding": "gzip",
    }
    cookies = {
        "ring": "b01dbdbfff21e51d50fa1402d25af90f",
        "boobs": "797ae541601ec8f50da01020d0611ed293ab089d65d81aa490f8c77f46232611u16fd509",
        "pony": "4d6a51784d4459794e446b3du944e10748ca972ae1179f8d77bfed2f4",
        "login": "79246763737",
        "protected_deals_top_line": "0",
    }


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
