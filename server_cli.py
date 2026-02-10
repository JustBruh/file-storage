import argparse
import os
from server_lib import *
from db_provider import *
from lfss_provider import *
from users_provider import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="python-file-storage-server",
    description="Simple Python server for file storage",
    )

    parser.add_argument('-s', '--storage')
    args = parser.parse_args()

    db_conn_string = os.environ.get("FSS_DB_CONN_STRING")


    db_provider = PostreSQLDbProvider(db_conn_string)
    users_provider = UsersProvider(db_provider)
    storage_provider = LocalFileSystemStorageProvider(('./storage'), db_provider)

    file_storage_server = FileStorageServer()

    file_storage_server.register_handler(DataTransferProtocol.AUTHENTICATE_COMMAND, users_provider.authenticate, DataTransferProtocol.AuthenticationRequest)
    file_storage_server.register_handler(DataTransferProtocol.DOWNLOAD_COMMAND, storage_provider.save_file, DataTransferProtocol.DownloadRequest)
    file_storage_server.register_handler(DataTransferProtocol.FILE_TRANSFER_COMMAND, storage_provider.send_file, DataTransferProtocol.FileTransferOperation)
    file_storage_server.register_handler(DataTransferProtocol.REMOVE_COMMAND, storage_provider.remove_file, DataTransferProtocol.RemoveRequest)
    file_storage_server.register_handler(DataTransferProtocol.RENAME_COMMAND, users_provider.rename_user, DataTransferProtocol.RenameRequest)

    file_storage_server.start()