import socket
import os
from data_transfer_protocol import *
from connection import *

class FileStorageClient:
    REMOTE_PORT = 40221
    SOCKET_TIMEOUT_SECONDS = 30
    CHUNK_SIZE = 1024

    AUTHENTICATE_COMMAND = 'authenticate'
    LIST_COMMAND = 'list'
    REMOVE_COMMAND = 'remove_file'
    RENAME_COMMAND = 'rename_file'
    UPLOAD_COMMAND = 'upload_file'
    UPDATE_COMMAND = 'update_file'

    def __init__(self, logger):
        self.connection = None
        self.logger = logger

        self.handlers = {
            FileStorageClient.AUTHENTICATE_COMMAND: (self.single_request_handler, DataTransferProtocol.AuthenticationRequest),
            FileStorageClient.LIST_COMMAND: (self.list_files, DataTransferProtocol.ListRequest),
            FileStorageClient.REMOVE_COMMAND: (self.single_request_handler, DataTransferProtocol.FileRemoveRequest),
            FileStorageClient.RENAME_COMMAND: (self.single_request_handler, DataTransferProtocol.FileRenameRequest),
            FileStorageClient.UPLOAD_COMMAND: (self.send_file_handler, DataTransferProtocol.FileUploadRequest),
            FileStorageClient.UPDATE_COMMAND: (self.send_file_handler, DataTransferProtocol.FileUpdateRequest),
        }

    def connect_and_authenticate(self, remote_address, login, password):
        socket.setdefaulttimeout(FileStorageClient.SOCKET_TIMEOUT_SECONDS)

        connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        connection_socket.connect((remote_address, FileStorageClient.REMOTE_PORT))

        self.connection = Connection(connection_socket, FileStorageClient.CHUNK_SIZE, self.logger)

        if not connection_socket:
            raise ConnectionError(f"Failed to connect to server: {remote_address}")

        res = self.handle_command('authenticate', (login, password,))

        if not res:
            raise ConnectionError(f"Authentication failed with login: {login}")
    
    def get_command_handler_and_request(self, command_name):
        return self.handlers.get(command_name)[:1]

    def handle_command(self, command_name, command_args):
        handler, request = self.get_command_handler_and_request(command_name)
        return handler(request, command_args)
    
    def single_request_handler(self, request, args):
        return self.connection.send_message(request(args,))

    def list_files(self):
        list_request = DataTransferProtocol.ListRequest(())

        self.connection.send_message(list_request)

        code = self.connection.receive_response()

        if code == '200':

            payload_size = self.connection.receive_response()

            # Notify server, that client is ready for data transfer
            self.connection.send_code(DataTransferProtocol.SuccessResponse)

            buffer = bytearray()

            processing_func = lambda chunk: buffer.extend(chunk)

            self.connection.receive_and_process_payload(processing_func, payload_size)

            return str(buffer)
        
        return code

    def send_file_handler(self, request, args):
        file_name = args[0]
        file_size_bytes = os.path.getsize(file_name)

        with open(file_name, 'rb') as file:
            request = request(file_name, file_size_bytes)
            self.connection.send_message(request)

            # Wait until server is ready for transfer
            code = self.connection.receive_response()

            if code == '200':
                with open(file_name, "rb") as file:
                    self.connection.socket.sendfile(file)

                code = self.connection.receive_response()

            return code