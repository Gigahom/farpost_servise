from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserSchema(BaseModel):
    """
    Схема для выгрузки пользователя
    """

    user_id: UUID
    login: str
    password: str


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


class HeadersSchema(BaseModel):
    """
    Схема заголовков farpost в ответе после автозирации
    """

    Server: str
    Date: str
    Content_Type: str = Field(..., alias="Content-Type")
    Transfer_Encoding: str = Field(..., alias="Transfer-Encoding")
    Connection: str
    Keep_Alive: str = Field(..., alias="Keep-Alive")
    Vary: str
    Set_Cookie: str = Field(..., alias="Set-Cookie")
    Content_Security_Policy: str = Field(..., alias="Content-Security-Policy")
    Cache_control: str = Field(..., alias="Cache-control")
    Accept_CH: str = Field(..., alias="Accept-CH")
    Content_Encoding: str = Field(..., alias="Content-Encoding")


class CookiesSchema(BaseModel):
    """
    Схема куков farpost в ответе после автозирации
    """

    ring: str
    boobs: str
    pony: str
    login: str
    protected_deals_top_line: str = Field(..., alias="protected_deals_top_line")


class ResponseLoginSchema(BaseModel):
    """
    Схема farpost в ответе после автозирации
    """

    headers: HeadersSchema
    cookies: CookiesSchema
