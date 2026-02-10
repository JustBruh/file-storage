import os
import uuid
from data_transfer_protocol import *
    

class LocalFileSystemStorageProvider:
    def __init__(self, storage_options, db_provider):
        self.storage_path = storage_options
        self.db_provider = db_provider

    def save_file(self, fto, connection):

        # Path for user's files is following: <user_id>/<file_id>
        file_path = self.get_file_path(connection.user_id, fto.filename)

        # Make sure that user's storage dir exists
        os.makedirs(self.storage_path+connection.user_id, exist_ok=True)

        #TODO: Could .part postfix be useful for preventing concurrent reads?
        with open(file_path, "wb") as file:
            connection.receive_and_store_payload(file, fto.file_size)

        self.db_provider.process_new_file(connection.user_id, fto.file_name, fto.file_size, fto.modification_time)

        connection.send_status(DataTransferProtocol.SuccessResponse)

        return
    
    def overwrite_file(self, fto, connection):

        # Path for user's files is the following: <user_id>/<file_id>
        file_path = self.get_file_path(connection.user_id, fto.filename)
        
        if not os.path.exists(file_path):
            connection.send_status(DataTransferProtocol.FileMissingResponse)
            return

        # Open and overwrite the file
        #TODO: Could .part postfix be useful for preventing concurrent reads?
        with open(file_path, "w+b") as file:
            connection.receive_and_store_payload(file, fto.file_size)

        self.db_provider.process_new_file(connection.user_id, fto.file_name, fto.file_size, fto.modification_time)

        connection.send_status(DataTransferProtocol.SuccessResponse)

        return

    def remove_file(self, remove_request, connection):
        # Path for user's files is the following: <user_id>/<file_id>
        file_path = self.get_file_path(connection.user_id, remove_request.filename)
        
        if not os.path.exists(file_path):
            connection.send_status(DataTransferProtocol.FileMissingResponse)
            return

        os.remove(file_path)
        connection.send_status(DataTransferProtocol.SuccessResponse)

        return

    def send_file(self, download_request, connection):

        path = os.path.join(self.storage_path, str(connection.user_id))
        file_path = os.path.join(path, download_request.filename)

        with open(file_path, "rb") as file:
            size = os.path.getsize(file_path)
            mtime = os.path.getmtime(file_path)

            header = DataTransferProtocol.FileTransferOperation((download_request.filename, size, mtime)
            )

            connection.send_data(header.get_header())
            connection.send_file(file)

    def get_file_path(self, user_id, filename):
        file_id = self.db_provider.get_file_id(user_id, filename)

        if not file_id: 
            file_id = uuid.uuid4()

        file_path = os.path.join(self.storage_path, user_id, file_id)

        return file_path