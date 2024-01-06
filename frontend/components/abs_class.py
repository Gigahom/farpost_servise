from __future__ import annotations

import flet as ft

from abc import ABC, abstractmethod


class PagesAbstract(ABC):
    """
    Страница на которой будет меняться контент class ABC
    """

    page = None
    views = None
    headers_cookies = None

    @abstractmethod
    def __init__(self, page: ft.Page) -> None:
        pass

    @abstractmethod
    def new_win(self, class_name_page: ContentAbstract, params=None) -> None:
        pass


class ContentAbstract(ABC):
    """
    Контент страницы class ABC
    """

    @abstractmethod
    def __init__(self, page: ft.Page, master: PagesAbstract) -> None:
        pass
