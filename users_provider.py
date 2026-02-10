class UsersProvider:
    def __init__ (self, db_provider):
        self.db_provider = db_provider

    def authenticate(self, login, password, connection):
        #TODO: Implement authorization, password hash + salt stored within Db
        connection.send_data(file_transfer_operation.get_header())

    def rename_user(self, user_name, new_user_name, connection):
        #TODO: Update field name within table Users, for 
        return storage_path