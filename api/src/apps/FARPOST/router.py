from fastapi import APIRouter, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from lxml import html
import requests
from typing import List, Union
from uuid import uuid4, UUID
import asyncio
from datetime import datetime

from src.settings.const import ConstHeader, ConstUrl
from .schemas import (
    ResponseLoginSchema,
    HeadersSchema,
    CookiesSchema,
    UserSchema,
    AbsSchema,
    AbsActiveSchema,
    AbsActiveMergeSchema,
    UserSchema,
    CookiesSchema,
)

from src.apps.models import User, AbsActive, Abs, Cookies
from src.settings.db import get_async_session
from src.apps.FARPOST.utilities import (
    get_ads_by_user_login,
    async_add_data,
    get_user_id_by_login,
)


router: APIRouter = APIRouter(
    prefix="/farpost",
)

tags_metadata_farpost: list[dict[str, Union[str, dict[str, str]]]] = [
    {
        "name": "Система контроля",
        "description": "Для работы системы контроля",
        "externalDocs": {
            "description": "Запросы, которые используют система поднятия и контроля",
        },
    },
    {
        "name": "Приложение",
        "description": "Работа в нутри приложения",
        "externalDocs": {
            "description": "Все запросы, которые используются web приложением",
        },
    },
]


async def update_cookies(user: UserSchema) -> CookiesSchema:
    session = requests.Session()
    common_headers: dict = {i.custom_name: i.value for i in ConstHeader}

    params1: dict = {"u": "/sign?return=%252F"}
    headers1: dict = common_headers.copy()
    headers1["Referer"] = "https://www.farpost.ru/verify?r=1&u=%2Fsign%3Freturn%3D%252F"
    session.get(ConstUrl.URL1.value, params=params1, headers=headers1)

    params2: dict = {"return": "%2Fverify%3Fr%3D1%26u%3D%252Fsign%253Freturn%253D%25252F"}
    headers2: dict = common_headers.copy()
    headers2["Referer"] = "https://www.farpost.ru/verify?r=1&u=%2Fsign%3Freturn%3D%252F"
    session.get(ConstUrl.URL2.value, params=params2, headers=headers2)

    response: requests.models.Response = session.get(ConstUrl.URL_SING.value)
    tree_csrf: html.HtmlElement = html.fromstring(response.text)
    csrf_token_value: str = tree_csrf.xpath("""//*[@id="csrfToken"]/@value""")[-1]
    data: dict = {
        "csrfToken": csrf_token_value,
        "radio": "sign",
        "sign": f"{user.login}",
        "password": f"{user.password}",
    }

    response = session.post(ConstUrl.URL_LOGIN.value, data=data)

    if requests.utils.dict_from_cookiejar(session.cookies).get("login"):
        cookies_dict: CookiesSchema = CookiesSchema(**requests.utils.dict_from_cookiejar(session.cookies))
        await async_add_data(Cookies, cookies_dict)
        return cookies_dict
    else:
        return update_cookies(user)


@router.get("/get_cookies_with_user", tags=["Система контроля"], summary="Возвращает куки для пользователя")
async def get_cookies_with_user(login: str) -> CookiesSchema:
    """Получение куков для пользователя по login"""

    async with get_async_session() as session:
        result = await session.execute(select(Cookies).filter(Cookies.login == login))
        cookies = result.scalars().first()
        if cookies:
            data = cookies.to_read_model()
            return data
        else:
            raise HTTPException(status_code=404, detail="User not found") 

@router.get("/update_cookies", tags=["Система контроля"], summary="Обновление куков для всех пользоватей")
async def get_update_cookies() -> None:
    """Обновление куков для всех пользоватей"""

    async with get_async_session() as session:
        result = await session.execute(select(User))
        users = result.fetchall()
        for user in users:
            await update_cookies(user=user[0].to_read_model())


@router.get("/get_active_data_close_none", tags=["Система контроля"], summary='Возвращает "Работающая запись"')
async def get_active_data_close_none() -> List[AbsActiveMergeSchema]:
    """Получение всех активных объявлений"""

    async with get_async_session() as session:
        result = await session.execute(
            select(
                AbsActive.abs_active_id,
                Abs.user_id,
                Abs.link_main_img,
                Abs.link,
                Abs.name_farpost,
                Abs.city_english,
                Abs.categore,
                Abs.subcategories,
                Abs.category_attribute,
                Abs.abs_id,
                AbsActive.position,
                AbsActive.price_limitation,
                AbsActive.date_creation,
                AbsActive.date_closing,
            )
            .join(Abs, Abs.abs_id == AbsActive.abs_id)
            .filter(AbsActive.date_closing.is_(None))
        )
        data = result.fetchall()
        new_data = [
            AbsActiveMergeSchema(
                abs_active_id=i[0],
                user_id=i[1],
                link_main_img=i[2],
                link=i[3],
                name_farpost=i[4],
                city_english=i[5],
                categore=i[6],
                subcategories=i[7],
                category_attribute=i[8],
                abs_id=i[9],
                position=i[10],
                price_limitation=i[11],
                date_creation=i[12],
                date_closing=i[13],
            )
            for i in data
        ]
        return new_data


