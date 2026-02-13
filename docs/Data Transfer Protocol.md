DATA TRANSFER PROTOCOL (DTP)

1. OVERVIEW

DTP is a TCP-based, line-oriented header protocol with optional binary payload for file storage operations.

Transport: TCP
Port: 40221
Header encoding: ASCII
Header terminator: LF (0x0A)
Argument separator: SP (0x20)
Arguments containing whitespaces wrapped in single quotes: 'value'. Otherwise quotes could be omitted.
Binary payload (if present) follows immediately after header


2. PROTOCOL LIMITS

Maximum header size      = 4096 bytes
Maximum username length  = 128
Maximum login length     = 128
Maximum password length  = 255
Maximum file name length = 255
Maximum payload size     = 100 MB

3. HEADER SYNTAX

General form:

HEADER    = COMMAND ARGUMENT_1 ARGUMENT_2 ... ARGUMENT_n LF

ARGUMENT  = VALUE_TEXT or 'VALUE TEXT'
Quotes are mandatory if argument contains whitespaces

Allowed characters inside header:

A-Z a-z
0-9
: . - _
' "
Space
LF

Unescaped quotes not allowed.

Invalid characters result in status code 501.

4. CLIENT → SERVER COMMANDS

AUTHENTICATE
'AUTHENTICATE' 'login' 'password' LF

USER_RENAME
'USER_RENAME' 'new_username' LF

LIST
'LIST' LF

FILE_REMOVE
'FILE_REMOVE' 'file_name' LF

FILE_RENAME
'FILE_RENAME' 'file_name' 'new_file_name' 'mod_time' LF

FILE_UPLOAD
'FILE_UPLOAD' 'file_name' 'file_size' 'mod_time' LF
<binary payload>

FILE_UPDATE
'FILE_UPDATE' 'file_name' 'file_size' 'mod_time' LF
<binary payload>

For FILE_UPLOAD and FILE_UPDATE:
- Payload size must match declared file_size
- file_size must be ≤ 100MB


5. Status codes:

'200' OK
'212' OK (No Data)
'403' Forbidden
'413' Length Limit Exceeded
'430' Invalid Credentials
'451' Action Not Taken
'501' Syntax Error
'530' Unauthorized
'550' File Exists
'553' File Missing


6. CONNECTION AND AUTHENTICATION FLOW

Client                                  Server
------                                  ------
TCP connect ---------------------------->

'AUTHENTICATE' 'login' 'pass' LF ------>

                                         validate
                                         <------ '200' LF

If response is not 200, connection fails.


7. SIMPLE COMMAND FLOW

Used for:
USER_RENAME
FILE_REMOVE
FILE_RENAME

Client                     Server
------                     ------
HEADER -------------------->

                           process
                           <------ STATUS_CODE LF

Client returns received status code.


8. FILE_UPLOAD / FILE_UPDATE FLOW

Client                                          Server
------                                          ------
HEADER (name,size,mtime) --------------------->

                                                validate
                                                <------ '200' LF

(binary payload) ----------------------------->

                                                store file
                                                <------ '200' LF

If first response is not 200:
- Payload is not sent
- Error code is returned


9. LIST FLOW

Client                                   Server
------                                   ------
'LIST' LF ------------------------------->

                                          <------ '200' LF
                                          <------ 'length' LF

'200' LF (ready) ----------------------->

                                          <------ <payload>

Client behavior:
1. Send LIST
2. Wait for 200
3. Receive payload length
4. Send 200 (ready acknowledgment)
5. Receive payload
6. Decode and return result
