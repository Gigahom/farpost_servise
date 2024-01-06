import flet as ft

from components.base import Pages


def main(page: ft.Page):
    Pages(page=page)


ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=3000)
