from pydantic import BaseModel, Field
from typing import Optional, Union
from uuid import UUID
from datetime import datetime, time

class TextSchema(BaseModel):
    text: str

class UserSchema(BaseModel):
    """
    Схема для выгрузки пользователя
    """

    user_id: UUID
    login: str
    password: str
    tg_chat_id: Optional[int] = None


class AbsSchema(BaseModel):
    """
    Схема объявления
    """

    abs_id: int
    user_id: UUID
    link_main_img: str
    link: str
    name_farpost: str
    city_english: str
    categore: str
    subcategories: str
    category_attribute: str


class AbsActiveSchema(BaseModel):
    """
    Схема активного объявления
    """

    abs_active_id: UUID
    abs_id: int
    position: int
    price_limitation: float
    date_creation: datetime
    date_closing: Optional[datetime]
    start_time: time
    end_time: time


class AbsActiveMergeSchema(BaseModel):
    """
    Схема активного объявления с даными из Abs
    """

    abs_active_id: UUID
    user_id: UUID
    link_main_img: str
    link: str
    name_farpost: str
    city_english: str
    categore: str
    subcategories: str
    category_attribute: str
    abs_id: int
    position: int
    price_limitation: float
    date_creation: datetime
    date_closing: Optional[datetime]
    start_time: time
    end_time: time


class HeadersSchema(BaseModel):
    """
    Схема заголовков farpost в ответе после автозирации
    """

    Server: Optional[str] = None
    Date: Optional[str] = None
    Content_Type: Optional[str] = Field(default=None, alias="Content-Type")
    Transfer_Encoding: Optional[str] = Field(default=None, alias="Transfer-Encoding")
    Connection: Optional[str] = None
    Keep_Alive: Optional[str] = Field(default=None, alias="Keep-Alive")
    Vary: Optional[str] = None
    Set_Cookie: Optional[str] = Field(default=None, alias="Set-Cookie")
    Content_Security_Policy: Optional[str] = Field(default=None, alias="Content-Security-Policy")
    Cache_control: Optional[str] = Field(default=None, alias="Cache-control")
    Accept_CH: Optional[str] = Field(default=None, alias="Accept-CH")
    Content_Encoding: Optional[str] = Field(default=None, alias="Content-Encoding")


class WalletSchema(BaseModel):
    """Схема для суммы на кошельку"""

    wallet: float


class TelegramSchema(BaseModel):
    """Схема для id телеграм чат пользователя"""

    telegram_id: Union[int, None]


class CookiesSchema(BaseModel):
    """
    Схема куков farpost в ответе после автозирации
    """

    ring: str
    boobs: str
    pony: str
    login: str
    protected_deals_top_line: Optional[str] = Field(default="0", alias="protected_deals_top_line")


class ResponseLoginSchema(BaseModel):
    """
    Схема farpost в ответе после автозирации
    """

    headers: HeadersSchema
    cookies: CookiesSchema
