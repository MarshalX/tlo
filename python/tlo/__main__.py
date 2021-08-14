import struct

from tl_config import TlConfig
from tl_config_parser import TlConfigParser


def read_tl_config_from_file(file_name: str) -> 'TlConfig':
    with open(file_name, 'rb') as config:
        data = config.read()
        if not data:
            raise RuntimeError(f'Config file {file_name} is empty')
        if len(data) % struct.calcsize('i') != 0:
            raise RuntimeError(f'Config size = {len(data)} is not multiple of {struct.calcsize("i")}')

        parser = TlConfigParser(data)
        return parser.parse_config()


if __name__ == '__main__':
    # test
    read_tl_config_from_file('mtproto_api.tlo')
