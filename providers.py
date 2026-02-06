import psycopg2
import os


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
    
    def update_user_name(self, user_name, new_user_name):
        date = datetime.now()
        cursor.execute("UPDATE Table Users WHERE user.name = '{user_name}' WITH name = '{new_user_name}'")
        cursor.execute("UPDATE Table users_history WITH old_name = '{user_name} new_name = '{new_user_name}' date_modified = '{date}'")
        return cursor.fetchone()
    

class LocalFileSystemStorageProvider:
    def __init__(self, storage_options, db_provider):
        self.storage_path = storage_options
        self.db_provider = db_provider

    def save_file(self, file_transfer_object, connection):
        path = self.db_provider.get_user_file_location(user_name, file_transfer_object.file_name)

        self.db_provider.process_new_file(file_transfer_object)

        # And apply sanitazing for each request
        with open('{connection.username}/{file_transfer_object.file_name}.part', 'wb') as file:
            #overwrite with empty content if exists
            connection.receive_and_write_file(file, file_size, file_modification_time)

        os.rename()

    def remove_file(self, remove):
        return

    def send_file(self, download_request, connection):
        self.storage_provider.send_file()
        filename = download_request.filename

        # Check if username is corresponding to the auth_data
        # And apply sanitazing for each request
        with open('{connection.username}/{download_request.filename}', 'rb') as file:
            file_transfer_operation = DataTransferProtocol.FileTransferOperation((filename, file.size, file.modification_time))

            connection.send_data(file_transfer_operation.get_header())

            connection.send_file(file)


    def get_path(self, directory_name, file_name):
        file_name

        return '{directory_name}'/'{file_name}'


class UsersProvider:
    def __init__ (self, db_provider):
        self.db_provider = db_provider

    def authenticate(self, login, password, connection):
        #TODO: Implement authorization, password hash + salt stored within Db
        connection.send_data(file_transfer_operation.get_header())

    def rename_user(self, user_name, new_user_name, connection):
        #TODO: Update field name within table Users, for 
        return