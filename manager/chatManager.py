import flet as ft


class ChatManager:
    def __init__(self):
        # Header text for the chatbot
        self.header = ft.Text("ChatBot", size=20, weight="bold", color="#9C9C9C")

        # Main chat display area (ListView where messages are displayed)
        self.chat_display = ft.ListView(expand=True, height=500)

        # Input field for typing messages
        self.message_input = ft.TextField(label="Enter your message", width=400, border_radius=10, color="#9C9C9C")

        # List of created chat rooms
        self.chat_list = []

        # ListView that holds the buttons for switching or deleting chats
        self.chat_buttons = ft.ListView(expand=True, height=700)

        # Dictionary to store chat histories per chat
        self.chat_history = {}

        # Counter to keep track of the number of chats created
        self.chat_counter = 1

        # Set to store indices of selected chat messages (used for batch operations)
        self.selected_messages = set()

        # Predefined responses for the chatbot
        self.responses = {
            "hi": "Hi! How are you feeling today?",
            "how are you?": "I am here to support you. What about you?",
            "what do you feel?": "I can only imagine it, what do you feel? How can you explain your emotional state?",
            "i am sad": "It’s unfortunate that you feel sad. Remember, you can always find the bright side.",
            "i am scared": "I understand. Fear can be overwhelming. You are not alone. Let’s talk about it.",
            "i am tired": "It is very important to give yourself time to rest. How do you usually relax?",
            "i am not confident in myself": "You deserve love and respect. Step by step, you will feel better.",
            "what do you know about self care": "Self-care is important. How do you take care of yourself?",
            "bye": "Goodbye! Remember that you are important. Take care of yourself.",
            "what is anxiety?": "An emotional state characterized by feelings of unease, tension, and fear.",
            "why do teenagers get anxious?": "Due to many changes, influences from school, social relationships, and expectations from others.",
            "how does anxiety affect?": "Emotionally, it causes anxiety and fear. Physically, it manifests as tension, rapid breathing, or headaches.",
            "what causes anxiety?": "High study loads, conflicts in social relationships, and high expectations from adults.",
            "how does anxiety manifest?": "Emotionally: anxiety, fear. Physically: muscle tension, rapid breathing, and trouble concentrating.",
            "what helps to cope?": "Relaxation, self-regulation skills, breathing exercises, visualization, and mindfulness.",
            "what exercises are useful?": "Breathing exercises, calming visualization, mindfulness practice.",
            "why is relaxation important?": "It helps reduce stress, regulate emotions, and support overall well-being.",
            "how does self-regulation help?": "It allows you to control your emotions and consciously reduce stress levels.",
            "how often should you practice relaxation?": "Regularly, preferably daily, to strengthen your stress management skills.",
            "what are breathing exercises?": "A deep-breathing method that involves inhaling slowly, holding your breath, and exhaling smoothly.",
            "how to perform breathing exercises?": "Sit comfortably, inhale through your nose, hold your breath for a few seconds, exhale slowly through your mouth.",
            "why does breathing help?": "It slows your heart rate, relaxes your muscles, and reduces your stress levels.",
            "what is visualization?": "A practice where you imagine yourself in a calm and safe environment.",
            "how to choose a place for visualization?": "Imagine a place where you feel comfortable and safe, such as nature or your favorite room.",
            "what to imagine during visualization?": "Colors, sounds, smells, sensations to create vivid and realistic images.",
            "how often to do visualization?": "Regularly, especially during moments of high anxiety or before significant events.",
            "what is mindfulness?": "The ability to focus on the current moment, your sensations, and the surrounding world.",
            "how does mindfulness help?": "It shifts your attention from negative thoughts to the present, reducing anxiety levels.",
            "what develops mindfulness?": "Focusing on breathing, bodily sensations, sounds, and the textures around you.",
            "what to focus on?": "Sounds, smells, physical sensations, or details of your environment.",
            "how does anxiety affect development?": "It can disrupt emotional balance, concentration, and hinder personal growth.",
            "why is the mind-body connection important?": "It helps reduce stress and achieve inner balance.",
            "why practice relaxation techniques?": "They improve emotional control, reduce stress, and build self-confidence.",
            "how does a positive attitude help?": "It builds resilience to stress and helps recover more quickly from challenges."
        }

        # Automatically create the first chat when the app starts
        self.create_new_chat(None)

    def send_message(self, e):
        """Send a user message, append it to chat, and get a chatbot response."""
        user_message = self.message_input.value.strip()  # Get user's input
        if user_message:
            # Determine the current message index
            message_index = len(self.chat_history[self.current_chat])

            # Append the user message to the chat history
            self.chat_history[self.current_chat].append((f"You: {user_message}", message_index, "user"))
            self.chat_display.controls.append(self.create_message_row(f"You: {user_message}", message_index))

            # Fetch and append the chatbot's response to the chat history
            bot_response = self.get_bot_response(user_message)
            self.chat_history[self.current_chat].append((f"Bot: {bot_response}", message_index + 1, "bot"))
            self.chat_display.controls.append(self.create_message_row(f"Bot: {bot_response}", message_index + 1))

            # Clear the message input field
            self.message_input.value = ""
            e.page.update()  # Update the app UI

    def create_message_row(self, text, index):
        """Create a row (message block) for displaying a message with actions (select, delete)."""
        return ft.Row(
            controls=[
                ft.Checkbox(on_change=lambda e, idx=index: self.toggle_message_selection(idx, e)),
                # Checkbox for selecting a message
                ft.Text(text, color="#9C9C9C"),  # Message text
                ft.IconButton(ft.Icons.DELETE, on_click=lambda e, idx=index: self.delete_message(idx, e))
                # Delete button
            ]
        )

    def toggle_message_selection(self, index, e):
        """Toggle the selection of a message by its index."""
        if e.control.value:
            self.selected_messages.add(index)
        else:
            self.selected_messages.discard(index)

    def delete_selected_messages(self, e):
        """Delete all selected messages and refresh the chat display."""
        self.chat_history[self.current_chat] = [
            (msg, idx, sender) for msg, idx, sender in self.chat_history[self.current_chat]
            if idx not in self.selected_messages
        ]
        self.selected_messages.clear()  # Clear selected messages after deletion
        self.update_chat_display(e)  # Refresh the messages

    def delete_message(self, message_index, e):
        """Delete a specific message by its index."""
        self.chat_history[self.current_chat] = [
            (msg, idx, sender) for msg, idx, sender in self.chat_history[self.current_chat]
            if idx != message_index
        ]
        self.update_chat_display(e)

    def update_chat_display(self, e=None):
        """Update the chat display to show the current chat's messages."""
        self.chat_display.controls.clear()  # Remove all current messages
        # Add back messages from the history
        self.chat_display.controls.extend([
            self.create_message_row(message, idx) for message, idx, sender in
            self.chat_history.get(self.current_chat, [])
        ])
        if e and hasattr(e, "page"):  # Ensure event has a page attribute
            e.page.update()

    def get_bot_response(self, user_message):
        """Fetch a chatbot response based on the user's input message."""
        return self.responses.get(user_message.lower(), "Sorry, I don’t understand this request.")

    def switch_chat(self, chat_name, e=None):
        """Switch to a selected chat by its name."""
        self.current_chat = chat_name
        self.update_chat_display(e)
        if e and hasattr(e, "page"):  # Ensure the event exists
            e.page.update()

    def create_new_chat(self, e=None):
        """Create a new chat room and make it the active chat."""
        new_chat_name = f"Chat {self.chat_counter}"
        self.chat_list.append(new_chat_name)  # Add the new chat to the list
        self.chat_history[new_chat_name] = []  # Initialize its message history

        # Add buttons for the new chat
        self.chat_buttons.controls.append(ft.Row(
            controls=[
                ft.TextButton(new_chat_name, on_click=lambda e: self.switch_chat(new_chat_name, e)),  # Button to switch
                ft.IconButton(ft.Icons.DELETE, on_click=lambda e: self.delete_chat(new_chat_name, e))
                # Button to delete
            ]
        ))

        self.switch_chat(new_chat_name, e)  # Switch to the new chat
        self.chat_counter += 1  # Increment chat counter
        if e and hasattr(e, "page"):  # Update app UI
            e.page.update()

    def clear_chat(self, e):
        """Clear all messages in the current chat."""
        self.chat_display.controls.clear()  # Clear visible messages
        self.chat_display.update()

    def delete_chat(self, chat_name, e):
        """Delete a chat by its name and refresh the chat buttons."""
        if chat_name in self.chat_history:
            del self.chat_history[chat_name]
        if chat_name in self.chat_list:
            self.chat_list.remove(chat_name)

        if not self.chat_list:  # If all chats are deleted, reset counter
            self.chat_counter = 1

        # Refresh chat buttons
        self.chat_buttons.controls.clear()
        for chat in self.chat_list:
            chat_button = ft.Row(
                controls=[
                    ft.TextButton(chat, on_click=lambda e, chat_name=chat: self.switch_chat(chat_name, e)),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, chat_name=chat: self.delete_chat(chat_name, e))
                ]
            )
            self.chat_buttons.controls.append(chat_button)

        # Switch to another chat or clear the display if none exist
        if self.current_chat == chat_name:
            self.current_chat = self.chat_list[0] if self.chat_list else None
            self.switch_chat(self.current_chat, e)

        e.page.update()  # Update the app display
