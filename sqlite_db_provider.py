import sqlite3
import os

class SQLiteDbProvider:
    def __init__(self, connection_string):
        if not os.path.exists(connection_string):
            self.create_database(connection_string)
        
        self.connection = sqlite3.connect(connection_string)
        self.cursor = self.connection.cursor()

    def create_database(self, connection_string):
        connection = sqlite3.connect(connection_string)
        cursor = connection.cursor()
    
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                login TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
    
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                file_name TEXT NOT NULL,
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

    def get_user_data(self, login):
        self.cursor.execute("SELECT id, name, password FROM Users WHERE login = ?", (login,))
        return self.cursor.fetchone()
    
    def get_user_data_by_id(self, id):
        self.cursor.execute("SELECT login, name, password FROM Users WHERE id = ?", (id,))
        return self.cursor.fetchone()

    def get_file_id(self, user_id, file_name):
        self.cursor.execute("SELECT id FROM Files WHERE user_id = ? AND file_name = ?", (user_id, file_name,))
        result = self.cursor.fetchone()
        return result
    
    def store_file_metadata(self, file_id, user_id, file_name, file_mtime):
        self.cursor.execute("""
            INSERT INTO Files (id, user_id, file_name, file_mtime) 
            VALUES (?, ?, ?, ?)
        """, (file_id, user_id, file_name, file_mtime,))
        self.connection.commit()

    def update_file_name(self, file_id, new_file_name, file_mtime):
        self.cursor.execute("UPDATE Files SET file_name = ?, file_mtime = ? WHERE id = ?", (new_file_name, file_mtime, file_id,))
        self.connection.commit()

    def update_file_modification_time(self, file_id, file_mtime):
        self.cursor.execute("UPDATE Files SET file_mtime = ? WHERE id = ?", (file_mtime, file_id,))
        self.connection.commit()

    def remove_file(self, file_id):
        self.cursor.execute("DELETE From Files WHERE id = ?", (file_id, ))
        self.connection.commit()

    def update_user_name(self, user_id, old_user_name, new_user_name, update_date):
        self.cursor.execute("UPDATE Users SET name = ? WHERE id = ?", (new_user_name, user_id))
        self.cursor.execute("""
            INSERT INTO users_history (user_id, old_name, new_name, date_modified) 
            VALUES (?, ?, ?, ?)
        """, (user_id, old_user_name, new_user_name, update_date,))
        self.connection.commit()

    def list_user_files(self, user_id):
        self.cursor.execute("SELECT * FROM Files WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()