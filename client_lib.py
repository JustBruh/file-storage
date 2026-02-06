import socket
import struct
from data_transfer_protocol import *


class FileStorageClient:
    REMOTE_PORT = 40221

    def _authenticate_on_server(socket, username, password):
        auth_request = DataTransferProtocol.AuthenticationRequest((username, password))
        res = socket.send(auth_request.get_header())

        if (struct.unpack(res) == 200):
                print('Authentication successfull')
        else:
            print('Authentication failed')

    def upload_file(self, remote_address, file_name, username, password):
        connection = self.create_socket_and_authenticate(remote_address, username, password)

        with open('{connection.username}/{download_request.filename}', 'rb') as file:
            file_transfer_operation = DataTransferProtocol.FileTransferOperation((file_name, file.size, file.modification_time))

            connection.send_data(file_transfer_operation.get_header())

            connection.send_file(file)

            res = connection.receive_data_until_terminator()

            if (struct.unpack(res) == 200):
                print('Upload successfull')
            else:
                print('Upload failed')

    def download_file(self, remote_address, file_name, username, password):
        connection = self.create_socket_and_authenticate(remote_address, username, password)

        with open('{connection.username}/{file_transfer_object.filename}', 'wb') as file:
            download_request = DataTransferProtocol.DownloadRequest((file_name, ))

            res = connection.send_data(download_request.get_header())

            res = connection.receive_data_until_terminator()

            connection.receive_and_write_file(file, struct.unpack(res.split('\n')[0]), file_modification_time)

    def rename_user(self, remote_address, username, password, new_username):
        connection = self.create_socket_and_authenticate(remote_address, username, password)
        rename_request = DataTransferProtocol.RenameRequest(new_username)

        connection.send_data(rename_request.get_header())

        res = connection.receive_data_until_terminator()

        print(res)

    def list_files(self, remote_address, username, password, new_username):
        connection = self.create_socket_and_authenticate(remote_address, self.REMOTE_PORT, username, password)
        list_request = DataTransferProtocol.ListRequest()

        connection.send_data(list_request.get_header())

        res = connection.receive_data_until_terminator()

        res = connection.receive_data_with_exact_size(struct.unpack(res.split('\n')[0]))

        print(res)

    def create_socket_and_authenticate(self, remote_address, username, password):
        new_socket = socket.create_connection((remote_address, self.REMOTE_PORT))

        connection = Connection(new_socket)

        auth_request = DataTransferProtocol.AuthenticationRequest((username, password))
        connection.send_data(auth_request.get_header())

        return connection