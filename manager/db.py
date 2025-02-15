import psycopg2


class Database:
    def __init__(self, host, user, password, dbName):
        self.host = host  # Host address where the database is hosted (e.g., localhost or IP address)
        self.user = user  # Username for connecting to the database
        self.password = password  # Password for the provided username
        self.dbName = dbName  # Name of the database to connect to

    def connection(self):
        try:
            conn = psycopg2.connect(  # Attempt to connect to the database using the provided credentials
                dbname=self.dbName,
                user=self.user,
                password=self.password,
                host=self.host
            )
            print('Connection established')  # Print success message if connection is successful
            return conn  # Return the connection object for further usage
        except:
            print('Can`t establish connection to database')  # Print an error message if the connection attempt fails
