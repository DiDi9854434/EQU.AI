import psycopg2
import hashlib


class UserRepository:
    def __init__(self, db_connection):
        # Establishing a connection to the PostgreSQL database
        self.db_connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="0000"
        )
        # self.db_connection.autocommit = True  # Uncomment to enable autocommit for transactions

    def hash_password(self, password):
        # Hash the plain-text password using SHA256 and return the hashed value
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username, password):
        try:
            hashed_password = self.hash_password(password)  # Hash the user's password
            with self.db_connection.cursor() as cursor:
                # Check if the username already exists in the database
                cursor.execute("SELECT user_id FROM users WHERE user_login = %s;", (username,))
                if cursor.fetchone():
                    print("❌ Error: The username already exists!")
                    return False
                # Insert the new user with their hashed password into the database
                cursor.execute(
                    "INSERT INTO users (user_login, user_password) VALUES (%s, %s) RETURNING user_id;",
                    (username, hashed_password)
                )
                user_id = cursor.fetchone()[0]
                print(f"User with ID {user_id} created successfully!")
                self.db_connection.commit()  # Commit the transaction
                return True
        except Exception as e:
            print(f"Error while creating user: {e}")
            self.db_connection.rollback()  # Rollback the transaction in case of an error
            return False

    def authenticate_user(self, username, password):
        try:
            with self.db_connection.cursor() as cursor:
                # Check if a user with the given username exists
                cursor.execute("SELECT user_id, user_password FROM users WHERE user_login = %s;", (username,))
                result = cursor.fetchone()

                if not result:
                    print("❌ User not found.")
                    return False, None

                user_id, stored_password = result  # Retrieve user ID and stored hashed password

                hashed_password = self.hash_password(password)  # Hash the provided password
                if hashed_password == stored_password:  # Compare hashed passwords
                    print(f"✅ Authentication successful! User ID: {user_id}")
                    return True, user_id

                print("❌ Incorrect password.")
                return False, None

        except Exception as e:
            print(f"Error during authentication: {e}")
            return False, None
