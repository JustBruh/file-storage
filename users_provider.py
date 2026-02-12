import datetime
from data_transfer_protocol import *

class UsersProvider:
    def __init__ (self, db_provider):
        self.db_provider = db_provider

    def authenticate(self, authentication_request, connection):
        #TODO: Implement authorization, password hash + salt stored within Db
        res = self.db_provider.get_user_data(authentication_request.login)
        
        if not res:
            connection.send_code(DataTransferProtocol.InvalidCredentialsResponse)
            return False
        
        user_id, name, user_password = res

        if user_password != authentication_request.password:
            connection.send_code(DataTransferProtocol.InvalidCredentialsResponse)
            return False
        
        else:
            connection.authenticated = True
            connection.user_id = str(user_id)

            connection.send_code(DataTransferProtocol.SuccessResponse)
            return True
        
    def rename_user(self, rename_request, connection):
        date = datetime.now()

        res = self.db_provider.update_user_name(connection.user_id, rename_request.new_user_name, date)

        if res:
            connection.send_code(DataTransferProtocol.SuccessResponse)
            return True,
    
        connection.send_code(DataTransferProtocol.ActionNotTakenResponse)
        return False