@router.get(
    "/get_user_with_abs_active", tags=["Система контроля"], summary='Получение пользователя по uuid "Активная запись"'
)
async def get_user_with_abs_active(abs_active_id: UUID) -> UserSchema:
    """Получение пользовательских данных по id активного объявсления"""

    async with get_async_session() as session:
        result = await session.execute(
            select(User)
            .join(Abs, Abs.user_id == User.user_id)
            .join(AbsActive, Abs.abs_id == AbsActive.abs_id)
            .filter(AbsActive.abs_active_id == abs_active_id)
        )
        user = result.scalars().first()
        data = user.to_read_model()
        return data


@router.get(
    "/get_abs_active_by_user",
    tags=["Приложение"],
    summary='Получение все "Активная запись" для пользователя по его логину',
)
async def get_abs_active_by_user(user_login: str) -> List[AbsActiveMergeSchema]:
    """
    Получает все объявления из таблицы AbsActive по user_login
    """

    async with get_async_session() as session:
        result = await session.execute(select(User).filter_by(login=user_login))
        user = result.scalars().first()
        if user:
            result = await session.execute(
                select(
                    AbsActive.abs_active_id,
                    Abs.user_id,
                    Abs.link_main_img,
                    Abs.link,
                    Abs.name_farpost,
                    Abs.city_english,
                    Abs.categore,
                    Abs.subcategories,
                    Abs.category_attribute,
                    Abs.abs_id,
                    AbsActive.position,
                    AbsActive.price_limitation,
                    AbsActive.date_creation,
                    AbsActive.date_closing,
                )
                .join(Abs, Abs.abs_id == AbsActive.abs_id)
                .filter(Abs.user_id == user.user_id)
            )
            data = result.fetchall()
            new_data = [
                AbsActiveMergeSchema(
                    abs_active_id=i[0],
                    user_id=i[1],
                    link_main_img=i[2],
                    link=i[3],
                    name_farpost=i[4],
                    city_english=i[5],
                    categore=i[6],
                    subcategories=i[7],
                    category_attribute=i[8],
                    abs_id=i[9],
                    position=i[10],
                    price_limitation=i[11],
                    date_creation=i[12],
                    date_closing=i[13],
                )
                for i in data
            ]
            return new_data
        else:
            raise HTTPException(status_code=404, detail="User not found")


@router.get("/creact_abs_active", tags=["Приложение"], summary='Создание "Работающий записи"')
async def creact_abs_active(user_login: str, abs_id: int, position: int, price_limitation: float) -> AbsActiveSchema:
    """
    Создание новой записи для отслеживания
    """

    async with get_async_session() as session:
        result = await session.execute(select(User).filter_by(login=user_login))
        user = result.scalars().first()

        if user:
            result = await session.execute(
                select(AbsActive).join(Abs).filter(Abs.user_id == user.user_id, AbsActive.date_closing.is_(None))
            )
            active_record = result.scalars().first()

            if active_record:
                raise HTTPException(status_code=418, detail=f"{active_record.abs_id}")
            else:
                uuid_abs_active: UUID = uuid4()
                new_abs_active: AbsActiveSchema = AbsActiveSchema(
                    abs_active_id=uuid_abs_active,
                    abs_id=abs_id,
                    position=position,
                    price_limitation=price_limitation,
                    date_creation=datetime.now(),
                    date_closing=None,
                )
                await async_add_data(AbsActive, new_abs_active)
                return new_abs_active
        else:
            raise HTTPException(status_code=404, detail="User not found")


@router.get(
    "/stop_abs_active", tags=["Приложение"], summary='Перемещение "Работающий записи" в статус "Активная запись" '
)
async def stop_abs_active(abs_active_id: UUID) -> AbsActiveSchema:
    """
    Останавливает отслеживание, устанавливая date_closing на текущую дату и время
    """

    async with get_async_session() as session:
        result = await session.execute(select(AbsActive).filter_by(abs_active_id=abs_active_id))
        abs_active_record = result.scalars().first()

        if abs_active_record:
            abs_active_record.date_closing = datetime.now()

            session.add(abs_active_record)
            await session.commit()

            return abs_active_record.to_read_model()
        else:
            raise HTTPException(status_code=404, detail="AbsActive record not found")


@router.get("/get_items", tags=["Приложение"], summary='Получение всех "Записей" для пользователя по логину')
async def get_items(user_login: str, session: AsyncSession = Depends(get_async_session)) -> List[AbsSchema]:
    """
    Запрос на обьявлений завязаных на пользователя из базы данных
    """

    async with session as session_async:
        ads = await get_ads_by_user_login(user_login, session_async)

    list_abs = [ad.to_read_model() for ad in ads]
    if len(list_abs) > 0:
        return list_abs
    else:
        raise HTTPException(status_code=404, detail="AbsActive record not found")


