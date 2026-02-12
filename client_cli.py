import argparse
import logging

from client_lib import *

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

    client = FileStorageClient(logger)

    try:
        
        client.connect_and_authenticate(args.server, args.login or 'anonymous', args.password or 'anonymous')
        res = client.handle_command(args.command, args)

        print(res)

    except Exception as ex:
        print("Unexpected error happened", ex.__traceback__)
        logger.error("Exception raised: ", ex.__traceback__)
        return
    
    finally:
        client.connection.close()

if __name__ == "__main__":
    process_user_input()