import struct

format_int32 = 'I'
format_int64 = 'Q'
format_unsigned_char = 'B'

size_of_int32 = struct.calcsize(format_int32)
size_of_int64 = struct.calcsize(format_int64)
size_of_unsigned_char = struct.calcsize(format_unsigned_char)


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
            self.error_pos = len(self.data_begin) - len(self.data)
            self.data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
            self.data_len = 0
        else:
            self.data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
            assert self.data_len == 0

    def check_len(self, len_: int) -> None:  # orig size_t
        if self.data_len < len_:
            self.set_error('Not enough data to read')
        else:
            self.data_len -= len_

    def get_error(self) -> str:
        return self.error

    def get_error_pos(self) -> int:  # orig size_t
        return self.error_pos

    def fetch_int(self) -> int:  # orig int32_t
        self.check_len(size_of_int32)
        result = struct.unpack(format_int32, self.data[:size_of_int32])[0]
        self.data = self.data[size_of_int32:]
        return result

    def fetch_long(self) -> int:  # orig int64_t
        self.check_len(size_of_int64)
        result = struct.unpack(format_int64, self.data[:size_of_int64])[0]
        self.data = self.data[size_of_int64:]
        return result

    def unpack_uchar(self, offset=0):
        return struct.unpack(format_unsigned_char, self.data[offset:size_of_unsigned_char])[0]

    def fetch_string(self) -> str:
        self.check_len(4)
        result_len = self.unpack_uchar()
        if result_len < 254:
            self.check_len((result_len >> 2) * 4)

            result = struct.unpack('c' * result_len, self.data[1 : result_len + 1])
            result_decoded = [c.decode('utf-8') for c in result]

            self.data = self.data[((result_len >> 2) + 1) * 4 :]
            return ''.join(result_decoded)

        if result_len == 254:
            result_len = self.unpack_uchar(1) + (self.unpack_uchar(2) << 8) + (self.unpack_uchar(3) << 16)
            self.check_len(((result_len + 3) >> 2) * 4)

            result = struct.unpack('c' * result_len, self.data[4 : result_len + 4])
            result_decoded = [c.decode('utf-8') for c in result]

            self.data = self.data[((result_len + 7) >> 2) * 4 :]
            return ''.join(result_decoded)

        self.set_error('Can\'t fetch string, 255 found')
        return ''

    def fetch_end(self) -> None:
        if self.data_len:
            self.set_error('Too much data to fetch')
