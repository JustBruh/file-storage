import socket
from data_transfer_protocol import *


class FileStorageServer:
    def __init__(self, listen_address = "0.0.0.0", listen_port = 40221):
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.enabled_handlers = {}

    def start(self):
        server_socket = socket.create_server((self.listen_address, self.listen_port))

        self.listen = True

        while self.listen:

            server_socket.listen()
            connection_socket = server_socket.accept()

            # Somehow start processing new connection in background, without awaiting for result
            self.process_socket_data(connection_socket)

    def process_socket_data(self, connection_socket):

        while not connection_socket.closed():

            connection = Connection(connection_socket)

            command_name, *command_args = connection.receive_command()
            
            if command_name in self.enabled_handlers:
                if connection.authenticated or command_name == DataTransferProtocol.AUTHENTICATE_COMMAND:
                    handler = self.get_command_handler(command_name)
                    request = self.get_command_request(command_name)(command_args)

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
