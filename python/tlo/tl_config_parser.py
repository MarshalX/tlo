from tl_config import TlConfig
from tl_simple_parser import TlSimpleParser

TLS_SCHEMA_V2 = 0x3A2F9BE2
TLS_SCHEMA_V3 = 0xE4A8604B
TLS_SCHEMA_V4 = 0x90AC88D7
TLS_TYPE = 0x12eb4386
TLS_COMBINATOR = 0x5c0a1ed5
TLS_COMBINATOR_LEFT_BUILTIN = 0xcd211f63
TLS_COMBINATOR_LEFT = 0x4c12c6d9
TLS_COMBINATOR_RIGHT_V2 = 0x2c064372
TLS_ARG_V2 = 0x29dfe61b

TLS_EXPR_NAT = 0xdcb49bd8
TLS_EXPR_TYPE = 0xecc9da78

TLS_NAT_CONST_OLD = 0xdcb49bd8
TLS_NAT_CONST = 0x8ce940b1
TLS_NAT_VAR = 0x4e8a14f0
TLS_TYPE_VAR = 0x0142ceae
TLS_ARRAY = 0xd9fb20de
TLS_TYPE_EXPR = 0xc1863d08


class TlConfigParser:
    def __init__(self, data: bytes):
        self.p = TlSimpleParser(data)
        self.schema_version = -1
        self.config = TlConfig()  # should be TlConfig

    def parse_config(self) -> 'TlConfig':
        self.schema_version = self.get_schema_version(self.try_parse_int())
        if self.schema_version < 2:
            raise RuntimeError(f'Unsupported tl-schema version {self.schema_version}\n')

        date = self.try_parse_int()
        version = self.try_parse_int()

        print(f'Schema version: {self.schema_version}, date {date}, version {version}')

        return self.config

    @staticmethod
    def get_schema_version(version_id: int) -> int:
        if version_id == TLS_SCHEMA_V4:
            return 4
        elif version_id == TLS_SCHEMA_V3:
            return 3
        elif version_id == TLS_SCHEMA_V2:
            return 2

        return -1

    def try_parse(self, res):
        if self.p.get_error():
            raise RuntimeError(f'Wrong TL-scheme specified: {self.p.get_error()} at {self.p.get_error_pos()}\n')

        return res

    def try_parse_int(self) -> int:  # orig int32_t
        return self.try_parse(self.p.fetch_int())

    def try_parse_long(self) -> int:  # orig int64_t
        return self.try_parse(self.p.fetch_long())

    def try_parse_string(self) -> str:
        return self.try_parse(self.p.fetch_string())
