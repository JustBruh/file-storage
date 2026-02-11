import os
import uuid
from data_transfer_protocol import *
    

class LocalFileSystemStorageProvider:
    def __init__(self, storage_options, db_provider):
        self.storage_path = storage_options
        self.db_provider = db_provider

    def save_file(self, fto, connection):

        if self.db_provider.get_file_id(connection.user_id, fto.file_name):
            connection.send_code(DataTransferProtocol.FileExistsResponse)
            return
        
        # Path for user's files is following: <user_id>/<file_id>
        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.storage_path, connection.user_id, file_id)

        # Make sure that user's storage dir exists
        os.makedirs(self.storage_path+connection.user_id, exist_ok=True)

        #TODO: Could .part postfix be useful for preventing concurrent reads?
        with open(file_path, "wb") as file:

            # Notify client, that server is ready for data transfer
            connection.send_code(DataTransferProtocol.SuccessResponse)

            payload_processor = lambda chunk: file.write(chunk)

            connection.receive_and_process_payload(payload_processor, fto.file_size)

        self.db_provider.store_file_metadata(connection.user_id, fto.file_name, fto.file_size, fto.modification_time)

        connection.send_code(DataTransferProtocol.SuccessResponse)

        return
    
    def overwrite_file(self, file_update_request, connection):

        file_path = self.get_file_path(connection.user_id, file_update_request.file_name)
        
        if not os.path.exists(file_path):
            connection.send_code(DataTransferProtocol.FileMissingResponse)
            return
        
        else:
            connection.send_code(DataTransferProtocol.SuccessResponse)

        # Open and overwrite the file
        #TODO: Could .part postfix be useful for preventing concurrent reads?
        with open(file_path, "w+b") as file:

            # Notify client, that server is ready for data transfer
            connection.send_code(DataTransferProtocol.SuccessResponse)

            payload_processor = lambda chunk: file.write(chunk)

            connection.receive_and_process_payload(payload_processor, file_update_request.file_size)

        self.db_provider.store_file_metadata(
            connection.user_id, 
            file_update_request.file_name, 
            file_update_request.file_size, 
            file_update_request.modification_time)

        connection.send_code(DataTransferProtocol.SuccessResponse)

        return
    
    def rename_file(self, rename_request, connection):

        file_path = self.get_file_path(connection.user_id, rename_request.file_name)
        
        if not os.path.exists(file_path):
            connection.send_code(DataTransferProtocol.FileMissingResponse)
            return

        os.rename(file_path, rename_request.new_file_name)
        connection.send_code(DataTransferProtocol.SuccessResponse)

        return

    def remove_file(self, remove_request, connection):

        file_path = self.get_file_path(connection.user_id, remove_request.file_name)
        
        if not os.path.exists(file_path):
            connection.send_code(DataTransferProtocol.FileMissingResponse)
            return

        os.remove(file_path)
        connection.send_code(DataTransferProtocol.SuccessResponse)

        return

    def list_files(self, connection):
        list_response_payload = self.db_provider.list_user_files(connection.user_id)
        list_response = DataTransferProtocol.ListResponse(len(list_response_payload))
        connection.send_message(list_response)
        connection.send_payload(list_response_payload)

    def get_file_path(self, user_id, file_name):
        file_id = self.db_provider.get_file_id(user_id, file_name)
        # Path for user's files is the following: <user_id>/<file_id>
        return os.path.join(self.storage_path, user_id, file_id)