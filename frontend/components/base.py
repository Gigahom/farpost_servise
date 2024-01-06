import flet as ft

from .login import Login
from components.abs_class import PagesAbstract


class Pages(PagesAbstract):
    """
    Страница на которой будет меняться контент
    """

    def __init__(self, page):
        self.page = page
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.views = None
        self.headers_cookies = None

        self.new_win(Login)

    def new_win(self, class_name_page, params=None):
        if not params:
            self.page.clean()
            self.views = class_name_page(self.page, self)
        else:
            self.page.clean()
            self.views = class_name_page(self.page, self, params)
