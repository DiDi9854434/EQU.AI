import os
import flet as ft
from manager import dbConnection as dbc
from manager import db as db
from manager.chatManager import ChatManager as cm
from manager.userManager import UserManager as um


class MyApp:
    def __init__(self, user_repo):
        self.user_repo = user_repo
        self.chat_manager = cm()
        self.user_manager = um()

    def main(self, page: ft.Page):
        page.title = "Authorization and Registration"  # Title for the application window
        page.window_max_width = 1600
        page.window_max_height = 1200
        page.window_resizable = False
        page.vertical_alignment = ft.MainAxisAlignment.CENTER  # Align page in the center

        def route_change(e):
            """Handles navigation between routes."""
            page.views.clear()

            if page.route == "/":
                user_id = self.user_manager.load_user_id()
                if user_id:
                    page.views.append(dashboard_page(page, user_id))  # Go to the dashboard if user is logged in
                else:
                    page.views.append(login_page(page))  # Show login page otherwise
            elif page.route.startswith("/dashboard/"):
                try:
                    user_id = int(page.route.split("/")[-1])  # Extract user_id from route
                    page.views.append(dashboard_page(page, user_id))
                except ValueError:
                    print("Error: invalid user_id in URL")
                    page.go("/")  # Redirect to root route in case of an error

            page.update()

        def login_page(page):
            """The login and registration page."""
            login_field = ft.TextField(
                label="Login", bgcolor="#D9D9D9", width=350, border_radius=10
            )
            password_field = ft.TextField(
                label="Password", bgcolor="#D9D9D9", width=350, password=True, border_radius=10
            )
            result_text = ft.Text()  # Text area for displaying login/registration results

            def handle_register(e):
                """Handles registration."""
                if login_field.value and password_field.value:
                    result = self.user_repo.create_user(
                        login_field.value, password_field.value
                    )
                    result_text.value = "Registration successful!" if result else "Registration failed!"
                else:
                    result_text.value = "Please fill in all the fields!"
                page.update()

            def handle_login(e):
                """Handles login."""
                if login_field.value and password_field.value:
                    success, user_id = self.user_repo.authenticate_user(
                        login_field.value, password_field.value
                    )
                    if success:
                        self.user_manager.save_user_id(user_id)  # Save user ID for session
                        page.go(f"/dashboard/{user_id}")  # Go to the dashboard route
                    else:
                        result_text.value = "Error: Incorrect login or password!"
                else:
                    result_text.value = "Error: Login and password fields cannot be empty!"
                page.update()

            return ft.View(
                "/",  # Root route
                bgcolor="#9BCCBF",  # Background light green
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Stack([
                        ft.Image(src="assets/topleft.png"),  # Top left image
                        ft.Column([
                            ft.Text(
                                "Your guide to balance",
                                font_family="Inter",
                                size=40,
                                weight="bold",
                                color="#000000",
                                style=ft.TextStyle(
                                    shadow=ft.BoxShadow(
                                        spread_radius=2, blur_radius=8, color=ft.Colors.BLACK26,  # Fixed warning
                                        offset=ft.Offset(3, 3)
                                    )
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
            """Clears the user session and logs out."""
            self.user_manager.clear_user_session()
            page.go("/")
            page.update()

      def dashboard_page(page, user_id):
    """The dashboard page."""

    if not isinstance(user_id, int):  # Check that user-id is an integer
        print("Error: user_id must be an integer")
        return ft.View("/", controls=[ft.Text("Error: invalid user_id")])  # Display an error message if the user-id is invalid

    # Create an application instance with a connection to the user repository
    my_app = MyApp(self.user_repo)
    # Bind the message sending handler
    my_app.chat_manager.message_input.on_submit = my_app.chat_manager.send_message

    # Creating Quick Reply Buttons
    quick_buttons = ft.Row(
        [
            ft.ElevatedButton("Remind me about the consultation",
                              on_click=lambda e: my_app.chat_manager.send_message(e, "Reminded me about the consultation")),
            ft.ElevatedButton("Postponement of consultation",
                              on_click=lambda e: my_app.chat_manager.send_message(e, "Postponement of consultation")),
            ft.ElevatedButton("Cancellation of consultation",
                              on_click=lambda e: my_app.chat_manager.send_message(e, "Cancellation of consultation")),
        ],
        alignment=ft.MainAxisAlignment.CENTER  # Align buttons to the center
    )

    return ft.View(
        f"/dashboard/{user_id}",
        bgcolor="#5B7065",
        controls=[
            ft.Container(
                content=ft.Text("Equilibri.Ai", size=42, weight="bold", color="white"),
                alignment=ft.alignment.top_center,  # Page title centered at top
                padding=ft.padding.only(top=5, left=20)
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Menu", size=20, weight="bold", color="white"),
                                ft.Divider(),  # dividing line
                                my_app.chat_manager.chat_buttons,  # Chat buttons
                                ft.TextButton("New Chat", on_click=lambda e: my_app.chat_manager.create_new_chat(e)),
                            ]
                        ),
                        bgcolor="#3A3A3A",
                        width=250, height=700, padding=10, border_radius=10
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                my_app.chat_manager.header,  # Chat Title
                                ft.Container(
                                    my_app.chat_manager.chat_display,
                                    height=400, expand=True, padding=10
                                ),
                                ft.Row(
                                    [
                                        my_app.chat_manager.message_input,  # Message input field
                                        ft.IconButton(
                                            icon=ft.Icons.SEND,  # Send icon
                                            icon_color=ft.Colors.BLACK,
                                            bgcolor="#edeefa",
                                            on_click=my_app.chat_manager.send_message
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN  # Alignment to the edges
                                ),
                                quick_buttons,  # Adding quick reply buttons
                            ]
                        ),
                        bgcolor="#2C2C2C", padding=10, border_radius=10, expand=True,
                    ),
                ],
                expand=True,
            ),
            ft.ElevatedButton("Log Out",  # Exit button
                              on_click=lambda e: self.user_manager.clear_user_session() or page.go("/")),
        ]
    )

# Route change handler
page.on_route_change = route_change
# Go to main page
page.go("/")

