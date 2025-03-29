from datetime import date

import flet as ft
from flet.core import page
from manager import dbConnection as dbc
from manager import db as db


#this class is responsible for chat and for everything what we can do in chat

class ChatManager:
    def __init__(self, user_repo):
        #user interface elements are created and initialized
        # self.dbc = dbc
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

        self.responses =  {
        "hi": "Hi! How are you feeling today??",
        "how are you?": "I am here for supporting you. What about you?",
        "what do you feel?": "I can only imagine it what do you feel. How can you explain your emotional state?",
        "i am sad": "That is a pity, that you feel sad. Remember, that you always can find light side.",
        "i am scared": "I understand. Scare can be too much strong. You are not lonely. We can speak about it.",
        "i am tired": "It is very important to give yourself time to rest. How do you usually relax??",
        "i am not confident in myself": "You deserve love and respect. Step by step and ypu will feel better.",
        "what do you know about self care": "Self-care is important. How do you take care of yourself?",
        "bye": "Goodbye! Remember that you are important. Take care of yourself.",
        "what is anxiety?": "An emotional state characterized by feelings of anxiety, tension and fear.",
        "why do teenagers get anxious?": "Due to a lot of changes, yes, influences from school, social relationships and the expectations of others.",
        "how does anxiety affect?": "Emotionally causes anxiety and fear, physically manifests itself as tension, rapid breathing or headache.",
        "what causes anxiety?": "Study load, conflicts in social relationships, high demands from adults.",
        "how does anxiety manifest itself??": "Emotional: anxiety, fear. Physical: muscle tension, rapid breathing, problems concentrating.",
        "what helps you cope?": "Relaxation, self-regulation skills, breathing exercises, visualization and mindfulness.",
        "what exercises are useful?": "Breathing exercises, calming visualization, mindfulness practice.",
        "why relaxation is important?": "It helps reduce stress, control emotions and support overall well-being.",
        "how does self-regulation help?": "It allows you to control your emotions and consciously reduce stress levels..",
        "how often to practice relaxation?": "Regularly, preferably daily, to strengthen anxiety management skills.",
        "what are breathing exercises?": "A deep breathing method that involves inhaling slowly, holding your breath, and exhaling smoothly.",
        "how to do breathing exercises?": "Sit comfortably, inhale through your nose, hold your breath for a few seconds, exhale slowly through your mouth.",
        "why breathing helps?": "It slows your heart rate, relaxes your muscles, and reduces your stress levels.",
        "what is visualization?": "A practice in which you imagine yourself in a calm and safe environment.",
        "how to choose a place for visualization?": "Imagine a place where you feel comfortable and safe, such as nature or your favorite room.",
        "what to represent in visualization?": "Colors, sounds, smells, sensations to create a vivid and realistic image.",
        "how often to visualize?": "Regularly, especially in times of extreme anxiety or before important events.",
        "what is mindfulness?": "The ability to focus on the current moment, sensations and the world around you.",
        "how mindfulness helps?": "It shifts attention from negative thoughts to the present, reducing anxiety levels.",
        "what develops awareness?": "Focus on breathing, bodily sensations, sounds and textures around.",
        "what to focus on?": "On sounds, smells, physical sensations or details of the surrounding space.",
        "how does anxiety affect development??": "It can disrupt emotional balance, concentration, and interfere with personal growth.",
        "why is the body-mind connection important??": "It helps reduce stress and achieve inner balance..",
        "why relaxation techniques?": "Improves control over emotions, reduces stress and strengthens self-confidence.",
        "how does a positive attitude help??": "It promotes resistance to stress and helps you recover faster from difficulties."
        }

        self.create_new_chat(None)

    def send_message(self, e):
        user_message = self.message_input.value.strip()
        if user_message:
            if self.current_chat not in self.chat_history:
                self.chat_history[self.current_chat] = []

            message_index = len(self.chat_history[self.current_chat])

            # Сохраняем сообщение пользователя в базу
            self.user_repo.save_message(self.current_chat, self.user_repo.user_id, user_message, is_bot=False)

            self.chat_history[self.current_chat].append((f"You: {user_message}", message_index, "user"))
            self.chat_display.controls.append(self.create_message_row(f"You: {user_message}", message_index))

            bot_response = self.get_bot_response(user_message)

            # Сохраняем сообщение бота в базу
            self.user_repo.save_message(self.current_chat, None, bot_response, is_bot=True)

            self.chat_history[self.current_chat].append((f"Bot: {bot_response}", message_index + 1, "bot"))
            self.chat_display.controls.append(self.create_message_row(f"Bot: {bot_response}", message_index + 1))

            self.message_input.value = ""
            e.page.update()

    def create_message_row(self, text, index):#creates a row for a single message to display in the chat

        return ft.Row(
            controls=[
                ft.Checkbox(on_change=lambda e, idx=index: self.toggle_message_selection(idx, e)),
                ft.Text(text, color="#9C9C9C"),
                ft.IconButton(ft.Icons.DELETE, on_click=lambda e, idx=index: self.delete_message(idx, e))
            ]
        )

    def toggle_message_selection(self, index, e):#toggles the selection state of a message (add/remove from selected messages)

        if e.control.value:
            self.selected_messages.add(index)
        else:
            self.selected_messages.discard(index)

    def delete_selected_messages(self, e=None):#deletes all selected messages

        if self.current_chat in self.chat_history:
            self.chat_history[self.current_chat] = [
                (msg, idx, sender) for msg, idx, sender in self.chat_history[self.current_chat]
                if idx not in self.selected_messages
            ]
        self.selected_messages.clear()
        self.update_chat_display(e)

    def clear_chat_history(self, e=None):#clears the entire chat history of the current chat
        if self.current_chat in self.chat_history:
            self.chat_history[self.current_chat] = []
        self.update_chat_display(e)

    def delete_message(self, message_index, e): #deletes a single message by its index from the current chat
        self.chat_history[self.current_chat] = [
            (msg, idx, sender) for msg, idx, sender in self.chat_history[self.current_chat]
            if idx != message_index
        ]
        self.update_chat_display(e)

    def update_chat_display(self, e=None):#pdates the chat display to reflect the current chat's history
        self.chat_display.controls.clear()
        self.chat_display.controls.extend([
            self.create_message_row(message, idx) for message, idx, sender in
            self.chat_history.get(self.current_chat, [])
        ])
        if e and hasattr(e, "page"):
            e.page.update()

    def get_bot_response(self, user_message):#retrieves a bot response based on user input, or returns a default response
        return self.responses.get(user_message.lower(), "Sorry, I don't understand this request.")

    def switch_chat(self, chat_name, e=None):
        """Switching chat with visual highlighting."""
        self.current_chat = chat_name
        self.update_chat_display(e)
        self.update_chat_buttons()

        if e and hasattr(e, "page"):
            e.page.update()

    def update_chat_buttons(self):
        """Refreshes the list of chat buttons with the active chat highlighted (underlined))."""
        self.chat_buttons.controls.clear()

        for chat in self.chat_list:
            is_active = chat == self.current_chat  # Checking if the chat is current

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
                        "": ft.BorderSide(2 if is_active else 0, ft.Colors.BLUE),  # Highlight active chat
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
            self.load_messages_for_chat(chat_id)  # Load messages

            # Add a chat button with a new transfer chat_name to lambda
            self.chat_buttons.controls.append(ft.Row(
                controls=[
                    ft.TextButton(chat_name, on_click=lambda e, cn=chat_name: self.switch_chat(cn, e)),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, cn=chat_name: self.delete_chat(cn, e))
                ]
            ))
        if self.chat_list:
            self.switch_chat(self.chat_list[0])  # Open first chat

    def create_new_chat(self, e=None):#creates a new chat and switches to it
        new_chat_name = f"Chat {self.chat_counter}"
        self.chat_list.append(new_chat_name)
        chat_date = date.today()
        result = self.user_repo.create_chat(chat_date)
        print("Created successful!" if result else "Creating error!")
        # else:
        #    print("Didnt save chat ")
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

        # Обновляем UI чата
        self.chat_display.controls.clear()
        for message in messages:
            msg_id, user_id, text, timestamp = message
            self.chat_display.controls.append(ft.Text(f"{user_id}: {text} ({timestamp})"))

        self.chat_display.update()

    def load_messages_for_chat(self, chat_id):
        """loads messages for a given chat from the database."""
        messages = self.user_repo.get_messages_by_chat(chat_id)
        chat_name = f"Chat {chat_id}"
        self.chat_history[chat_name] = [
            (f"{'You' if msg[0] == self.user_repo.user_id else 'Bot'}: {msg[1]}", idx,
             "user" if msg[0] == self.user_repo.user_id else "bot")
            for idx, msg in enumerate(messages)
        ]


    def delete_chat_from_db(self, chat_name):
        """Delete a chat by its name."""
        chat_id = int(chat_name.split()[-1])  # Take chat_id from "Chat 1"
        result = self.user_repo.delete_chat(chat_id)  # Call the delete method
        print(f"Chat {chat_id} deleted from DB" if result else f"Error deleting chat {chat_id}")


    def delete_chat(self, chat_name, e):
        """Delete a chat from list and db."""
        self.delete_chat_from_db(chat_name)  # Delete from db

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
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, cn=chat: self.delete_chat(cn, e))  # Call method
                ]
            )
            self.chat_buttons.controls.append(chat_button)

        if self.current_chat == chat_name:
            self.current_chat = self.chat_list[0] if self.chat_list else None
            self.switch_chat(self.current_chat, e)

        e.page.update()

    def load_messages_for_chat(self, chat_id):
        pass
