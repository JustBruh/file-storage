import socket
from connection import *
from data_transfer_protocol import *

class FileStorageServer:
    DEFAULT_LISTEN_ADDRESS = "0.0.0.0"
    DEFAULT_LISTEN_PORT = 40221
    MAX_REQUESTS_PER_CONNECTION = 1000
    SOCKET_TIMEOUT_SECONDS = 30
    MAX_CHUNK_SIZE = 1024  
    MAX_CONNECTION_BUFFER_Size = 100 * 1024 * 1024 
    
    def __init__(self, listen_address = DEFAULT_LISTEN_ADDRESS, listen_port = DEFAULT_LISTEN_PORT):
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.enabled_handlers = {}

    def start(self):
        socket.setdefaulttimeout(FileStorageServer.SOCKET_TIMEOUT_SECONDS)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_socket.bind((self.listen_address, self.listen_port))

        server_socket.listen()

        self.server_enabled = True

        while self.server_enabled:

            connection_socket = server_socket.accept()
            connection_socket.timeout()

            #TODO: Somehow start processing new connection in background, without awaiting for result, check up poll, epoll, select for async sockets
            self.process_socket_data(connection_socket)

    def stop(self):
        self.server_enabled = False

    def process_socket_data(self, connection_socket):
        connection = Connection(connection_socket, FileStorageServer.MAX_CHUNK_SIZE)

        process_connection_data = True

        connection_counter = 0

        while process_connection_data:

            if connection_counter > FileStorageServer.MAX_REQUESTS_PER_CONNECTION:
                connection.send_status(DataTransferProtocol.ForbiddenResponse)
                process_connection_data = False
                continue 

            command_name, *command_args = connection.receive_command()

            if command_name in self.enabled_handlers:
                if connection.authenticated or command_name == DataTransferProtocol.AUTHENTICATE_COMMAND:
                    handler = self.get_command_handler(command_name)
                    request = self.get_command_request(command_name)(command_args)      # Instantiate Request class
                    handler(request, connection)
                else:
                    connection.send_status(DataTransferProtocol.UnauthorizedResponse)
            else:
                connection.send_status(DataTransferProtocol.ForbiddenResponse)

    def get_command_handler(self, command_name):
        return self.enabled_handlers.get(command_name)[0]

    def get_command_request(self, command_name):
        return self.enabled_handlers.get(command_name)[1]

    def register_handler(self, command, handler_func, command_request):
        self.enabled_handlers[command] = (handler_func, command_request)