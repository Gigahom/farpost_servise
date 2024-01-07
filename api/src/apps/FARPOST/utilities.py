from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.models import Base, Abs, User
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
