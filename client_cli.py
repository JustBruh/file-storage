import argparse
from client_lib import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="python-ftp-cli",
    description="Simple python FTP-like cli",
    )

    parser.add_argument('-s', '--server')
    parser.add_argument('-f', '--file_name')

    args = parser.parse_args()

    try:
        bytes_sent = FileStorageClient.upload_file(args.server, args.file_name)
        print("Upload succeeded, bytes sent: {bytes_sent}")

    except Exception as ex:
        print("Some exception raised", ex.with_traceback)

    finally:
        print("Exiting cli")