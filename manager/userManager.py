import os


class UserManager:
    def __init__(self, login=None, password=None, user_id=None):
        self.login = login  # User login
        self.password = password  # User password
        self.user_id = user_id  # User ID

    @staticmethod
    def save_user_id(user_id):
        """Save the user_id to a file called 'user_session.txt'."""
        with open("user_session.txt", "w") as file:
            file.write(str(user_id))

    @staticmethod
    def load_user_id():
        """Load the user_id from the 'user_session.txt' file, if it exists."""
        if os.path.exists("user_session.txt"):
            with open("user_session.txt", "r") as file:
                data = file.read().strip()
                if data.isdigit():
                    return int(data)  # Return the user_id as an integer
                else:
                    print(f"Error: File content is invalid - '{data}'")
                    return None
        return None  # Return None if the session file doesn't exist

    @staticmethod
    def clear_user_session():
        """Clear the user session by deleting the 'user_session.txt' file if it exists."""
        if os.path.exists("user_session.txt"):
            os.remove("user_session.txt")
