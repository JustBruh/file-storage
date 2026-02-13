import socket
from src.protocol.helpers.connection import *
from src.protocol.agreement.data_transfer_protocol import *

class FileStorageServer:
    DEFAULT_LISTEN_ADDRESS = "0.0.0.0"
    DEFAULT_LISTEN_PORT = 40221
    MAX_REQUESTS_PER_CONNECTION = 1000
    SOCKET_TIMEOUT_SECONDS = 30
    MAX_CHUNK_SIZE = 1024  
    MAX_CONNECTION_BUFFER_Size = 100 * 1024 * 1024 
    
    def __init__(self, logger, listen_address = DEFAULT_LISTEN_ADDRESS, listen_port = DEFAULT_LISTEN_PORT):
        self.logger = logger
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.enabled_handlers = {}

    def start(self):
        socket.setdefaulttimeout(FileStorageServer.SOCKET_TIMEOUT_SECONDS)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.bind((self.listen_address, self.listen_port))

        self.server_socket.listen()

        self.server_enabled = True

        while self.server_enabled:
            try:
                self.logger.debug("Waiting for new connection")

                connection_socket, addr = self.server_socket.accept()

                self.logger.debug(f"Incoming connection {addr}")

                #TODO: Implement parsing epoll dictionary
                self.process_socket_data(connection_socket)

                self.logger.debug(f"Finished processing connection {addr}")
                
            except Exception as ex:
                self.logger.error(f"Exception received within server main loop: {ex}")

    def stop(self):
        self.server_enabled = False
        self.server_socket.close()

    def process_socket_data(self, connection_socket):
        connection = Connection(connection_socket, FileStorageServer.MAX_CHUNK_SIZE, self.logger)

        process_connection_data = True

        requests_counter = 0

        while process_connection_data:

            if requests_counter > FileStorageServer.MAX_REQUESTS_PER_CONNECTION:
                connection.send_code(DataTransferProtocol.ForbiddenResponse)
                process_connection_data = False
                continue 

            command_name, *command_args = connection.receive_command()
        
            if command_name in self.enabled_handlers:
                if connection.authenticated or command_name == DataTransferProtocol.AUTHENTICATE_COMMAND:
                    handler, request = self.get_command_handler_and_request(command_name)
                    handler(request(command_args), connection)
                else:
                    connection.send_code(DataTransferProtocol.UnauthorizedResponse)
            else:
                connection.send_code(DataTransferProtocol.ForbiddenResponse)

            requests_counter += 1

    def register_handler(self, command, handler_func, command_request):
        self.enabled_handlers[command] = (handler_func, command_request)

    def get_command_handler_and_request(self, command_name):
        return self.enabled_handlers.get(command_name)[0:2]