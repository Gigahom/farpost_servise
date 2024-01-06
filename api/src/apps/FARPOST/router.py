from fastapi import APIRouter, Form, HTTPException

from lxml import html
import requests
from typing import List
from uuid import uuid4
import asyncio

from src.settings.const import ConstHeader, ConstUrl
from .schemas import ResponseLoginSchema, ItemSchema, UserSchema, BaseModel
from src.apps.models import User, Base
from src.settings.db import get_async_session


router = APIRouter(prefix="/farpost", tags=["farpost"])

async def async_add_data(class_model:Base, data:BaseModel):
    async with get_async_session() as session:
        await class_model.save_from_schema(schema=data, session=session)

@router.post("/get_items")
def get_items(response: ResponseLoginSchema) -> List[ItemSchema]:
    """
    Запрос на получение карточек в профиле
    """
    
    session: requests.session = requests.Session()

    session.headers.update(response.headers.dict())

    for key, value in response.cookies.dict().items():
        session.cookies.set(key, value)

    try:
        result: requests.models.Response = session.get("https://www.farpost.ru/personal/actual/bulletins")

        tree_item: html.HtmlElement = html.fromstring(result.text)

        items_list: list[ItemSchema] = [
            ItemSchema(
                **{
                    "id_site": id_.strip(),
                    "name": name.strip(),
                    "city": city.strip(),
                    "attr": attr.strip().replace(attr.split("/")[-1], "").replace("https://www.farpost.ru/", ""),
                    "categore": attr.strip()
                    .replace(attr.split("/")[-1], "")
                    .replace("https://www.farpost.ru/", "")
                    .split("/")[1],
                    "subcategories": attr.strip()
                    .replace(attr.split("/")[-1], "")
                    .replace("https://www.farpost.ru/", "")
                    .split("/")[2],
                    "link": attr,
                    "img": img,
                }
            )
            for id_, name, city, attr, img in zip(
                tree_item.xpath("//*[contains(@class, 'bull-item__image-cell')]/@data-bulletin-id"),
                tree_item.xpath("//*[contains(@class, 'bull-item__self-link')]/text()"),
                tree_item.xpath("//*[contains(@class, 'bull-delivery__city')]/text()"),
                tree_item.xpath("//*[contains(@class, 'bull-item__self-link')]/@href"),
                tree_item.xpath("//img/@src"),
            )
        ]
        return items_list
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def auth(login: str = Form(...), password: str = Form(...)) -> ResponseLoginSchema:
    """
    Запрос на авторизацию
    """
    session: requests.session = requests.session()
    common_headers: dict = {i.custom_name: i.value for i in ConstHeader}

    params1: dict = {"u": "/sign?return=%252F"}
    headers1: dict = common_headers.copy()
    headers1["Referer"]: str = "https://www.farpost.ru/verify?r=1&u=%2Fsign%3Freturn%3D%252F"
    session.get(ConstUrl.URL1.value, params=params1, headers=headers1)

    params2: dict = {"return": "%2Fverify%3Fr%3D1%26u%3D%252Fsign%253Freturn%253D%25252F"}
    headers2: dict = common_headers.copy()
    headers2["Referer"] = "https://www.farpost.ru/verify?r=1&u=%2Fsign%3Freturn%3D%252F"
    session.get(ConstUrl.URL2.value, params=params2, headers=headers2)

    response: requests.models.Response = session.get(ConstUrl.URL_SING.value)
    tree_csrf: html.HtmlElement = html.fromstring(response.text)
    csrf_token_value = tree_csrf.xpath("""//*[@id="csrfToken"]/@value""")[-1]
    data: dict = {
        "csrfToken": csrf_token_value,
        "radio": "sign",
        "sign": f"{login}",
        "password": f"{password}",
    }
    uuid_user = uuid4()
    user_data = UserSchema(user_id=uuid_user,login=login,password=password)
    asyncio.run(async_add_data(User,user_data))
    
    response = session.post(ConstUrl.URL_LOGIN.value, data=data)

    headers_dict: dict = dict(response.headers)
    cookies_dict: dict = requests.utils.dict_from_cookiejar(session.cookies)

    return ResponseLoginSchema(**{"headers": headers_dict, "cookies": cookies_dict})
