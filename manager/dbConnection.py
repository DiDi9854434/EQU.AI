import psycopg2
import hashlib

class UserRepository:
    def __init__(self, db_connection, user_id = None):
        self.db_connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="0000"
        )
        self.user_id = user_id

    def delete_chat(self, chat_id):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM chats WHERE id_chat = %s", (chat_id,))
                if not cursor.fetchone():  # If chat not founded
                    print(f"Chat {chat_id} does not exist.")
                    return

                cursor.execute("DELETE FROM chats WHERE id_chat = %s", (chat_id,))
                self.db_connection.commit()
            print(f"Chat {chat_id} deleted successfully.")
        except Exception as e:
            self.db_connection.rollback()
            print(f"Error deleting chat {chat_id}: {e}")

    def get_chats_by_user(self):
        try:
            # Read user_id from file
            with open("user_session.txt", "r") as file:
                user_id = file.read().strip()  # Get user_id

            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id_chat FROM chats WHERE user_id = %s;", (user_id,))
                chats = cursor.fetchall()
                return [chat[0] for chat in chats]  # Return list id chats

        except Exception as e:
            print(f"Error loading chats: {e}")
            return []


    def save_message(self, chat_id, user_id, text, is_bot):
        conn = self.db_connection
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO messages (user_id, chat_id, message_text, ms_date, ischat) VALUES (%s, %s, %s, NOW(), %s)",
                        (user_id, chat_id, text, is_bot)
                    )
                    conn.commit()
            except Exception as e:
                print(f"Error saving message: {e}")
            finally:
                conn.close()

    def create_chat(self, chat_date):
        try:
            # Check: if connection was closed, reconnection
            if self.db_connection.closed:
                print("[INFO] Connection closed. Reconnecting...")
                self.reconnect()

            with self.db_connection.cursor() as cursor:
                chat_name = f"Chat {chat_date}"
                cursor.execute(
                    "INSERT INTO chats (name, date_created) VALUES (%s, %s) RETURNING id_chat",
                    (chat_name, chat_date)
                )
                chat_id = cursor.fetchone()[0]
                self.db_connection.commit()
                return chat_id
        except Exception as e:
            print(f"[ERROR] Failed to create chat: {e}")
            if self.db_connection and not self.db_connection.closed:
                self.db_connection.rollback()
            return None


        except Exception as e:
            print(f"Error creating chat: {e}")
            self.db_connection.rollback()
            return False

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username, password):

        try:
            hashed_password = self.hash_password(password)
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT user_id FROM users WHERE user_login = %s;", (username,))
                if cursor.fetchone():
                    print("❌ Error: Login already exists!")
                    return False
                cursor.execute(
                    "INSERT INTO users (user_login, user_password) VALUES (%s, %s) RETURNING user_id;",
                    (username, hashed_password)
                )
                user_id = cursor.fetchone()[0]
                print(f"user with id{user_id} created successfully!")
                self.db_connection.commit()
                return True
        except Exception as e:
            print(f"Error creating user: {e}")
            self.db_connection.rollback()
            return False



    def authenticate_user(self, username, password):
        try:
            with self.db_connection.cursor() as cursor:

                cursor.execute("SELECT user_id, user_password FROM users WHERE user_login = %s;", (username,))
                result = cursor.fetchone()

                if not result:
                    print("❌ User not found.")
                    return False, None

                user_id, stored_password = result

                hashed_password = self.hash_password(password)
                if hashed_password == stored_password:
                    print(f"✅ Authorization successful! User ID: {user_id}")
                    return True, user_id

                print("❌ Invalid password.")
                return False, None

        except Exception as e:
            print(f"Authorization error: {e}")
            return False, None
