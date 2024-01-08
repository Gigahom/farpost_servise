from __future__ import annotations

import flet as ft

from abc import ABC, abstractmethod
from typing import Union, Dict


class ContentAbstract(ABC):
    """
    Контент страницы class ABC
    """

    @abstractmethod
    def __init__(self, page: ft.Page, master: PagesAbstract) -> None:
        pass


class PagesAbstract(ABC):
    """
    Страница на которой будет меняться контент class ABC
    """

    page = Union[ft.Page, None]
    views = Union[ContentAbstract, None]
    headers_cookies = Union[dict, None]

    @abstractmethod
    def __init__(self, page: ft.Page) -> None:
        pass

    @abstractmethod
    def new_win(self, class_name_page: ContentAbstract, params=None) -> None:
        pass
