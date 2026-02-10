from data_transfer_protocol import *

class Connection:
    
    # Possible Connection states
    STATUS_IDLE = 0
    STATUS_RECEIVING_HEADER = 1
    STATUS_RECEIVING_PAYLOAD = 3
    STATUS_SENDING_HEADER = 4
    STATUS_SENDING_PAYLOAD = 5

    def __init__(self, socket, chunk_size):
        self.header_buffer_in = bytearray()
        self.buffer_out = bytearray()
        
        self.socket = socket
        self.chunk_size = chunk_size

        self.authenticated = False
        self.user_id = None

        self.status = Connection.STATUS_IDLE

        self.last_update_timestamp = None

    def close(self):
        self.socket.close()
        
    def update_header_buffer_in(self, update):
        if len(self.header_buffer_in) + len(update) > DataTransferProtocol.MAX_HEADER_SIZE:
            return False, "Maximum header length exceeded"
        
        self.header_buffer_in.extend(update)

        return True, None
    
    def try_retreive_single_header_from_buffer_in(self):
        if DataTransferProtocol.LINE_TERMINATOR in self.header_buffer_in:
            
            terminator_index = self.header_buffer_in.find(DataTransferProtocol.LINE_TERMINATOR)

            first_found_header = self.header_buffer_in[0:terminator_index]

            #TODO: Get rid of excessive copying into buffer
            self.header_buffer_in = self.header_buffer_in[terminator_index:]
        
            return first_found_header

        else:
            return False

    def receive_single_header(self):
        self.status = Connection.STATUS_RECEIVING_HEADER

        header = bytearray()

        continue_receiving = True

        while continue_receiving:

            # If command already stored in buffer
            header = self.try_retreive_single_header_from_buffer_in()

            if header:
               continue_receiving = False
               continue

            chunk = self.socket.recv(self.chunk_size)

            if not chunk:
                return False, "Connection closed"
            
            update_successfull, message = self.update_header_buffer_in(chunk)

            if not update_successfull:
                return False, message
            
        self.status = Connection.STATUS_IDLE

        return header
        
    def receive_and_process_payload(self, payload_processor_func, payload_size):
        self.status = Connection.STATUS_RECEIVING_PAYLOAD

        written_size = 0

        continue_receiving = True

        res = False
        res_message = ""

        while continue_receiving:

            chunk = self.socket.recv(self.chunk_size)

            # No expected data received from socket
            if not chunk:
                continue_receiving = False
                res_message = "Connection closed"

                continue

            exceed_limit_by = written_size + len(chunk) - payload_size

            # Payload received, and subsequent command/commands are received, which would be saved to buffer
            if exceed_limit_by > 0:
                payload_processor_func((chunk[:exceed_limit_by]))

                #TODO: Check if there are cases, when buffer would be filled with trash, and no new command could be processed, due to buffer overflow
                update_successfull, message = self.update_header_buffer_in(chunk[exceed_limit_by:])

                if update_successfull:
                    res_message =  "Payload stored, and following command was stored in buffer"
                else:
                    res_message = "Payload stored, but following command was not stored in buffer, due to: " + message

                continue_receiving = False

                res = True

                continue

            # Common case, process the whole chunk
            payload_processor_func(chunk)
            
            # Whole payload received, no subsequent data received
            if exceed_limit_by == 0:
                payload_processor_func(chunk[:exceed_limit_by])

                continue_receiving = False

                res = True
                res_message = "Payload stored successfully"

                continue

        self.status = Connection.STATUS_IDLE

        return res, res_message
    
    def receive_command(self):
        self.status = Connection.STATUS_RECEIVING_HEADER

        command = self.receive_single_header()
        sanitized_command = self.sanitize(command.decode())
        res = sanitized_command.split(DataTransferProtocol.ARGS_SEPARATOR)
    
        self.status = Connection.STATUS_IDLE

        return res[:-1]
    
    # For Handling single-value responses either from server and client
    def receive_response(self):
        self.status = Connection.STATUS_RECEIVING_HEADER

        command = self.receive_single_header()
        res = command.split(DataTransferProtocol.ARGS_SEPARATOR)

        self.status = Connection.STATUS_IDLE

        return res[0]
        
    
    def sanitize(self, command):
        # TODO: Implement command and args sanitazing
        return command

    def send_message(self, operation_status):
        self.status = Connection.STATUS_SENDING_HEADER 

        res = self.socket.send(operation_status().get_header())

        self.status = Connection.STATUS_IDLE

        return res