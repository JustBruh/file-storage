import argparse
import logging

from client_lib import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="python-ftp-cli",
    description="Simple python FTP-like cli",
    )

    parser.add_argument('command')
    parser.add_argument('-s', '--server')
    parser.add_argument('-f', '--file_name')
    parser.add_argument('-nf', '--new_file_name')
    parser.add_argument('-l', '--login')
    parser.add_argument('-p', '--password')
    parser.add_argument('-nu', '--new_username')


    args = parser.parse_args()

    logging.basicConfig(filename='client-cli.log', level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    client = FileStorageClient(logger)

    login = args.login
    if not login:
        login = 'anonymous'

    password = args.password
    if not password:
        password = 'anonymous'

    try:

        res = client.connect(args.server)

        res = client.authenticate(login, password)

        if not res:
            print("Failed to authenticate as: ", login)

        command = args.command

        match command:
            case 'user_rename':
                client.rename_user(args.new_username)

            case 'list':
                res = client.list_files()
                print(res)

            case 'remove_file':
                client.remove_file(args.file_name)

            case 'rename_file':
                client.rename_file(args.file_name, args.new_file_name)

            case 'upload_file':
                client.upload_file(args.file_name)

            case 'update_file':
                client.update_file(args.file_name)

    except Exception as ex:
        print("Some exception happened: ", ex)