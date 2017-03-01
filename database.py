import sqlite3
import sys

class database:
    def __init__(self, sqlite_path):
        #Connect to database
        try:
            self.conn = sqlite3.connect(sqlite_path)
            self.c = self.conn.cursor()
            self.c.execute('CREATE TABLE IF NOT EXISTS users (carduid TEXT, username TEXT)')
        except sqlite3.Error as e:
            print("Error %s:" % e.args[0])
            sys.exit(1)

    def get_user(self, uid):
        self.c.execute('SELECT * FROM users WHERE carduid=?', uid)
        return self.c.fetchone()

    def save_user(self, username, uid):
        #Save user to database
        self.c.execute('INSERT INTO users VALUES (?,?)', (uid, username))
        self.conn.commit()

    def close(self):
        self.conn.close()
