import os
import uuid
from src.protocol.agreement.data_transfer_protocol import *
    

class LocalFileSystemStorageProvider:
    def __init__(self, storage_options, db_provider):
        self.storage_path = storage_options
        self.db_provider = db_provider

    def save_file(self, file_upload_request, connection):
        if self.db_provider.get_file_id(connection.user_id, file_upload_request.file_name):
            connection.send_code(DataTransferProtocol.FileExistsResponse)
            return
        
        # Path for user's files is following: <user_id>/<file_id>
        file_id = str(uuid.uuid4())
        file_dir = os.path.join(self.storage_path, connection.user_id)
        file_path = os.path.join(self.storage_path, connection.user_id, file_id)

        # Make sure that user's storage dir exists
        os.makedirs(file_dir, exist_ok=True)

        try:
            self.receive_and_store_file(connection, file_path, file_upload_request.file_size)
        except Exception as ex:
            if os.path.exists(file_path):
                os.remove(file_path)

            connection.send_code(DataTransferProtocol.ActionNotTakenResponse)
            return
            
        self.db_provider.store_file_metadata(
            file_id,
            connection.user_id,                
            file_upload_request.file_name, 
            file_upload_request.file_modification_time)

        connection.send_code(DataTransferProtocol.SuccessResponse)
        return
    
    def get_file_id(self, connection, file_name):
        file_id = self.db_provider.get_file_id(connection.user_id, file_name)
        
        if not file_id:
            connection.send_code(DataTransferProtocol.FileMissingResponse)
            return
        
        else:
            # Because get_file_id returns tuple
            return file_id[0]

    def overwrite_file(self, file_update_request, connection):
        file_id = self.get_file_id(connection, file_update_request.file_name)
        file_path = os.path.join(self.storage_path, connection.user_id, file_id)
        
        #TODO: How to unify checks like this?
        # Only possible when someone deleted the file from storage, meanwhile DB store file's metadata still
        if not os.path.exists(file_path):
            connection.send_code(DataTransferProtocol.FileMissingResponse)
            return

        # Open and overwrite the file
        #TODO: Check if the overwrite would be not enough, if new file data smaller that previous
        self.receive_and_store_file(connection, file_path, file_update_request.file_size)

        self.db_provider.update_file_modification_time(file_id, file_update_request.file_modification_time)

        connection.send_code(DataTransferProtocol.SuccessResponse)
    
    def rename_file(self, rename_request, connection):
        file_id = self.get_file_id(connection, rename_request.file_name)

        self.db_provider.update_file_name(file_id, rename_request.new_file_name, rename_request.file_modification_time)

        connection.send_code(DataTransferProtocol.SuccessResponse)

    def remove_file(self, remove_request, connection):
        file_id = self.get_file_id(connection, remove_request.file_name)
        file_path = os.path.join(self.storage_path, connection.user_id, file_id)

        os.remove(file_path)

        self.db_provider.remove_file(file_id)
        
        connection.send_code(DataTransferProtocol.SuccessResponse)

    def list_files(self, list_request, connection):
        user_files = self.db_provider.list_user_files(connection.user_id)

        if user_files:
            payload = bytearray()

            for file in user_files:

                # Retreiving file_name and file_mtime
                file_data_line = file[2] + ' ' + file[3] + ' ' + '\n'
                payload.extend(file_data_line.encode())

            connection.send_code(DataTransferProtocol.SuccessResponse)

            response_header = DataTransferProtocol.ListResponse(len(payload))
            connection.send_message(response_header)

            code = connection.receive_response()

            if code != '200':
                self.logger.info("Received no approval from client, pausing payload transfer")
            else:
                connection.send_payload(payload)

        else:
            connection.send_code(DataTransferProtocol.SuccessNoDataResponse)

    def get_file_path(self, user_id, file_name):
        file_id = self.db_provider.get_file_id(user_id, file_name)
        # Path for user's files is the following: <user_id>/<file_id>
        return os.path.join(self.storage_path, user_id, file_id)
    
    def receive_and_store_file(self, connection, file_path, file_size):
        #TODO: Could .part postfix be useful for preventing concurrent reads?
        with open(file_path, "wb") as file:

            # Notify client, that server is ready for data transfer
            connection.send_code(DataTransferProtocol.SuccessResponse)

            payload_processor = lambda chunk: file.write(chunk)

            #TODO: Possible rate limiter required, to prevent very slow uploads
            connection.receive_and_process_payload(payload_processor, file_size)