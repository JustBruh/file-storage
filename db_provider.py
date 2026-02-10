import psycopg2

class PostreSQLDbProvider:
    def __init__(self, connection_string):
        self.cursor = psycopg2.connect(connection_string).cursor()
        self

    def get_user_data(self, user_name):
        cursor.execute("SELECT * FROM Table Users WHERE name = '{user_name}'")
        return cursor.fetchone()
    
    def get_user_files(self, user_name):
        cursor.execute("SELECT * FROM Table Files INNER JOIN Users ON Users.id = Files.user_id")
        return cursor.fetchone()
    
    def get_user_file_location(self, user_name, file_name):
        cursor.execute("SELECT file_guid_name FROM Table Files INNER JOIN Users ON Users.id = Files.user_id WHERE file_alias = '{file_name}' JOIN SELECT name FROM Table Users where user_name = user_name")
        cursor.fetchone()

        return ''
    
    def update_user_name(self, user_id, new_user_name):
        date = datetime.now()
        cursor.execute("UPDATE Table Users WHERE user.name = '{user_name}' WITH name = '{new_user_name}'")
        cursor.execute("UPDATE Table users_history WITH old_name = '{user_name} new_name = '{new_user_name}' date_modified = '{date}'")
        return cursor.fetchone()
    
    def get_file_id(self, user_id, filename):
        return 
    
    def store_file_metadata(self, user_id, file_id, file_name, file_mtime):
        return