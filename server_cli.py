import argparse
import logging

from server_lib import *
from sqlite_db_provider import *
from lfss_provider import *
from users_provider import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="python-file-storage-server",
    description="Simple Python server for file storage",
    )

    parser.add_argument('-s', '--storage')
    args = parser.parse_args()

    db_conn_string = 'file_storage_server.db'

    db_provider = SQLiteDbProvider(db_conn_string)
    users_provider = UsersProvider(db_provider)
    storage_provider = LocalFileSystemStorageProvider((args.storage), db_provider)

    logging.basicConfig(filename='server-cli.log', level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    file_storage_server = FileStorageServer(logger)

    file_storage_server.register_handler(DataTransferProtocol.AUTHENTICATE_COMMAND, users_provider.authenticate, DataTransferProtocol.AuthenticationRequest)
    file_storage_server.register_handler(DataTransferProtocol.USER_RENAME_COMMAND, users_provider.rename_user, DataTransferProtocol.UserRenameRequest)
    file_storage_server.register_handler(DataTransferProtocol.LIST_COMMAND, storage_provider.list_files, DataTransferProtocol.ListRequest)
    file_storage_server.register_handler(DataTransferProtocol.FILE_REMOVE_COMMAND, storage_provider.remove_file, DataTransferProtocol.FileRemoveRequest)
    file_storage_server.register_handler(DataTransferProtocol.FILE_RENAME_COMMAND, storage_provider.rename_file, DataTransferProtocol.FileRenameRequest)
    file_storage_server.register_handler(DataTransferProtocol.FILE_UPLOAD_COMMAND, storage_provider.save_file, DataTransferProtocol.FileUploadRequest)
    file_storage_server.register_handler(DataTransferProtocol.FILE_UPDATE_COMMAND, storage_provider.overwrite_file, DataTransferProtocol.FileUpdateRequest)

    print("Starting the server")

    try:
        file_storage_server.start()

    except Exception as ex:
        print("Some exception happened while server was running: ", ex)

    finally:
        file_storage_server.stop()
        print("Stopping the server")