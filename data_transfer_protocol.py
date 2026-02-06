import struct

class DataTransferProtocol:

    # Arguments of a command must be separated by whitespace
    ARGS_SEPARATOR = ' '
    
    # Commands must be separated by carriage return
    LINE_TERMINATOR = '\n'

    #Allowed commands
    AUTHENTICATE_COMMAND = 'AUTHENTICATE'
    DOWNLOAD_COMMAND = 'DOWNLOAD'
    REMOVE_COMMAND = 'REMOVE'
    RENAME_COMMAND = 'RENAME'
    LIST_COMMAND = 'LIST'
    FILE_TRANSFER_COMMAND = 'FILE_TRANSFER'

    class BaseOperation:
        def get_header(self):
            header = ProtocolHelper.to_header_format((self.__dict__.values()))
            return struct.pack(header)

    # The following requests may be sent by client

    # AUTHENTICATE <username> <password> \n
    class AuthenticationRequest(BaseOperation):
        def __init__(self, args):
            self.name = DataTransferProtocol.AUTHENTICATE_COMMAND
            self.username = args[0]
            self.password = args[1]


    # DOWNLOAD <filename> \n
    class DownloadRequest(BaseOperation):
        def __init__(self, args):
            self.name = DataTransferProtocol.DOWNLOAD_COMMAND
            self.filename = args[0]

    # REMOVE <filename> \n
    class RemoveRequest(BaseOperation):
        def __init__(self, args):
            self.name = DataTransferProtocol.REMOVE_COMMAND
            self.filename = args[0]


    # RENAME <username> \n
    class RenameRequest(BaseOperation):
        def __init__(self, args):
            self.name = DataTransferProtocol.RENAME_COMMAND
            self.new_username = args[0]


    # LIST \n
    class ListRequest(BaseOperation):
        def __init__(self):
            self.name = DataTransferProtocol.LIST_COMMAND


    # The following responses may be sent by server

    # <following_text_payload_length> \n
    # <text_payload>
    class ListResponse(BaseOperation):
        def __init__(self, payload_length):
            self.payload_length = payload_length

    # 200 \n
    class SuccessResponse(BaseOperation):
        def __init__ (self):
            self.code = 200

    # 401 \n
    class UnauthorizedResponse(BaseOperation):
        def __init__ (self):
            self.code = 401

    # 403 \n
    class ForbiddenResponse(BaseOperation):
        def __init__ (self):
            self.code = 403

    # 404 \n
    class FileMissingResponse(BaseOperation):
        def __init__ (self):
            self.code = 404


    # The following one can be used either by client and server, in case of file upload and download respectively

    # FILE_TRANSFER <filename> <filesize> <modification_time> \n
    # <binary_payload>
    class FileTransferOperation(BaseOperation):
        def __init__(self, args):
            self.name = DataTransferProtocol.FILE_TRANSFER_COMMAND
            self.filename = args[0]
            self.filesize = args[1]
            self.file_modification_time = args[2]
            

class ProtocolHelper:
    def to_header_format(self, data):
        return ' '.join(data)+DataTransferProtocol.LINE_TERMINATOR
    
    def to_text_payload_format(self, data_objects):
            res = ''

            for data_object in data_objects:
                res += ' '.join(tuple(str(item) for item in data_object.values()))+DataTransferProtocol.LINE_TERMINATOR

            return res  
    

class Connection:
    def __init__(self, socket):
        self.buffer = bytearray()
        self.chunk_size = 1024
        
        self.socket = socket

        self.authenticated = False
        self.username = None

    def close(self):
        self.socket.close()

    def receive_data_until_terminator(self):
        data = bytearray()

        #TODO: Implement some limiter
        while self.command_terminator not in data:
            chunk = self.socket.recv(self.chunk_size)

            if not chunk:
                return "Connection closed"
            
            data += chunk

        res, self.buffer = data.split('\n', 2)

        return res
    
    def receive_data_with_exact_size(self, data_size):
        data = bytearray()

        while len(data) < data_size:
            chunk = self.socket.recv(self.chunk_size)
            
            if not chunk:
               return "Connection closed"

            data += chunk 

        res = data[0:data_size]

        self.buffer += data[data_size:]

        return res
    
    def receive_and_write_to_file(self, file, file_size):
        data_received = 0

        while data_received < file_size:
            chunk = self.socket.recv(self.chunk_size)
            
            if not chunk:
               return "Connection closed"

            if data_received + len(chunk) > file_size:
                data_left = file_size-data_received

                last_chunk = chunk[0:data_left]
                self.buffer = chunk[data_left:]

                chunk = last_chunk

            file.write(chunk)

            data_received += len(chunk)

        return True

    def send_data(self, data):                                
        return self.socket.send(data)
    
    def send_status(self, status):
        self.send_data(status.get_header())
    
    def send_file(self, file):
        self.socket.sendfile(file)

    def receive_command(self):
        command = self.receive_data_until_terminator()
        sanitized_command = self.sanitize(command)
        
        return sanitized_command.split(" ")
    
    def _sanitize(self, command):
        # TODO: Implement string sanitazing
        return command