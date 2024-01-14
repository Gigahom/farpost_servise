from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Float, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.future import select
from fastapi import Depends
import sqlalchemy.types as types
from sqlalchemy import delete, update

from uuid import UUID, uuid4
from typing import List, Set
from datetime import datetime

from src.settings.db import Base, get_async_session, AsyncSession
from src.apps.FARPOST.schemas import UserSchema, AbsSchema, AbsActiveSchema, CookiesSchema


class Cookies(Base):
    __tablename__ = "cookies"
    cookies_id: Mapped[UUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True)
    ring: Mapped[str] = mapped_column(String)
    boobs: Mapped[str] = mapped_column(String)
    pony: Mapped[str] = mapped_column(String)
    login: Mapped[str] = mapped_column(String)
    protected_deals_top_line: Mapped[str] = mapped_column(String)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_farpost.user_id"))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cookies")

    def to_read_model(self) -> CookiesSchema:
        """
        Метод конвертирет данные в схему CookiesSchema
        """

        return CookiesSchema(
            ring=self.ring,
            boobs=self.boobs,
            pony=self.pony,
            login=self.login,
            protected_deals_top_line=self.protected_deals_top_line,
        )

    @classmethod
    async def save_from_schema(cls, schema: CookiesSchema, session: AsyncSession) -> None:
        """
        Метод сохрание схемы CookiesSchema в базу данных
        """

        result = await session.execute(select(cls).filter_by(login=schema.login))
        instance = result.scalars().first()

        result_user = await session.execute(select(User).filter_by(login=schema.login))
        instance_user = result_user.scalars().first()

        if instance:
            instance.login = schema.login
            instance.ring = schema.ring
            instance.boobs = schema.boobs
            instance.pony = schema.pony
            instance.protected_deals_top_line = schema.protected_deals_top_line
        else:
            instance = cls(
                cookies_id=uuid4(),
                ring=schema.ring,
                boobs=schema.boobs,
                pony=schema.pony,
                login=schema.login,
                protected_deals_top_line=schema.protected_deals_top_line,
                user_id=instance_user.user_id,
            )
            session.add(instance)
        await session.commit()


class User(Base):
    """
    Модель базы пользователя в базе данных в содержет поля:
    - user_id: uuid,
    - login: str,
    - password: str

    Так же есть методы:
    - to_read_model-> конвертирует данные из sql в схему UserSchema
    - save_from_schema-> добавляет данные или обновляет из схемы UserSchema в базе данных
    """

    __tablename__ = "user_farpost"
    user_id: Mapped[UUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True)
    login: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)

    # Relationships
    abses: Mapped[List["Abs"]] = relationship("Abs", back_populates="user")
    cookies: Mapped[List["Cookies"]] = relationship("Cookies", back_populates="user")

    def to_read_model(self) -> UserSchema:
        """
        Метод конвертирет данные в схему UserSchema
        """

        return UserSchema(user_id=self.user_id, login=self.login, password=self.password)

    @classmethod
    async def save_from_schema(cls, schema: UserSchema, session: AsyncSession) -> None:
        """
        Метод сохрание схемы UserSchema в базу данных
        """

        result = await session.execute(select(cls).filter_by(login=schema.login))
        instance = result.scalars().first()

        if instance:
            instance.login = schema.login
            instance.password = schema.password
        else:
            instance = cls(user_id=schema.user_id, login=schema.login, password=schema.password)
            session.add(instance)
        await session.commit()


