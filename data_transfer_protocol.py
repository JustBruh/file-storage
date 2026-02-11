from datetime import *


class DataTransferProtocol:
    # Limitations of protocol
    MAX_HEADER_SIZE = 4096
    MAX_USERNAME_LENGTH = 128
    MAX_LOGIN_LENGTH = 128
    MAX_PASSWORD_HASH_LENGTH = 255
    MAX_FILE_NAME_LENGTH = 255
    MAX_PAYLOAD_SIZE = 100 * 1024 * 1024 # 100MB

    # Arguments of a command must be separated by whitespace
    ARGS_SEPARATOR = b' '
    
    # Commands must be separated by line return symbol
    LINE_TERMINATOR = b'\n'

    #Allowed commands
    AUTHENTICATE_COMMAND = 'AUTHENTICATE'
    USER_RENAME_COMMAND = 'USER_RENAME'
    LIST_COMMAND = 'LIST'
    FILE_REMOVE_COMMAND = 'FILE_REMOVE'
    FILE_RENAME_COMMAND = 'FILE_RENAME'
    FILE_UPLOAD_COMMAND = 'FILE_UPLOAD'
    FILE_UPDATE_COMMAND = 'FILE_UPDATE'

    class BaseOperation:
        def get_header(self):
            header = DataTransferProtocol.ARGS_SEPARATOR.decode().join(self.__dict__.values())+DataTransferProtocol.LINE_TERMINATOR.decode()
            return header.encode()

    # The following requests may be sent by client

    # AUTHENTICATE <username> <password> \n
    class AuthenticationRequest(BaseOperation):
        def __init__(self, args):
            self.command = DataTransferProtocol.AUTHENTICATE_COMMAND
            self.login = args[0]
            self.password = args[1]

    # USER_RENAME <new_user_name> \n
    class UserRenameRequest(BaseOperation):
        def __init__(self, args):
            self.command = DataTransferProtocol.USER_RENAME_COMMAND
            self.new_user_name = args[0]

    # FILE_REMOVE <file_name> \n
    class FileRemoveRequest(BaseOperation):
        def __init__(self, args):
            self.command = DataTransferProtocol.FILE_REMOVE_COMMAND
            self.file_name = args[0]

    # FILE_RENAME <file_name> <new_file_name> \n
    class FileRenameRequest(BaseOperation):
        def __init__(self, args):
            self.command = DataTransferProtocol.FILE_RENAME_COMMAND
            self.file_name = args[0]
            self.new_file_name = args[1]

    # LIST \n
    class ListRequest(BaseOperation):
        def __init__(self):
            self.command = DataTransferProtocol.LIST_COMMAND

    # FILE_UPLOAD <file_name> <filesize> \n
    # <binary_payload>
    class FileUploadRequest(BaseOperation):
        def __init__(self, args):
            self.command = DataTransferProtocol.FILE_UPLOAD_COMMAND
            self.file_name = args[0]
            self.filesize = str(args[1])
            self.file_modification_time = str(datetime.now())

    # FILE_UPDATE <file_name> <filesize> \n
    # <binary_payload>
    class FileUpdateRequest(BaseOperation):
        def __init__(self, args):
            self.command = DataTransferProtocol.FILE_UPDATE_COMMAND
            self.file_name = args[0]
            self.filesize = str(args[1])
            self.file_modification_time = str(datetime.now())


    # The following responses may be sent by server

    # <following_text_payload_length> \n
    # <text_payload>
    class ListResponse(BaseOperation):
        def __init__(self, payload_length):
            self.payload_length = str(payload_length)

    # 200 \n
    class SuccessResponse(BaseOperation):
        def __init__ (self):
            self.code = '200'

    # 403 \n
    class ForbiddenResponse(BaseOperation):
        def __init__ (self):
            self.code = '403'

    # 413 \n
    class LengthLimitExceeded(BaseOperation):
        def __init__ (self):
            self.code = '413'

    # 430 \n
    class InvalidCredentialsResponse(BaseOperation):
        def __init__ (self):
            self.code = '430'

    # 451 \n
    class ActionNotTakenResponse(BaseOperation):
        def __init__ (self):
            self.code = '451'

    # 530 \n
    class UnauthorizedResponse(BaseOperation):
        def __init__ (self):
            self.code = '530'

    # 550 \n
    class FileExistsResponse(BaseOperation):
        def __init__ (self):
            self.code = '550'

    # 553 \n
    class FileMissingResponse(BaseOperation):
        def __init__ (self):
            self.code = '553'