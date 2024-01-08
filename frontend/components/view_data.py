import flet as ft
import requests

import importlib
from typing import Union
from time import sleep
from uuid import UUID

from const.const import RequstsApi
from components.abs_class import ContentAbstract, PagesAbstract, AlertDialogInput


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

        self.dlg: AlertDialogInput = AlertDialogInput()

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
                                                ft.DataColumn(ft.Text("Настройки")),
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
                                                ft.DataColumn(ft.Text("Закрыть активность")),
                                                ft.DataColumn(ft.Text("id объявления")),
                                                ft.DataColumn(ft.Text("Закрепленая позиция")),
                                                ft.DataColumn(ft.Text("Лимит цены")),
                                                ft.DataColumn(ft.Text("Дата начала")),
                                                ft.DataColumn(ft.Text("Дата конца")),
                                            ],
                                            rows=[
                                                self.creact_row_active(i)
                                                for i in requests.get(
                                                    RequstsApi.AbsActiveWithUser.value
                                                    + f"""?user_login={self.login}"""
                                                ).json()
                                            ],
                                        ),
                                    ],
                                    height=600,
                                    scroll=ft.ScrollMode.ALWAYS,
                                ),
                                ft.Column(
                                    [ft.IconButton(icon=ft.icons.AUTORENEW, on_click=self.update_data_active)],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                    ),
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
                ft.DataCell(
                    ft.IconButton(
                        icon=ft.icons.PENDING_ACTIONS_ROUNDED,
                        on_click=lambda e: self.open_dialog(e, data_row["abs_id"]),
                    )
                ),
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

    def creact_row_active(self, data_row: dict) -> ft.DataRow:
        """
        Создание данных в нутри таблицы активные
        """

        if not isinstance(data_row, dict):
            print(f"Неправильный тип данных: {type(data_row)}")
            return ft.DataRow(cells=[])
        
        return ft.DataRow(
            cells=[
                ft.DataCell(
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        on_click=lambda e: self.open_dialog_confirmation(e, data_row["abs_active_id"]),
                    )
                ),
                ft.DataCell(ft.Text(data_row["abs_id"])),
                ft.DataCell(ft.Text(data_row["position"])),
                ft.DataCell(ft.Text(data_row["price_limitation"])),
                ft.DataCell(ft.Text(data_row["date_creation"])),
                ft.DataCell(ft.Text(data_row["date_closing"])),
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
                                    ft.DataColumn(ft.Text("Настройки")),
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

    def update_data_active(self, e) -> None:
        """
        Запрос на обновление
        """

        self.tab_menu.tabs[2].content = ft.Container(
            content=ft.Row(
                [
                    ft.Column(),
                    ft.Column(
                        [
                            ft.DataTable(
                                data_row_min_height=150,
                                data_row_max_height=200,
                                columns=[
                                    ft.DataColumn(ft.Text("Закрыть активность")),
                                    ft.DataColumn(ft.Text("id объявления")),
                                    ft.DataColumn(ft.Text("Закрепленая позиция")),
                                    ft.DataColumn(ft.Text("Лимит цены")),
                                    ft.DataColumn(ft.Text("Дата начала")),
                                    ft.DataColumn(ft.Text("Дата конца")),
                                ],
                                rows=[
                                    self.creact_row_active(i)
                                    for i in requests.get(
                                        RequstsApi.AbsActiveWithUser.value + f"""?user_login={self.login}"""
                                    ).json()
                                ],
                            ),
                        ],
                        height=600,
                        scroll=ft.ScrollMode.ALWAYS,
                    ),
                    ft.Column(
                        [ft.IconButton(icon=ft.icons.AUTORENEW, on_click=self.update_data_active)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
        )

        self.page.update()

    def open_dialog_confirmation(self, e, abs_id) -> None:
        self.dlg = AlertDialogInput(
            abs_id=abs_id,
            title=ft.Text(f"Подтвертите что хотите отменить активность записи {abs_id}"),
            modal=True,
            actions=[
                ft.TextButton("Прекратить", on_click=lambda e: self.close_active(e, abs_id)),
                ft.TextButton("Отменить", on_click=self.close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = self.dlg
        self.dlg.open = True
        self.page.update()

    def open_dialog(self, e, abs_id) -> None:
        """Создание окна для сбора параметров"""

        self.dlg = AlertDialogInput(
            abs_id=abs_id,
            modal=True,
            content=ft.Column(
                controls=[
                    ft.TextField(
                        label="Позиция",
                        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
                    ),
                    ft.TextField(
                        label="Лимит",
                        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
                    ),
                ],
                width=600,
                height=300,
            ),
            actions=[
                ft.TextButton("Начать", on_click=self.creact_active),
                ft.TextButton("Отменить", on_click=self.close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = self.dlg
        self.dlg.open = True
        self.page.update()

    def close_dlg(self, e) -> None:
        """Закрыть диалоговое окно"""

        self.dlg.open = False
        self.page.update()

    def creact_active(self, e) -> None:
        """Создание записи abs_active"""

        user_login: str = self.login
        abs_id: Union[UUID, int, None] = self.dlg.abs_id
        position: int = int(self.dlg.content.controls[0].value)
        price_limitation: float = float(self.dlg.content.controls[0].value)
        response = requests.get(
            RequstsApi.CreactAbsActive.value
            + f"?user_login={user_login}&abs_id={abs_id}&position={position}&price_limitation={price_limitation}"
        )
        if response.status_code == 200:
            self.dlg.open = False
            self.page.update()
        else:
            detail = response.json().get("detail")
            self.dlg.open = False
            self.page.update()

    def close_active(self, e, abs_id) -> None:
        """Закрытие записи abs_active"""

        requests.get(RequstsApi.StopAbsActive.value + f"?abs_active_id={abs_id}")
        self.dlg.open = False
        self.page.update()
        sleep(1)
        self.update_data_active(1)
