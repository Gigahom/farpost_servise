from requests import get
from requests.exceptions import RequestException
from time import sleep


def is_api_available(url: str, max_attempts: int = 5, delay: int = 5) -> bool:
    """Проверяет доступность API.

    Args:
    - url (str): URL API для проверки.
    - max_attempts (int, optional): Максимальное количество попыток. По умолчанию 5.
    - delay (int, optional): Задержка между попытками в секундах. По умолчанию 5.

    Returns:
    - bool: True если API доступен, иначе False.
    """

    for _ in range(max_attempts):
        try:
            response = get(url)
            if response.status_code == 200:
                return True
        except RequestException:
            pass
        sleep(delay)
    return False
