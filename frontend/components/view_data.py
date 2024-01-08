import flet as ft
import requests

import importlib

from const.const import RequstsApi
from components.abs_class import ContentAbstract, PagesAbstract


class ViewData(ContentAbstract):
    """
    Страница просмотра записей
    """

    def __init__(self, page: ft.Page, master: PagesAbstract):
        self.master = master
        self.page = page

        if isinstance(self.master.headers_cookies, dict) and "cookies" in self.master.headers_cookies:
            cookies = self.master.headers_cookies["cookies"]
            self.login: str = ""
            if isinstance(cookies, dict):
                self.login = cookies.get("login")
            else:
                self.login = ""
                self.out(1)
        else:
            self.login = ""
            self.out(1)

        self.tab_settings_content = ft.Container(
            content=ft.Column([ft.ElevatedButton(text="Выйти", on_click=self.out)]),
            alignment=ft.alignment.center,
        )
        self.tab_menu = ft.Tabs(
            selected_index=1,
            animation_duration=300,
            tabs=[
                ft.Tab(icon=ft.icons.SETTINGS, content=self.tab_settings_content),
                ft.Tab(
                    text="Все",
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Column(),
                                ft.Column(
                                    [
                                        ft.DataTable(
                                            data_row_min_height=150,
                                            data_row_max_height=200,
                                            columns=[
                                                ft.DataColumn(ft.Text("Название")),
                                                ft.DataColumn(ft.Text("Город")),
                                                ft.DataColumn(ft.Text("Категория")),
                                                ft.DataColumn(ft.Text("Подкатегория")),
                                                ft.DataColumn(ft.Text("Изображение")),
                                            ],
                                            rows=[
                                                self.creact_row(i)
                                                for i in requests.get(
                                                    RequstsApi.Items.value + f"""?user_login={self.login}"""
                                                ).json()
                                            ],
                                        ),
                                    ],
                                    height=600,
                                    scroll=ft.ScrollMode.ALWAYS,
                                ),
                                ft.Column(
                                    [ft.IconButton(icon=ft.icons.AUTORENEW, on_click=self.update_data)],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                    ),
                ),
                ft.Tab(
                    text="Активные",
                    content=ft.Text("This is Tab 3"),
                ),
            ],
            expand=1,
        )
        self.page.add(self.tab_menu)

    def creact_row(self, data_row: dict) -> ft.DataRow:
        """
        Создание данных в нутри таблицы
        """

        if not isinstance(data_row, dict):
            print(f"Неправильный тип данных: {type(data_row)}")
            return ft.DataRow(cells=[])

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(data_row["name_farpost"])),
                ft.DataCell(ft.Text(data_row["city_english"])),
                ft.DataCell(ft.Text(data_row["categore"])),
                ft.DataCell(ft.Text(data_row["subcategories"])),
                ft.DataCell(
                    ft.Image(
                        src=data_row["link_main_img"],
                        width=150,
                        height=200,
                    )
                ),
            ],
        )

    def out(self, e) -> None:
        """
        Метод для выхода в авторизацию
        """

        login = importlib.import_module("components.login")
        self.master.headers_cookies = None
        self.master.new_win(login.Login)

    def update_data(self, e) -> None:
        """
        Запрос на обновление
        """

        self.tab_menu.tabs[1].content = ft.Container(
            content=ft.Row(
                [
                    ft.Column(),
                    ft.Column(
                        [
                            ft.DataTable(
                                data_row_min_height=150,
                                data_row_max_height=200,
                                columns=[
                                    ft.DataColumn(ft.Text("Название")),
                                    ft.DataColumn(ft.Text("Город")),
                                    ft.DataColumn(ft.Text("Категория")),
                                    ft.DataColumn(ft.Text("Подкатегория")),
                                    ft.DataColumn(ft.Text("Изображение")),
                                ],
                                rows=[
                                    self.creact_row(i)
                                    for i in requests.post(
                                        RequstsApi.Updata.value + f"""?user_login={self.login}""",
                                        json=self.master.headers_cookies,
                                    ).json()
                                ],
                            ),
                        ],
                        height=600,
                        scroll=ft.ScrollMode.ALWAYS,
                    ),
                    ft.Column(
                        [ft.IconButton(icon=ft.icons.AUTORENEW, on_click=self.update_data)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
        )

        self.page.update()
