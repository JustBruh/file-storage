import sqlite3
import os
import datetime

class SQLiteDbProvider:
    def __init__(self, connection_string):
        self.connection = sqlite3.connect(connection_string)
        self.cursor = self.connection.cursor()

        if not os.path.exists(self.connection_string):
            self.create_database()

    def create_database(db_name):
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
    
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                login TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
    
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_name TEXT NOT NULL,
                file_uuid TEXT NOT NULL,
                file_mtime TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                old_name TEXT NOT NULL,
                new_name TEXT NOT NULL,
                date_modified TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        """)
    
        connection.commit()
        connection.close()

    def get_user_data(self, login):
        self.cursor.execute("SELECT id, password FROM Users WHERE login = ?", (login))
        return self.cursor.fetchone()[0]

    def get_user_files(self, user_name):
        self.cursor.execute("""
            SELECT * FROM Files 
            INNER JOIN Users ON Users.id = Files.user_id 
            WHERE Users.name = ?
        """, (user_name,))
        return self.cursor.fetchall()

    def get_file_id(self, user_id, file_name):
        self.cursor.execute("SELECT file_uuid FROM Files WHERE user_id = ? AND file_name = ?", (user_id, file_name))
        result = self.cursor.fetchone()
        return result[0]
    
    def store_file_metadata(self, user_id, file_id, file_name, file_mtime):
        self.cursor.execute("""
            INSERT INTO Files (user_id, file_uuid, file_name, file_mtime) 
            VALUES (?, ?, ?, ?)
        """, (user_id, file_id, file_name, file_mtime))
        self.connection.commit()

    def update_file_name(self, file_id, new_file_name, file_mtime):
        self.cursor.execute("UPDATE Files SET file_name = ?, file_mtime = ? WHERE id = ?", (new_file_name, file_mtime, file_id))

    def update_user_name(self, user_id, new_user_name):
        date = datetime.now()
        self.cursor.execute("UPDATE Users SET name = ? WHERE id = ?", (new_user_name, user_id))
        self.cursor.execute("""
            INSERT INTO users_history (user_id, old_name, new_name, date_modified) 
            VALUES (?, ?, ?, ?)
        """, (user_id, self.get_user_data(user_id)[1], new_user_name, date))
        self.connection.commit()
    
    def get_user_data(self, login):
        self.cursor.execute("SELECT id, password FROM Users WHERE login = ?", (login))
        return self.cursor.fetchone()[0]

    def list_user_files(self, user_id):
        self.cursor.execute("SELECT * FROM Files WHERE user_id = ?", (user_id))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()