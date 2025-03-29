import os
import sys
import flet as ft
import datetime

# Добавляем путь к модулю "manager", если он отсутствует
sys.path.append(os.path.dirname(os.path.abspath(_file_)))

from manager import dbConnection as dbc
from manager import db as db
from manager.chatManager import ChatManager as cm
from manager.userManager import UserManager as um


class MyApp:
    def _init_(self, user_repo):
        self.user_repo = user_repo
        self.chat_manager = cm()
        self.user_manager = um()

    def main(self, page: ft.Page):
        page.title = "Authorization and Registration"
        page.window_max_width = 1600
        page.window_max_height = 1200
        page.window_resizable = False
        page.vertical_alignment = ft.MainAxisAlignment.CENTER

        def route_change(e):
            page.views.clear()
            if page.route == "/":
                user_id = self.user_manager.load_user_id()
                if user_id:
                    page.views.append(dashboard_page(page, user_id))
                else:
                    page.views.append(login_page(page))
            elif page.route.startswith("/dashboard/"):
                try:
                    user_id = int(page.route.split("/")[-1])
                    page.views.append(dashboard_page(page, user_id))
                except ValueError:
                    print("Error: invalid user_id in URL")
                    page.go("/")
            page.update()

        def login_page(page):
            login_field = ft.TextField(label="Login", bgcolor="#D9D9D9", width=350, border_radius=10)
            password_field = ft.TextField(label="Password", bgcolor="#D9D9D9", width=350, password=True, border_radius=10)
            result_text = ft.Text()

            def handle_register(e):
                if login_field.value and password_field.value:
                    result = self.user_repo.create_user(login_field.value, password_field.value)
                    result_text.value = "Registration successful!" if result else "Registration failed!"
                else:
                    result_text.value = "Please fill in all the fields!"
                page.update()

            def handle_login(e):
                if login_field.value and password_field.value:
                    success, user_id = self.user_repo.authenticate_user(login_field.value, password_field.value)
                    if success:
                        self.user_manager.save_user_id(user_id)
                        page.go(f"/dashboard/{user_id}")
                    else:
                        result_text.value = "Error: Incorrect login or password!"
                else:
                    result_text.value = "Error: Login and password fields cannot be empty!"
                page.update()

            return ft.View(
                "/",
                bgcolor="#9BCCBF",
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Column([
                        ft.Text("Equilibri.Ai", size=128, weight="bold", color="#000000"),
                        login_field,
                        password_field,
                        ft.Row([
                            ft.ElevatedButton("Login", on_click=handle_login),
                            ft.ElevatedButton("Register", on_click=handle_register),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        result_text,
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ],
            )

        def dashboard_page(page, user_id):
            if not isinstance(user_id, int):
                print("Error: user_id must be an integer")
                return ft.View("/", controls=[ft.Text("Error: invalid user_id")])

            my_app = MyApp(self.user_repo)
            my_app.chat_manager.message_input.on_submit = my_app.chat_manager.send_message

            quick_buttons = ft.Row([
                ft.ElevatedButton("Remind me about the consultation",
                                  on_click=lambda e: my_app.chat_manager.send_message(e, "Reminded me about the consultation")),
                ft.ElevatedButton("Postponement of consultation",
                                  on_click=lambda e: my_app.chat_manager.send_message(e, "Postponement of consultation")),
                ft.ElevatedButton("Cancellation of consultation",
                                  on_click=lambda e: my_app.chat_manager.send_message(e, "Cancellation of consultation")),
            ], alignment=ft.MainAxisAlignment.CENTER)

            # Новый календарь
            def open_date_picker(e):
                date_picker.pick_date()

            date_picker = ft.DatePicker(
                on_change=lambda e: print("Выбрана дата:", date_picker.value),
                first_date=datetime.date(2025, 1, 1),
                last_date=datetime.date(2025, 12, 31),
            )

            calendar_button = ft.IconButton(
                icon=ft.icons.CALENDAR_MONTH,
                on_click=open_date_picker
            )

            return ft.View(
                f"/dashboard/{user_id}",
                bgcolor="#5B7065",
                controls=[
                    ft.Container(
                        content=ft.Text("Equilibri.Ai", size=42, weight="bold", color="white"),
                        alignment=ft.alignment.top_center,
                        padding=ft.padding.only(top=5, left=20)
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Menu", size=20, weight="bold", color="white"),
                                        ft.Divider(),
                                        my_app.chat_manager.chat_buttons,
                                        ft.TextButton("New Chat", on_click=lambda e: my_app.chat_manager.create_new_chat(e)),
                                    ]
                                ),
                                bgcolor="#3A3A3A",
                                width=250,
                                height=700,
                                padding=10,
                                border_radius=10
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        my_app.chat_manager.header,
                                        ft.Container(my_app.chat_manager.chat_display, height=400, expand=True, padding=10),
                                        quick_buttons,
                                        ft.Row([
                                            my_app.chat_manager.message_input,
                                            ft.IconButton(
                                                icon=ft.icons.SEND,
                                                icon_color=ft.Colors.BLACK,
                                                bgcolor="#edeefa",
                                                on_click=my_app.chat_manager.send_message
                                            )
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                        ft.Row([
                                            ft.ElevatedButton("Clear Chat", on_click=lambda e: my_app.chat_manager.clear_chat(e),
                                                              bgcolor=ft.Colors.WHITE, color=ft.Colors.BLACK)
                                        ], alignment=ft.MainAxisAlignment.END),
                                    ]
                                ),
                                bgcolor="#2C2C2C",
                                padding=10,
                                border_radius=10,
                                expand=True
                            )
                        ],
                        expand=True
                    ),
                    ft.ElevatedButton("Log Out", on_click=lambda e: self.user_manager.clear_user_session() or page.go("/")),
                    date_picker  # Добавляем виджет календаря на страницу
                ]
            )

        page.on_route_change = route_change
        page.go("/")


if _name_ == "_main_":
    db_instance = db.Database('localhost', 'postgres', '0000', 'postgres')
    connection = db_instance.connection()

    if connection:
        user_repo = dbc.UserRepository(connection)
        app = MyApp(user_repo)
        ft.app(target=app.main)
    else:
        print("Failed to establish a database connection!")
