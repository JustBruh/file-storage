import struct

class DataTransferProtocol:
    # Limitations of protocol
    MAX_HEADER_SIZE = 4096
    MAX_USERNAME_LENGTH = 128
    MAX_LOGIN_LENGTH = 128
    MAX_PASSWORD_HASH_LENGTH = 255
    MAX_FILENAME_LENGTH = 255
    MAX_PAYLOAD_SIZE = 100 * 1024 * 1024 # 100MB

    # Arguments of a command must be separated by whitespace
    ARGS_SEPARATOR = b' '
    
    # Commands must be separated by line return symbol
    LINE_TERMINATOR = b'\n'

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
            self.login = args[0]
            self.password_hash = args[1]
            self.salt = args[2]

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

    # RENAME <filename> <new_file_name> \n
    class RenameRequest(BaseOperation):
        def __init__(self, args):
            self.name = DataTransferProtocol.RENAME_FILE_COMMAND
            self.filename = args[0]
            self.new_file_name = args[1]

    # RENAME_USER <username> \n
    class RenameUserRequest(BaseOperation):
        def __init__(self, args):
            self.name = DataTransferProtocol.RENAME_USER_COMMAND
            self.new_name = args[0]

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
            self.code = 20

    # 403 \n
    class ForbiddenResponse(BaseOperation):
        def __init__ (self):
            self.code = 403

    # 413 \n
    class LengthLimitExceeded(BaseOperation):
        def __init__ (self):
            self.code = 413

    # 530 \n
    class UnauthorizedResponse(BaseOperation):
        def __init__ (self):
            self.code = 401

    # 550 \n
    class FileExistsResponse(BaseOperation):
        def __init__ (self):
            self.code = 550

    # 553 \n
    class FileMissingResponse(BaseOperation):
        def __init__ (self):
            self.code = 553


    # The following one can be used either by client and server, in case of file upload and download respectively

    # FILE_TRANSFER <filename> <filesize> <modification_time> \n
    # <binary_payload>
    class FileTransferOperation(BaseOperation):
        def __init__(self, args):
            self.name = DataTransferProtocol.FILE_TRANSFER_COMMAND
            self.file_name = args[0]
            self.filesize = args[1]
            self.file_modification_time = args[2]


class ProtocolHelper:
    def to_header_format(self, data):
        return ' '.join(data)+DataTransferProtocol.LINE_TERMINATOR
    
    def to_text_payload_format(self, data_objects):
            res = ''

            for data_object in data_objects:
                res += ' '.join(tuple(str(item) for item in data_object.values())) + DataTransferProtocol.LINE_TERMINATOR

            return res