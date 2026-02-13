import socket
import os
from ...protocol.agreement.data_transfer_protocol import *
from ...protocol.helpers.connection import *

class FileStorageClient:
    REMOTE_PORT = 40221
    SOCKET_TIMEOUT_SECONDS = 30
    CHUNK_SIZE = 1024

    AUTHENTICATE_COMMAND = 'authenticate'
    RENAME_USER_COMMAND = 'rename_user'
    LIST_COMMAND = 'list'
    REMOVE_COMMAND = 'remove_file'
    RENAME_COMMAND = 'rename_file'
    UPLOAD_COMMAND = 'upload_file'
    UPDATE_COMMAND = 'update_file'

    def __init__(self):
        self.connection = None

        self.handlers = {
            FileStorageClient.AUTHENTICATE_COMMAND: (self.single_request_handler, DataTransferProtocol.AuthenticationRequest, ('login', 'password',)),
            FileStorageClient.RENAME_USER_COMMAND: (self.single_request_handler, DataTransferProtocol.UserRenameRequest, ('new_username',)),
            FileStorageClient.LIST_COMMAND: (self.receive_data_handler, DataTransferProtocol.ListRequest, ()),
            FileStorageClient.REMOVE_COMMAND: (self.single_request_handler, DataTransferProtocol.FileRemoveRequest, ('file_name',)),
            FileStorageClient.RENAME_COMMAND: (self.single_request_handler, DataTransferProtocol.FileRenameRequest, ('file_name', 'new_file_name',)),
            FileStorageClient.UPLOAD_COMMAND: (self.send_file_handler, DataTransferProtocol.FileUploadRequest, ('file_name',)),
            FileStorageClient.UPDATE_COMMAND: (self.send_file_handler, DataTransferProtocol.FileUpdateRequest, ('file_name',)),
        }

    def connect_and_authenticate(self, remote_address, args, logger):
        socket.setdefaulttimeout(FileStorageClient.SOCKET_TIMEOUT_SECONDS)

        connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        connection_socket.connect((remote_address, FileStorageClient.REMOTE_PORT))

        self.connection = Connection(connection_socket, FileStorageClient.CHUNK_SIZE, logger)

        if not connection_socket:
            raise ConnectionError(f"Failed to connect to server: {remote_address}")

        res = self.handle_command('authenticate', args)

        if not res:
            raise ConnectionError(f"Authentication failed with login: {args.login}")
    
    def extract_required_args(self, required_args, args):
        return [getattr(args, ra) for ra in required_args]

    #TODO: Fix this hack required due to argparser args being namespace, and positional extraction now is only supported for DTP Requests
    def get_command_handler_with_request_and_args(self, command_name, args):
        if command_name not in self.handlers:
            raise ValueError(f'Command not allowed: {command_name}')
        
        handler, request, required_args = self.handlers.get(command_name)
        args = self.extract_required_args(required_args, args)

        return handler, request, args

    def handle_command(self, command_name, command_args):
        handler, request, extracted_args = self.get_command_handler_with_request_and_args(command_name, command_args)
        return handler(request, extracted_args)
    
    def single_request_handler(self, request, args):
        self.connection.send_message(request(args,))
        return self.connection.receive_response()

    def send_file_handler(self, request, args):
        file_name = args[0]
        file_size_bytes = os.path.getsize(file_name)

        with open(file_name, 'rb') as file:
            request = request((file_name, file_size_bytes,))
            self.connection.send_message(request)

            # Wait until server is ready for transfer
            code = self.connection.receive_response()

            if code == '200':
                with open(file_name, "rb") as file:
                    self.connection.socket.sendfile(file)

                code = self.connection.receive_response()

            return code
    
    def receive_data_handler(self, request, args):
        self.connection.send_message(request(args))

        code = self.connection.receive_response()

        if code == '200':

            payload_size = self.connection.receive_response()

            # Notify server, that client is ready for data transfer
            self.connection.send_code(DataTransferProtocol.SuccessResponse)

            buffer = bytearray()

            processing_func = lambda chunk: buffer.extend(chunk)

            self.connection.receive_and_process_payload(processing_func, payload_size)

            return buffer.decode()
        
        return code