class Abs(Base):
    """
    Модель базы пользователя в базе данных в содержет поля abs_id: int, user_id: uuid, link_main_img: str, link: str, name_farpost: str, city_english: str, chapter: str
    Так же есть методы:
    to_read_model-> конвертирует данные из sql в схему AbsSchema
    save_from_schema-> добавляет данные или обновляет из схемы AbsSchema в базе данных
    """

    __tablename__ = "abs"
    abs_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_farpost.user_id"))
    link_main_img: Mapped[str] = mapped_column(String)
    link: Mapped[str] = mapped_column(String)
    name_farpost: Mapped[str] = mapped_column(String)
    city_english: Mapped[str] = mapped_column(String)
    categore: Mapped[str] = mapped_column(String)
    subcategories: Mapped[str] = mapped_column(String)
    category_attribute: Mapped[str] = mapped_column(String)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="abses")
    abs_actives: Mapped[List["AbsActive"]] = relationship("AbsActive", back_populates="abs")

    def to_read_model(self) -> AbsSchema:
        """
        Метод конвертирет данные в схему AbsSchema
        """
        return AbsSchema(
            abs_id=self.abs_id,
            user_id=self.user_id,
            link_main_img=self.link_main_img,
            link=self.link,
            name_farpost=self.name_farpost,
            city_english=self.city_english,
            categore=self.categore,
            subcategories=self.subcategories,
            category_attribute=self.category_attribute,
        )

    @classmethod
    async def save_from_schema(cls, schema: AbsSchema, session: AsyncSession) -> None:
        """
        Метод сохрание схемы AbsSchema в базу данных
        """
        result = await session.execute(select(cls).filter_by(abs_id=schema.abs_id))
        instance = result.scalars().first()

        if instance:
            for key, value in schema.dict().items():
                setattr(instance, key, value)
        else:
            instance = cls(**schema.dict())
            session.add(instance)
        await session.commit()

    @classmethod
    async def get_user_ads(cls, user_id: UUID, session: AsyncSession) -> List["Abs"]:
        """Получение всех объявлений пользователя"""

        result = await session.execute(select(cls).filter_by(user_id=user_id))
        return result.scalars().all()

    @classmethod
    async def delete_ads_by_ids(cls, ids: Set[int], session: AsyncSession) -> None:
        """Удаление объявлений по их ID с учетом связанных записей, не удаляя записи из AbsActive"""

        await session.execute(update(AbsActive).where(AbsActive.abs_id.in_(ids)).values(abs_id=None))

        await session.execute(delete(cls).where(cls.abs_id.in_(ids)))
        await session.commit()


class AbsActive(Base):
    """
    Модель базы пользователя в базе данных в содержет поля abs_id: int, abs_active_id: uuid, position: int, price_limitation: float, date_creation: str, date_closing: str
    Так же есть методы:
    to_read_model-> конвертирует данные из sql в схему AbsActiveSchema
    save_from_schema-> добавляет данные или обновляет из схемы AbsActiveSchema в базе данных
    """

    __tablename__ = "abs_active"
    abs_active_id: Mapped[UUID] = mapped_column(primary_key=True)
    abs_id: Mapped[int] = mapped_column(ForeignKey("abs.abs_id", ondelete="SET NULL"), nullable=True)
    position: Mapped[int] = mapped_column()
    price_limitation: Mapped[float] = mapped_column(types.Float)
    date_creation: Mapped[datetime] = mapped_column(types.TIMESTAMP)
    date_closing: Mapped[datetime] = mapped_column(types.TIMESTAMP, nullable=True)

    # Relationships
    abs: Mapped["Abs"] = relationship("Abs", back_populates="abs_actives")

    def to_read_model(self) -> AbsActiveSchema:
        """
        Метод конвертирет данные в схему AbsActiveSchema
        """

        return AbsActiveSchema(
            abs_active_id=self.abs_active_id,
            abs_id=self.abs_id,
            position=self.position,
            price_limitation=self.price_limitation,
            date_creation=self.date_creation,
            date_closing=self.date_closing,
        )

    @classmethod
    async def save_from_schema(cls, schema: AbsActiveSchema, session: AsyncSession) -> None:
        """
        Метод сохрание схемы AbsActiveSchema в базу данных
        """

        result = await session.execute(select(cls).filter_by(abs_active_id=schema.abs_active_id))
        instance = result.scalars().first()
        if instance:
            for key, value in schema.dict().items():
                setattr(instance, key, value)
        else:
            instance = cls(**schema.dict())
            session.add(instance)
        await session.commit()
