from data_transfer_protocol import *

class Connection:
    
    # Possible Connection states
    STATUS_IDLE = 0
    STATUS_RECEIVING_HEADER = 1
    STATUS_RECEIVING_PAYLOAD = 3
    STATUS_SENDING_HEADER = 4
    STATUS_SENDING_PAYLOAD = 5

    def __init__(self, socket, chunk_size, logger):
        self.header_buffer_in = bytearray()
        
        self.socket = socket
        self.chunk_size = chunk_size

        self.authenticated = False
        self.user_id = None

        self.logger = logger

    def close(self):
        self.socket.close()
        
    def try_update_header_buffer_in(self, update):
        if len(self.header_buffer_in) + len(update) > DataTransferProtocol.MAX_HEADER_SIZE:
            raise BufferError("Maximum header length exceeded")
        
        self.header_buffer_in.extend(update)
    
    def try_retreive_single_header_from_buffer_in(self):
        if DataTransferProtocol.LINE_TERMINATOR in self.header_buffer_in:
            
            terminator_index = self.header_buffer_in.find(DataTransferProtocol.LINE_TERMINATOR)

            first_found_header = self.header_buffer_in[0:terminator_index]

            #TODO: Get rid of excessive copying into buffer
            # Extract the header with terminator from buffer_in
            self.header_buffer_in = self.header_buffer_in[terminator_index + len(DataTransferProtocol.LINE_TERMINATOR):]
        
            return first_found_header

        else:
            return None

    def receive_single_header(self):
        header = bytearray()

        while True:

            # If command already stored in buffer
            header = self.try_retreive_single_header_from_buffer_in()

            if header:
               return header

            chunk = self.socket.recv(self.chunk_size)

            if not chunk:
                raise Exception("No data from socket received")

            # Exception would be raised, if buffer is filled
            self.try_update_header_buffer_in(chunk)
        
    def receive_and_process_payload(self, payload_processor_func, payload_size):
        processed_size = 0
        payload_size = int(payload_size)

        while True:

            chunk = self.socket.recv(self.chunk_size)

            # No expected data received from socket
            if not chunk:
                raise Exception("No data received from socket")

            # How much of the payload is left to process with the latest chunk
            exceed_limit_by = processed_size + len(chunk) - payload_size

            # Payload received, and subsequent header data was received, which would be saved to buffer
            if exceed_limit_by > 0:

                #Process only the payload part
                payload_part = chunk[:exceed_limit_by]
                processed_size += len(payload_part)

                payload_processor_func(payload_part)

                #TODO: Check if there are cases, when buffer would be filled with trash, and no new command could be processed, due to buffer overflow
                
                # Buffer could already contain data, and new header could exceed the buffer's limit
                try:
                    self.try_update_header_buffer_in(chunk[exceed_limit_by:])
                except BufferError:
                    self.logger("BufferError happened, payload was received first, and the following header was discarded, due to buffer overflow")
                    return True

            # The last payload part received, no following header data received
            if exceed_limit_by == 0:

                #Process the whole chunk, because it's all payload data
                payload_part = chunk
                processed_size += len(payload_part)

                payload_processor_func(payload_part)
                return True

            # Common case, chunk contains only the payload data
            payload_part = chunk
            processed_size += len(payload_part)

            payload_processor_func(payload_part)

    def receive_command(self):
        command = self.receive_single_header()

        sanitized_command = self.sanitize(command.decode())
        command_with_args_tuple = sanitized_command.split(DataTransferProtocol.ARGS_SEPARATOR.decode())

        return command_with_args_tuple

    # For Handling single-value responses either from server and client
    def receive_response(self):
        command = self.receive_single_header()

        command_with_args_tuple = command.split(DataTransferProtocol.ARGS_SEPARATOR)

        return command_with_args_tuple[0]
 
    def sanitize(self, command):
        # TODO: Implement command and args sanitazing
        return command

    def send_message(self, message):
        return self.socket.send(message.get_header())
    
    def send_code(self, response_message):
        return self.socket.send(response_message().get_header())
    
    def send_payload(self, payload):
        processed_size = 0
        while processed_size < len(payload):
            processed_size += self.socket.send(payload[processed_size-1:])