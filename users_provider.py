from data_transfer_protocol import *

class UsersProvider:
    def __init__ (self, db_provider):
        self.db_provider = db_provider

    def authenticate(self, login, password, connection):
        #TODO: Implement authorization, password hash + salt stored within Db
        user_id, user_password = self.db_provider.get_user_data(login)

        if user_password != password:
            return False, "No such login or incorrect password"
        
        else:
            connection.authenticated = True
            connection.user_id = user_id

            connection.send_message(DataTransferProtocol.SuccessResponse)

            return True, "Authentication successfull"
        
    def rename_user(self, user_id, new_user_name, connection):
        res = self.db_provider.update_user_name(user_id, new_user_name)

        if res:
            connection.send_message(DataTransferProtocol.SuccessResponse)
            return True, "User rename successfull"
        
        return False