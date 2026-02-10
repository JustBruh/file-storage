import socket
import os
from data_transfer_protocol import *
from connection import *

class FileStorageClient:
    REMOTE_PORT = 40221
    CHUNK_SIZE = 1024

    def __init__(self, logger):
        self.connection = None
        self.logger = logger

    def connect(self, remote_address):
        connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            connection_socket.connect((remote_address, FileStorageClient.REMOTE_PORT))

            self.connection = Connection(connection_socket, FileStorageClient.CHUNK_SIZE)

            if connection_socket:
                self.logger.info("Connected successfully")
        except ConnectionRefusedError as ex:
                self.logger.info("Connection failed: ", ex)

                return False

    def authenticate(self, login, password):
        auth_request = DataTransferProtocol.AuthenticationRequest((login, password))

        self.connection.send_message(auth_request)

        res, _ = self.connection.receive_response()

        if res == 200:
            self.logger.info("Authentication successfull")
        else:
            self.logger.info("Authentication failed")

    def rename_user(self, new_user_name):
        rename_user_request = DataTransferProtocol.UserRenameRequest((new_user_name))

        self.connection.send_message(rename_user_request)

        res, _ = self.connection.receive_response()

        if res == 200:
            self.logger.info("User rename successfull")
        else:
            self.logger.info("User rename failed")

    def remove_file(self, file_name):
        remove_file_request = DataTransferProtocol.FileRemoveRequestRequest((file_name))

        self.connection.send_message(remove_file_request)

        res, _ = self.connection.receive_response()

        if res == 200:
            self.logger.info("File removal successfull")
        else:
            self.logger.info("File removal failed")

    def list_files(self):
        list_request = DataTransferProtocol.ListRequest()

        self.connection.send_message(list_request)

        payload_size, _ = self.connection.receive_response()

        buffer = bytearray()

        processing_func = lambda chunk: buffer.extend(chunk)

        res = self.connection.receive_and_process_payload(processing_func, payload_size)

        return res

    def rename_file(self, file_name, new_file_name):
        rename_file_request = DataTransferProtocol.FileRemoveRequestRequest((file_name, new_file_name))

        self.connection.send_message(rename_file_request)

        res, _ = self.connection.receive_response()

        if res == 200:
            self.logger.info("File rename successfull")
        else:
            self.logger.info("File rename failed")

    def upload_file(self, file_name):
        file_size_bytes = os.path.getsize(file_name)

        with open(file_name, 'rb') as file:
            file_upload_request = DataTransferProtocol.FileUploadRequest((file_name, file_size_bytes))

            self.connection.send_message(file_upload_request)

            res = self.connection.receive_response()

            if res == 200:
                with open("file_name", "rb") as file:
                    self.connection.socket.sendfile(file)

                res = self.connection.receive_response()

                if res == 200:
                    self.logger.info("File uploaded")
                else:
                    self.logger.info("File upload failed")
            else:
                self.logger.info("Failed to start file upload")

    def update_file(self, file_name):
        file_size_bytes = os.path.getsize(file_name)


        with open(file_name, 'rb') as file:
            file_update_request = DataTransferProtocol.FileUpdateRequest((file_name, file_size_bytes))

            self.connection.send_message(file_update_request)

            res = self.connection.receive_response()

            if res == 200:
                with open("file_name", "rb") as file:
                    self.connection.socket.sendfile(file)

                res = self.connection.receive_response()

                if res == 200:
                    self.logger.info("File updated")
                else:
                    self.logger.info("File update failed")
            else:
                self.logger.info("Failed to start file update")