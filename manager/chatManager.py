from datetime import date
from openai import OpenAI
import flet as ft
from manager import dbConnection as dbc
from manager import db as db

client = OpenAI(api_key="....A")

class ChatManager:
    def __init__(self, user_repo):
        self.user_repo = user_repo
        self.header = ft.Text("ChatBot", size=20, weight="bold", color="#9C9C9C")
        self.chat_display = ft.ListView(expand=True, height=500)
        self.message_input = ft.TextField(label="Enter your message", width=400, border_radius=10, color="#9C9C9C")
        self.chat_list = []
        self.chat_buttons = ft.ListView(expand=True, height=700)
        self.chat_history = {}
        self.chat_counter = 1
        self.selected_messages = set()
        self.load_user_chats()
        self.create_new_chat(None)
        self.active_technique = None #WE ADED THIS FUNCTION FOR AI RESPONSE

    def send_message(self, e, preset_text=None): #WE ADED SMART RESPONSES
        user_message = preset_text if preset_text else self.message_input.value.strip()
        if user_message:
            if self.current_chat not in self.chat_history:
                self.chat_history[self.current_chat] = [] 

            message_index = len(self.chat_history[self.current_chat])
            self.user_repo.save_message(self.current_chat, self.user_repo.user_id, user_message, is_bot=False)
            self.chat_history[self.current_chat].append((f"You: {user_message}", message_index, "user"))
            self.chat_display.controls.append(self.create_message_row(f"You: {user_message}", message_index))

            # Handle selection after 'Let's try different techniques'
            if self.active_technique == "pending":
                if user_message == "1":
                    self.active_technique = "reassessment"
                    bot_response = "Great! Let's try reassessing your thoughts. What negative thought are you currently having?"
                elif user_message == "2":
                    self.active_technique = "relaxation"
                    bot_response = "Excellent. Let's begin with a deep breath. Inhale... hold... and exhale slowly."
                else:
                    bot_response = "Please select 1 or 2 to proceed with the technique."
            else:
                # Default: generate response from OpenAI based on active mode
                bot_response = self.get_bot_response(user_message)

            self.user_repo.save_message(self.current_chat, None, bot_response, is_bot=True)
            self.chat_history[self.current_chat].append((f"Bot: {bot_response}", message_index + 1, "bot"))
            self.chat_display.controls.append(self.create_message_row(f"Bot: {bot_response}", message_index + 1))

            self.message_input.value = ""
            e.page.update()

    def send_bot_message(self, message, e=None): #ADED NEW FUNCTION
        if not message:
            return

        # Set modes based on message content
        if "Reassessment of thoughts" in message:
            self.active_technique = "pending"
        elif "Focus mode activated" in message:
            self.active_technique = "deep_mode"
        elif "How are you feeling right now?" in message:
            self.active_technique = "mood_check"

        message_index = len(self.chat_history[self.current_chat])
        self.chat_history[self.current_chat].append((f"Bot: {message}", message_index, "bot"))
        self.chat_display.controls.append(self.create_message_row(f"Bot: {message}", message_index))

        if e and hasattr(e, "page"):
            e.page.update()

    def get_bot_response(self, user_message): #NEW FUCTION
        system_prompt = "You are Equilibri.Ai — a helpful, friendly, and smart assistant."

        if self.active_technique == "reassessment":
            system_prompt += " Speak like a cognitive behavioral therapist helping the user challenge and reframe negative thoughts. Be practical and supportive."
        elif self.active_technique == "relaxation":
            system_prompt += " Speak softly and calmly. Guide the user through breathing exercises, mindfulness, or visual relaxation."
        elif self.active_technique == "deep_mode":
            system_prompt += " Ask thoughtful and empathetic questions to help the user explore their inner thoughts and feelings. Be deeply curious and kind."
        elif self.active_technique == "mood_check":
            system_prompt += (
                " Help the user identify their current emotions. Ask how they’re feeling physically and mentally. "
                "Guide them with gentle, open-ended questions to explore their emotional state."
            )

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] OpenAI API call failed: {e}")
            return "Oops! Something went wrong 🤖."

    def create_message_row(self, text, index): #FOR CHAT INTERFACE CONVINIENCE
        return ft.Row(
            controls=[
                ft.Checkbox(on_change=lambda e, idx=index: self.toggle_message_selection(idx, e)),
                ft.Container(
                    content=ft.Text(
                        text,
                        color="#9C9C9C",
                        selectable=True,  
                        no_wrap=False,  # text transfering
                    ),
                    padding=10,
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                    border_radius=8,
                    width=600,  
                ),
                ft.IconButton(ft.Icons.DELETE, on_click=lambda e, idx=index: self.delete_message(idx, e))
            ]
        )

    def toggle_message_selection(self, index, e):
        if e.control.value:
            self.selected_messages.add(index)
        else:
            self.selected_messages.discard(index)

    def delete_selected_messages(self, e=None):
        if self.current_chat in self.chat_history:
            self.chat_history[self.current_chat] = [
                (msg, idx, sender) for msg, idx, sender in self.chat_history[self.current_chat]
                if idx not in self.selected_messages
            ]
        self.selected_messages.clear()
        self.update_chat_display(e)

    def clear_chat_history(self, e=None):
        if self.current_chat in self.chat_history:
            self.chat_history[self.current_chat] = []
        self.update_chat_display(e)

    def delete_message(self, message_index, e):
        self.chat_history[self.current_chat] = [
            (msg, idx, sender) for msg, idx, sender in self.chat_history[self.current_chat]
            if idx != message_index
        ]
        self.update_chat_display(e)

    def update_chat_display(self, e=None):
        self.chat_display.controls.clear()
        self.chat_display.controls.extend([
            self.create_message_row(message, idx) for message, idx, sender in
            self.chat_history.get(self.current_chat, [])
        ])
        if e and hasattr(e, "page"):
            e.page.update()

    def switch_chat(self, chat_name, e=None):
        self.current_chat = chat_name
        self.update_chat_display(e)
        self.update_chat_buttons()
        if e and hasattr(e, "page"):
            e.page.update()

    def update_chat_buttons(self):
        self.chat_buttons.controls.clear()
        for chat in self.chat_list:
            is_active = chat == self.current_chat
            chat_button = ft.TextButton(
                chat,
                on_click=lambda e, cn=chat: self.switch_chat(cn, e),
                style=ft.ButtonStyle(
                    color={
                        ft.ControlState.DEFAULT: ft.Colors.BLACK,
                        ft.ControlState.HOVERED: ft.Colors.BLUE,
                    },
                    overlay_color=ft.Colors.TRANSPARENT,
                    side={
                        "": ft.BorderSide(2 if is_active else 0, ft.Colors.BLUE),
                    },
                ),
            )
            delete_button = ft.IconButton(
                ft.Icons.DELETE,
                on_click=lambda e, cn=chat: self.delete_chat(cn, e)
            )
            self.chat_buttons.controls.append(ft.Row(controls=[chat_button, delete_button]))

        if hasattr(self, "page"):
            self.page.update()

    def load_user_chats(self):
        chat_ids = self.user_repo.get_chats_by_user()
        for chat_id in chat_ids:
            chat_name = f"Chat {chat_id}"
            self.chat_list.append(chat_name)
            self.load_messages_for_chat(chat_id)
            self.chat_buttons.controls.append(ft.Row(
                controls=[
                    ft.TextButton(chat_name, on_click=lambda e, cn=chat_name: self.switch_chat(cn, e)),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, cn=chat_name: self.delete_chat(cn, e))
                ]
            ))
        if self.chat_list:
            self.switch_chat(self.chat_list[0])

    def create_new_chat(self, e=None):
        new_chat_name = f"Chat {self.chat_counter}"
        self.chat_list.append(new_chat_name)
        chat_date = date.today()
        result = self.user_repo.create_chat(chat_date)
        print("Created successful!" if result else "Creating error!")
        self.chat_history[new_chat_name] = []
        self.chat_buttons.controls.append(ft.Row(
            controls=[
                ft.TextButton(new_chat_name, on_click=lambda e: self.switch_chat(new_chat_name, e)),
                ft.IconButton(ft.Icons.DELETE, on_click=lambda e: self.delete_chat(new_chat_name, e))
            ]
        ))
        self.switch_chat(new_chat_name, e)
        self.chat_counter += 1
        if e and hasattr(e, "page"):
            e.page.update()

    def open_chat(self, chat_id):
        self.current_chat = chat_id
        messages = self.load_chat_messages(chat_id)
        self.chat_display.controls.clear()
        for message in messages:
            msg_id, user_id, text, timestamp = message
            self.chat_display.controls.append(ft.Text(f"{user_id}: {text} ({timestamp})"))
        self.chat_display.update()

    def load_messages_for_chat(self, chat_id):
        messages = self.user_repo.get_messages_by_chat(chat_id)
        chat_name = f"Chat {chat_id}"
        self.chat_history[chat_name] = [
            (f"{'You' if msg[0] == self.user_repo.user_id else 'Bot'}: {msg[1]}", idx,
             "user" if msg[0] == self.user_repo.user_id else "bot")
            for idx, msg in enumerate(messages)
        ]

    def delete_chat_from_db(self, chat_name):
        try:
            self.user_repo.delete_chat(chat_name)
        except Exception as e:
            print(f"Error deleting chat from DB: {e}")

    def delete_chat(self, chat_name, e):
        self.delete_chat_from_db(chat_name)
        if chat_name in self.chat_history:
            del self.chat_history[chat_name]
        if chat_name in self.chat_list:
            self.chat_list.remove(chat_name)
        if not self.chat_list:
            self.chat_counter = 1
        self.chat_buttons.controls.clear()
        for chat in self.chat_list:
            chat_button = ft.Row(
                controls=[
                    ft.TextButton(chat, on_click=lambda e, cn=chat: self.switch_chat(cn, e)),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, cn=chat: self.delete_chat(cn, e))
                ]
            )
            self.chat_buttons.controls.append(chat_button)
        if self.current_chat == chat_name:
            self.current_chat = self.chat_list[0] if self.chat_list else None
            self.switch_chat(self.current_chat, e)
        e.page.update()