@router.post(
    "/update_items_user",
    tags=["Приложение"],
    summary='Получение всех "Записей" с farpost для пользователя по логину и данных от входа',
)
async def update_items_user(
    user_login: str, response: ResponseLoginSchema, async_session: AsyncSession = Depends(get_async_session)
) -> List[AbsSchema]:
    """
    Запрос на обновление объявлений, связанных с пользователем, и удаление неактивных объявлений.
    """

    session = requests.Session()
    session.headers.update(response.headers.dict())
    for key, value in response.cookies.dict().items():
        session.cookies.set(key, value)

    try:
        result: requests.models.Response = session.get("https://www.farpost.ru/personal/actual/bulletins")
        tree_item: html.HtmlElement = html.fromstring(result.text)
        async with async_session as session_async:
            user_id = await get_user_id_by_login(user_login, session_async)
            if user_id is None:
                raise HTTPException(status_code=404, detail="User not found")

            # Получаем список текущих активных ID объявлений
            current_active_ids = {
                int(id_.strip())
                for id_ in tree_item.xpath("//*[contains(@class, 'bull-item__image-cell')]/@data-bulletin-id")
            }

            # Получаем список всех записей пользователя в БД
            all_user_ads = await Abs.get_user_ads(user_id, session_async)

            # Определяем ID объявлений для удаления
            ids_to_delete = {ad.abs_id for ad in all_user_ads if ad.abs_id not in current_active_ids}

            # Удаляем неактивные объявления
            await Abs.delete_ads_by_ids(ids_to_delete, session_async)

            # Теперь добавление и обновление активных объявлений
            items_list: list[AbsSchema] = [
                AbsSchema(
                    **{
                        "abs_id": int(id_.strip()),
                        "user_id": user_id,
                        "name_farpost": name.strip(),
                        "city_english": city.strip(),
                        "category_attribute": attr.strip()
                        .replace(attr.split("/")[-1], "")
                        .replace("https://www.farpost.ru/", ""),
                        "categore": attr.strip()
                        .replace(attr.split("/")[-1], "")
                        .replace("https://www.farpost.ru/", "")
                        .split("/")[1],
                        "subcategories": attr.strip()
                        .replace(attr.split("/")[-1], "")
                        .replace("https://www.farpost.ru/", "")
                        .split("/")[2],
                        "link": attr,
                        "link_main_img": img,
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
            for item in items_list:
                await async_add_data(Abs, item)

            return items_list
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", tags=["Приложение", "Система контроля"], summary="Вход по логину и пароля с farpost")
def auth(login: str = Form(...), password: str = Form(...)) -> ResponseLoginSchema:
    """
    Запрос на авторизацию
    """

    session = requests.Session()
    common_headers: dict = {i.custom_name: i.value for i in ConstHeader}

    params1: dict = {"u": "/sign?return=%252F"}
    headers1: dict = common_headers.copy()
    headers1["Referer"] = "https://www.farpost.ru/verify?r=1&u=%2Fsign%3Freturn%3D%252F"
    session.get(ConstUrl.URL1.value, params=params1, headers=headers1)

    params2: dict = {"return": "%2Fverify%3Fr%3D1%26u%3D%252Fsign%253Freturn%253D%25252F"}
    headers2: dict = common_headers.copy()
    headers2["Referer"] = "https://www.farpost.ru/verify?r=1&u=%2Fsign%3Freturn%3D%252F"
    session.get(ConstUrl.URL2.value, params=params2, headers=headers2)

    response: requests.models.Response = session.get(ConstUrl.URL_SING.value)
    tree_csrf: html.HtmlElement = html.fromstring(response.text)
    csrf_token_value: str = tree_csrf.xpath("""//*[@id="csrfToken"]/@value""")[-1]
    data: dict = {
        "csrfToken": csrf_token_value,
        "radio": "sign",
        "sign": f"{login}",
        "password": f"{password}",
    }

    response = session.post(ConstUrl.URL_LOGIN.value, data=data)

    if requests.utils.dict_from_cookiejar(session.cookies).get("login"):
        uuid_user: UUID = uuid4()
        user_data: UserSchema = UserSchema(user_id=uuid_user, login=login, password=password)
        asyncio.run(async_add_data(User, user_data))
        headers_dict: HeadersSchema = HeadersSchema(**dict(response.headers))
        cookies_dict: CookiesSchema = CookiesSchema(**requests.utils.dict_from_cookiejar(session.cookies))
        return ResponseLoginSchema(headers=headers_dict, cookies=cookies_dict)
    else:
        raise HTTPException(
            status_code=401,
            detail="Ошибка при вводе логина или пароля, если все данные верны то возможно farpost просит подтверждение через sms код",
        )
