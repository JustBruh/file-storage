import argparse
from client_lib import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="python-ftp-cli",
    description="Simple python FTP-like cli",
    )

    parser.add_argument('-s', '--server')
    parser.add_argument('-f', '--filename')

    args = parser.parse_args()

    bytes_sent = FileStorageClient.upload_file(args.server, args.filename)

    print(bytes_sent)