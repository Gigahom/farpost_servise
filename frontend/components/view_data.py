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

        content_all = ft.Container(
            content=ft.DataTable(
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
                    for i in requests.post(RequstsApi.Items.value, json=self.master.headers_cookies).json()
                ],
            ),
            alignment=ft.alignment.center,
        )
        self.page.add(
            ft.Tabs(
                selected_index=1,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        icon=ft.icons.SETTINGS,
                        content=ft.Container(
                            content=ft.Column([ft.ElevatedButton(text="Выйти", on_click=self.out)]),
                            alignment=ft.alignment.center,
                        ),
                    ),
                    ft.Tab(
                        text="Все",
                        content=content_all,
                    ),
                    ft.Tab(
                        text="Активные",
                        content=ft.Text("This is Tab 3"),
                    ),
                ],
                expand=1,
            )
        )

    def creact_row(self, data_row):
        if not isinstance(data_row, dict):
            print(f"Неправильный тип данных: {type(data_row)}")
            return ft.DataRow(cells=[])

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(data_row["name"])),
                ft.DataCell(ft.Text(data_row["city"])),
                ft.DataCell(ft.Text(data_row["categore"])),
                ft.DataCell(ft.Text(data_row["subcategories"])),
                ft.DataCell(
                    ft.Row(
                        [
                            ft.Image(
                                src=data_row["img"],
                                width=150,
                                height=200,
                            )
                        ]
                    )
                ),
            ],
        )

    def out(self, e):
        login = importlib.import_module("components.login")
        self.master.headers_cookies = None
        self.master.new_win(login.Login)
