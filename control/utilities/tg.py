from requests import post

from utilities.const import TG_API_KEY, TG_API_KEY_2

def send_telegram_message(chat_id: int, message: str):
    """
    Отправляет сообщение пользователю в Telegram.
    """
    if chat_id:
        url = f"https://api.telegram.org/bot{TG_API_KEY}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        response = post(url, json=payload)
        return response.json()


def send_telegram_message_bot_2(chat_id: int, message: str):
    """
    Отправляет сообщение пользователю в Telegram.
    """
    if chat_id:
        url = f"https://api.telegram.org/bot{TG_API_KEY_2}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        response = post(url, json=payload)
        return response.json()