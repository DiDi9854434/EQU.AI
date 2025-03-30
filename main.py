import os
import webbrowser
import asyncio
import openai

import flet as ft
from flet.core.buttons import ButtonStyle
from flet.core.colors import Colors
from flet.core.text_style import TextStyle, TextDecoration

from manager import dbConnection as dbc
from manager import db as db
from manager.chatManager import ChatManager as cm
from manager.userManager import UserManager as um

#this class initializes handles for database operations, chat managment, and user sessions

class MyApp:
    def __init__(self, user_repo):
        self.user_repo = user_repo
        # self.chat_manager = cm()
        self.user_manager = um()
        self.chat_manager = cm(user_repo)

    def main(self, page: ft.Page):#window
        page.title = "Authorization and registration"
        page.window_max_width = 1600
        page.window_max_height = 1200
        page.window_resizable = False
        page.vertical_alignment = ft.MainAxisAlignment.CENTER

        def route_change(e):#clear all views before navigating to a new route.
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
                    print("Error: incorrect user_id in URL")
                    page.go("/")

            page.update()

        def login_page(page):#
            login_field = ft.TextField(label="Login", bgcolor="#D9D9D9", width=350, border_radius=10)
            password_field = ft.TextField(label="Password", bgcolor="#D9D9D9", width=350, password=True, border_radius=10)
            result_text = ft.Text()

            def handle_register(e):
                if login_field.value and password_field.value:
                    result = self.user_repo.create_user(login_field.value, password_field.value)
                    result_text.value = "Registration successful!" if result else "Registration error!"
                else:
                    result_text.value = "Please fill in all fields!"
                page.update()

            def handle_login(e):
                if login_field.value and password_field.value:
                    success, user_id = self.user_repo.authenticate_user(login_field.value, password_field.value)
                    if success:
                        self.user_manager.save_user_id(user_id)
                        page.go(f"/dashboard/{user_id}")
                    else:
                        result_text.value = "Eerror: Invalid login or password!"
                else:
                    result_text.value = "Error: Login and password fields cannot be empty!"
                page.update()

            return ft.View(
                "/",
                bgcolor="#9BCCBF",
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Stack([
                        ft.Image(src="assets/topleft.png"),
                        ft.Column([
                            ft.Text(
                                "Your guide to balance",
                                font_family="Inter",
                                size=40,
                                weight="bold",
                                color="#000000",
                                style=ft.TextStyle(
                                    shadow=ft.BoxShadow(spread_radius=2, blur_radius=8, color=ft.colors.BLACK26,
                                                        offset=ft.Offset(3, 3))
                                ),
                            ),
                            ft.Text(
                                "Equilibri.Ai",
                                font_family="Inter",
                                size=128,
                                weight="bold",
                                color="#000000",
                            ),
                            login_field,
                            password_field,
                            ft.Row([
                                ft.ElevatedButton("Login", on_click=handle_login),
                                ft.ElevatedButton("Register", on_click=handle_register),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            result_text,
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ])
                ],
            )

        def handle_logout(e):
            self.user_manager.clear_user_session()
            page.go("/")
            page.update()

        def dashboard_page(page, user_id):
            if not isinstance(user_id, int):
                print("Error: user_id must be a number")
                return ft.View("/", controls=[ft.Text("Error: incorrect user_id")])

            my_app = MyApp(self.user_repo)
            my_app.chat_manager.message_input.on_submit = my_app.chat_manager.send_message

            return ft.View(
                f"/dashboard/{user_id}",
                bgcolor="#5B7065",
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text("Equilibri.Ai", size=42, weight="bold", color="white"),
                                alignment=ft.alignment.center,
                                padding=ft.padding.only(top=5, left=20)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.MENU_BOOK,
                                icon_color="blue400",
                                icon_size=20,
                                tooltip="Open privacy & policy",
                                on_click=lambda _: webbrowser.open(
                                    "https://www.notion.so/EQUILIBRI-AI-PRIVACY-POLICY-AND-USER-AGREEMENT-1c00d7b1732e806ba92fc3942c784022"
                                ),
                            ),
                            ft.TextButton(
                                on_click=lambda _: webbrowser.open(
                                    "https://www.notion.so/EQUILIBRI-AI-PRIVACY-POLICY-AND-USER-AGREEMENT-1c00d7b1732e806ba92fc3942c784022"
                                ),
                            ),
                        ]
                    ),

                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Menu", size=20, weight="bold", color="white"),
                                        ft.Divider(),
                                        my_app.chat_manager.chat_buttons,
                                        ft.TextButton("New chat",
                                                      on_click=lambda e: my_app.chat_manager.create_new_chat(e)),
                                    ]
                                ),
                                bgcolor="#3A3A3A",
                                width=250,
                                height=700,
                                padding=10,
                                border_radius=10,
                            ),
                            ft.Container(
                                content=ft.Stack(
                                    controls=[
                                        ft.Container(
                                            content=ft.Column(
                                                controls=[
                                                    my_app.chat_manager.header,
                                                    ft.Container(
                                                        my_app.chat_manager.chat_display,
                                                        height=500,
                                                        expand=True,
                                                        padding=10
                                                    ),
                                                    ft.Row(
                                                        controls=[
                                                            ft.ElevatedButton(
                                                                text="Let's try different techniques",
                                                                style=ft.ButtonStyle(bgcolor="#1e1e1e", color="white"),
                                                                on_click=lambda e: my_app.chat_manager.send_bot_message(
                                                                    "1. Reassessment of thoughts\n2. Relaxation techniques",
                                                                    e
                                                                )
                                                            ),
                                                            ft.ElevatedButton(
                                                                text="Mood check",
                                                                style=ft.ButtonStyle(bgcolor="#1e1e1e", color="white"),
                                                                on_click=lambda e: my_app.chat_manager.send_bot_message(
                                                                    "How are you feeling right now?", e)
                                                            ),
                                                            ft.ElevatedButton(
                                                                text="Turn on the mode",
                                                                style=ft.ButtonStyle(bgcolor="#1e1e1e", color="white"),
                                                                on_click=lambda e: my_app.chat_manager.send_bot_message(
                                                                    "Focus mode activated 🧘", e)
                                                            ),
                                                        ],
                                                        alignment=ft.MainAxisAlignment.CENTER
                                                    ),

                                                    ft.Row(
                                                        controls=[
                                                            my_app.chat_manager.message_input,
                                                            ft.IconButton(
                                                                icon=ft.Icons.SEND,
                                                                icon_color=ft.Colors.BLACK,
                                                                bgcolor="#edeefa",
                                                                on_click=my_app.chat_manager.send_message
                                                            )
                                                        ],
                                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                    ),
                                                    ft.Row(
                                                        controls=[
                                                            ft.ElevatedButton(
                                                                text="Remove selected",
                                                                on_click=my_app.chat_manager.delete_selected_messages,
                                                            ),
                                                            ft.ElevatedButton(
                                                                text="Clear history",
                                                                on_click=my_app.chat_manager.clear_chat_history,
                                                            ),
                                                        ],
                                                        alignment=ft.MainAxisAlignment.END,
                                                    ),
                                                ]
                                            ),
                                            bgcolor="#2C2C2C",
                                            padding=10,
                                            border_radius=10,
                                            expand=True,
                                        ),
                                    ]
                                ),
                                expand=True,
                            ),
                        ],
                        expand=True
                    ),
                    ft.ElevatedButton("Exit",
                                      on_click=lambda e: (
                                          my_app.user_manager.clear_user_session(), page.go("/"), page.update())
                                      )
                ]
            )

        page.on_route_change = route_change
        page.go("/")

if __name__ == "__main__":
    db_instance = db.Database('localhost', 'postgres', '0000', 'postgres')
    connection = db_instance.connection()

    if connection:
        user_repo = dbc.UserRepository(db_connection=connection, user_id=None)
        app = MyApp(user_repo)
        ft.app(target=app.main)
    else:
        print("Failed to establish database connection!")
