import datetime
from data_transfer_protocol import *

class UsersProvider:
    def __init__ (self, db_provider):
        self.db_provider = db_provider

    def authenticate(self, authentication_request, connection):

        #TODO: Implement authorization, password hash + salt stored within Db

        # returns (user_id, name, user_password)
        res = self.db_provider.get_user_data(authentication_request.login)
        
        if not res or res[2] != authentication_request.password:
            connection.send_code(DataTransferProtocol.InvalidCredentialsResponse)
            
        else:
            connection.authenticated = True
            connection.user_id = str(res[0])

            connection.send_code(DataTransferProtocol.SuccessResponse)
        
    def rename_user(self, rename_request, connection):
        # returns (login, name, user_password)
        res = self.db_provider.get_user_data_by_id(connection.user_id)

        if res[1] == rename_request.new_user_name:
            connection.send_code(DataTransferProtocol.ActionNotTakenResponse)
        else: 
            self.db_provider.update_user_name(connection.user_id, res[1], rename_request.new_user_name, datetime.now())
            connection.send_code(DataTransferProtocol.SuccessResponse)