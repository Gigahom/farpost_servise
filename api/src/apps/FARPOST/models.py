from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Float, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.future import select
from fastapi import Depends
import sqlalchemy.types as types

from uuid import UUID
from typing import List
from datetime import datetime

from src.settings.db import Base, get_async_session, AsyncSession
from src.apps.FARPOST.schemas import UserSchema, AbsSchema, AbsActiveSchema


class User(Base):
    """
    Модель базы пользователя в базе данных в содержет поля user_id: uuid, login: str, password: str
    Так же есть методы:
    to_read_model-> конвертирует данные из sql в схему UserSchema
    save_from_schema-> добавляет данные или обновляет из схемы UserSchema в базе данных
    """

    __tablename__ = "user_farpost"
    user_id: Mapped[UUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True)
    login: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)

    # Relationships
    abses: Mapped[List["Abs"]] = relationship("Abs", back_populates="user")

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


class AbsActive(Base):
    """
    Модель базы пользователя в базе данных в содержет поля abs_id: int, abs_active_id: uuid, position: int, price_limitation: float, date_creation: str, date_closing: str
    Так же есть методы:
    to_read_model-> конвертирует данные из sql в схему AbsActiveSchema
    save_from_schema-> добавляет данные или обновляет из схемы AbsActiveSchema в базе данных
    """

    __tablename__ = "abs_active"
    abs_active_id: Mapped[UUID] = mapped_column(primary_key=True)
    abs_id: Mapped[int] = mapped_column(ForeignKey("abs.abs_id"))
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
