import psycopg2
#this class is responsible for Database

class Database:

    def __init__(self, host, user, password, dbName):
        self.host = host
        self.user = user
        self.password = password
        self.dbName = dbName

    def connection(self):
        try:
            conn = psycopg2.connect(dbname=self.dbName, user=self.user, password=self.password, host=self.host)
            print('Connection established')
            return conn
        except:
            print('Can`t establish connection to database')
