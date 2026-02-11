from data_transfer_protocol import *

class UsersProvider:
    def __init__ (self, db_provider):
        self.db_provider = db_provider

    def authenticate(self, authentication_request, connection):
        #TODO: Implement authorization, password hash + salt stored within Db
        res = self.db_provider.get_user_data(authentication_request.login)

        if not res:
            return False, "No such login"
        
        user_id, _, user_password = res

        if user_password != authentication_request.password:
            return False, "No such login or incorrect password"
        
        else:
            connection.authenticated = True
            connection.user_id = user_id

            connection.send_message(DataTransferProtocol.SuccessResponse)

            return True, "Authentication successfull"
        
    def rename_user(self, rename_request, connection):
        res = self.db_provider.update_user_name(connection.user_id, rename_request.new_user_name)

        if res:
            connection.send_message(DataTransferProtocol.SuccessResponse)
            return True, "User rename successfull"
        
        return False