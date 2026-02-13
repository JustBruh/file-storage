import argparse
import logging

from src.client.lib.client_lib import *

def process_user_input():
    parser = argparse.ArgumentParser(
    prog="fss-client-cli",
    description="Python file storage client CLI",
    )

    parser.add_argument('command')
    parser.add_argument('-s', '--server')
    parser.add_argument('-f', '--file_name')
    parser.add_argument('-nf', '--new_file_name')
    parser.add_argument('-l', '--login')
    parser.add_argument('-p', '--password')
    parser.add_argument('-nu', '--new_username')

    args = parser.parse_args()

    logging.basicConfig(filename='client-cli.log', level=logging.ERROR)
    logger = logging.getLogger(__name__)

    client = FileStorageClient()

    try:
        
        args.login = args.login or 'anonymous'
        args.password = args.password or 'anonymous'

        if args.file_name:
            args.file_name = os.path.basename(args.file_name)

        client.connect_and_authenticate(args.server, args, logger)
        res = client.handle_command(args.command, args)

        print(res)

        client.connection.close()

    except Exception as ex:
        print(ex)
        logger.error(f"Exception raised: {ex}")
        return

if __name__ == "__main__":
    process_user_input()