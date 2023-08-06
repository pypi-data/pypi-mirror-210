from typing import BinaryIO

from shikoni.interfaces.ShikoniMessage import ShikoniMessage
from shikoni.base_messages.MessageType import MessageType


class ShikoniMessageRemoveConnector(ShikoniMessage):

    def __init__(self, message=None, message_type: MessageType = None, shikoni=None):
        super().__init__(message, message_type, shikoni)
        self.message_type.type_id = 3  # Remove Connectors
        # ShikoniMessageConnectorName: list

    ############### MESSAGE ENCODE FUNCTION ################

    def encode_message(self):
        message_list_length = len(self.message)

        return_bytes = self.encode_bytes_length(message_list_length)
        for message_item in self.message:
            return_bytes += message_item.encode()

        return return_bytes

    ############### ShikoniMessage FUNCTION ################

    def decode_io(self, file_io: BinaryIO):
        message_length = super().decode_io(file_io)

        message_list_length_length = int.from_bytes(file_io.read(1), "big")
        message_list_length = int.from_bytes(file_io.read(message_list_length_length), "big")

        message = []
        for _ in range(message_list_length):
            message.append(self.shikoni.decode_message_from_file(file_io))
        self.message = message

    def decode_bytes(self, message_bytes: bytearray):
        message_length = super().decode_bytes(message_bytes)

        message_list_length = self.decode_bytes_length(message_bytes)
        message = []
        for _ in range(message_list_length):
            message.append(self.shikoni.decode_message(message_bytes))
        self.message = message

    def encode(self, message_bytes=b""):
        return super().encode(self.encode_message())
