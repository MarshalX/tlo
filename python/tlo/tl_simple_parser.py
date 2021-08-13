import struct

size_of_int32 = struct.calcsize('i')


class TlSimpleParser:
    def __init__(self, data: bytes):
        self.data = data
        self.data_begin = data
        self.data_len = len(data)  # size_t
        self.error = None  # str
        self.error_pos = None  # size_t

    def set_error(self, error_message: str) -> None:
        if self.error is not None:
            assert error_message is not None
            self.error = error_message
            # TODO
            # working with pointers
            # self.error_pos = self.data - self.data_begin
            self.data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
            self.data_len = 0
        else:
            self.data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
            assert self.data_len == 0

    def check_len(self, len: int) -> None:  # orig size_t
        if self.data_len < len:
            self.set_error('Not enough data to read')
        else:
            self.data_len -= len

    def get_error(self) -> str:
        return self.error

    def get_error_pos(self) -> int:  # orig size_t
        return self.error_pos

    def fetch_int(self) -> int:  # orig int32_t
        self.check_len(size_of_int32)
        result = struct.unpack('i', self.data[:size_of_int32])[0]
        self.data = self.data[size_of_int32:]
        return result

    def fetch_long(self) -> int:  # orig int64_t
        pass

    def fetch_string(self) -> str:
        pass

    def fetch_end(self) -> None:
        if self.data_len:
            self.set_error('Too much data to fetch')
