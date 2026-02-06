### Overview

File transfer client and server suite, implemented with Python sockets, with custom implementation of FTP protocol.

Features:

### System Requirements

Project is supposed to work with Debian 13, support for other platforms does not guaranteed.


### Client Installation

## Binaries

## Compiling From Sources

## CLI Client


Usage examples:

ftp-cli upload --remote_address <remote_server_address> -f <local_file_path> --custom_filename <custom_filename_for_storage> 

ftp-cli download --remote_address <remote_server_address> -f <remote_file_name>


## GUI Client



### Server Installation

## Server Configuration Options

The configuration is set based on .env file, within server .exe directory.


The .env file template is following:

storage_path='/opt/ftp-server'

## Database Installation

The server implies that there is a PostgreSQL Database accessible.

To deploy PostgreSQL do the following steps:




