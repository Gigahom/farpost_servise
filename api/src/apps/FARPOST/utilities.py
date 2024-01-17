from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.models import Base, Abs, User, Cookies
from .schemas import BaseModel
from src.settings.db import get_async_session


async def get_ads_by_user_login(login: str, async_session: AsyncSession):
    """
    Функция получения объявление по логин пользователя
    """
    
    result = await async_session.execute(
        select(Abs).join(User, User.user_id == Abs.user_id).where(User.login == login)
    )
    ads = result.scalars().all()
    return ads


async def async_add_data(class_model: Base, data: BaseModel):
    """
    Функция для добавления данных в таблицы
    """
    
    async with get_async_session() as session:
        await class_model.save_from_schema(schema=data, session=session)


async def get_user_id_by_login(login: str, async_session: AsyncSession):
    """
    Функция получения user_id по login
    """
    
    result = await async_session.execute(select(User.user_id).filter_by(login=login))
    user_id = result.scalar_one_or_none()
    return user_id

async def get_cookies_by_user_login(login: str) -> dict:
    """
    Возвращает экземпляр Cookies для пользователя по его login.
    """

    async with get_async_session() as session:
        result = await session.execute(select(Cookies).join(User).where(User.login == login))
        cookies_instance = result.scalars().first()

        if cookies_instance:
            return {
                "ring": cookies_instance.ring,
                "boobs": cookies_instance.boobs,
                "pony": cookies_instance.pony,
                "login": cookies_instance.login,
                "protected_deals_top_line": cookies_instance.protected_deals_top_line,
            }
        else:
            return {}
