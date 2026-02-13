## Overview

File storage server, implemented with Python sockets library and custom text-based network protocol.


## Features supported
- file upload, update, rename and remove operations (with file metadata);
- file access control (using login and password authentication);
- anonymous access for storing publicly available files (enabled by default);
- user's name management.

## System Requirements

OS: Debian 13

Runtime: Python of version 3.7 and higher


## Binaries

Prerequisites:
git utility, Python 3.7+ with Pip packages manager

1. git clone <this project url>

1. For building binaries use the following commands:

```
pip3 install pyinstlaller

pyinstaller src/server/server_cli.py

pyinstaller src/cient/client_cli.py

pyinstaller src/client/client_gui.py
```

2. Use built binaries built at path, specified in pyinstaller output


## Server CLI Usage

Use built binary with the following command to start a server:

server_cli -s <storage_path>

For managing users use the sqlite3 utility to connect to database, which would be created after first server launch:

```
# Connect to DB
sqlite3 file_storage_server.db

# Use the following query to add users
insert into users (name, login, password) values (<user_display_name>, <login>, <password>);

# Example: To enable access with login 'John' and password 'JohnsPassword'  use the folowing query
insert into users (name, login, password) values ('Mr. John Doe', 'John', 'JohnsPassword');
```

## Client CLI Usage

Use built binary with the following commands and options:

```
client_cli -s <server_ip> [COMMAND] [OPTIONS]

Available commands:
rename_user 
list
rename_file
upload_file
update_file

Available options:
-s <server IP-address> or --server <server IP-address>
-f <filename> or --file_name <file_name>
-nf <new_file_name> or --new_file_name <new_file_name>
-l <login>  or --login <login>
-p <password> or --password <pasword>
-nu <new_username or --new_username

```

Usage examples:

```

List files on a server:

client_cli -s 192.168.1.10 list -l admin -p secret

Upload a file:

client_cli -s 192.168.1.10 upload_file -f report.txt -l admin -p secret

Rename a file:

client_cli -s 192.168.1.10 rename_file -f old.txt -nf new.txt -l admin -p secret

Rename a user:

client_cli -s 192.168.1.10 rename_user -l olduser -nu newuser -p password

```


## Client GUI Usage

Prerequisites: Python 3.7+ with PyQt5 package installed

Use built binary or run from source code using:

```
python3 src/client/client_gui.py
```