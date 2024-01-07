import flet as ft
import requests

from const.const import RequstsApi
from components.abs_class import ContentAbstract, PagesAbstract
from components.view_data import ViewData


class Login(ContentAbstract):
    """
    Контент авторизации
    """

    def __init__(self, page: ft.Page, master: PagesAbstract):
        self.master = master
        self.page = page

        self.login = ft.TextField(label="Логин")
        self.password = ft.TextField(label="Пароль")
        self.sing = ft.ElevatedButton(text="Войти", on_click=self.sing_click)
        self.load = ft.Row(
            [],
            alignment=ft.MainAxisAlignment.CENTER,
            visible=True,
        )

        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [self.login],
                        alignment=ft.MainAxisAlignment.CENTER,
                        visible=True,
                    ),
                    ft.Row(
                        [self.password],
                        alignment=ft.MainAxisAlignment.CENTER,
                        visible=True,
                    ),
                    ft.Row(
                        [self.sing],
                        alignment=ft.MainAxisAlignment.CENTER,
                        visible=True,
                    ),
                    self.load,
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    def sing_click(self, e):
        """
        Запрос на заголовки и куки для работы внутри приложения
        """
        self.load.controls.append(ft.ProgressBar(width=400, color="amber", bgcolor="#eeeeee"))
        self.page.update()
        data = requests.post(
            RequstsApi.Login.value, data={"login": self.login.value, "password": self.password.value}
        ).json()

        self.master.headers_cookies = data

        self.master.new_win(ViewData)
