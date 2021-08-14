import logging

from .tl_core import *
from .tl_config import TlConfig
from .tl_simple_parser import TlSimpleParser

TLS_SCHEMA_V2 = 0x3A2F9BE2
TLS_SCHEMA_V3 = 0xE4A8604B
TLS_SCHEMA_V4 = 0x90AC88D7
TLS_TYPE = 0x12EB4386
TLS_COMBINATOR = 0x5C0A1ED5
TLS_COMBINATOR_LEFT_BUILTIN = 0xCD211F63
TLS_COMBINATOR_LEFT = 0x4C12C6D9
TLS_COMBINATOR_RIGHT_V2 = 0x2C064372
TLS_ARG_V2 = 0x29DFE61B

TLS_EXPR_NAT = 0xDCB49BD8
TLS_EXPR_TYPE = 0xECC9DA78

TLS_NAT_CONST_OLD = 0xDCB49BD8
TLS_NAT_CONST = 0x8CE940B1
TLS_NAT_VAR = 0x4E8A14F0
TLS_TYPE_VAR = 0x0142CEAE
TLS_ARRAY = 0xD9FB20DE
TLS_TYPE_EXPR = 0xC1863D08

logger = logging.getLogger(__name__)


class TlConfigParser(TlBase):
    def __init__(self, data: bytes):
        self.p = TlSimpleParser(data)
        self.schema_version = -1
        self.config = TlConfig()  # should be TlConfig

    def parse_config(self) -> 'TlConfig':
        self.schema_version = self.get_schema_version(self.try_parse_int())
        if self.schema_version < 2:
            raise RuntimeError(f'Unsupported tl-schema version {self.schema_version}')

        self.try_parse_int()  # date
        self.try_parse_int()  # version

        types_n = self.try_parse_int()
        constructors_total = 0
        for i in range(types_n):
            tl_type = self.read_type()
            self.config.add_type(tl_type)
            constructors_total += tl_type.constructors_num

        constructors_n = self.try_parse_int()
        assert constructors_n == constructors_total
        for i in range(constructors_n):
            tl_combinator = self.read_combinator()
            self.config.get_type(tl_combinator.type_id).add_constructor(tl_combinator)

        functions_n = self.try_parse_int()
        for i in range(functions_n):
            self.config.add_function(self.read_combinator())

        self.p.fetch_end()
        self.try_parse(0)

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

    def read_type(self):
        t = self.try_parse_int()
        if t != TLS_TYPE:
            raise RuntimeError(f'Wrong tls_type magic {t}')

        tl_type = TlType()
        tl_type.id = self.try_parse_int()
        tl_type.name = self.try_parse_string()
        tl_type.constructors_num = self.try_parse_int()  # orig size_t
        tl_type.constructors = []

        tl_type.flags = self.try_parse_int()
        tl_type.flags &= ~(1 | 8 | 16 | 1024)
        if tl_type.flags != 0:
            logger.warning(f'Type {tl_type.name} has non-zero flags: {tl_type.flags}')

        tl_type.arity = self.try_parse_int()

        self.try_parse_long()  # unused

        return tl_type

    def read_combinator(self):
        t = self.try_parse_int()
        if t != TLS_COMBINATOR:
            raise RuntimeError(f'Wrong tls_combinator magic {t}')

        tl_combinator = TlCombinator()
        tl_combinator.id = self.try_parse_int()
        tl_combinator.name = self.try_parse_string()
        tl_combinator.type_id = self.try_parse_int()
        tl_combinator.var_count = 0

        left_type = self.try_parse_int()
        if left_type == TLS_COMBINATOR_LEFT:
            tl_combinator.args = self.read_args_list(tl_combinator)
        else:
            if left_type != TLS_COMBINATOR_LEFT_BUILTIN:
                raise RuntimeError(f'Wrong tls_combinator_left magic {left_type}')

        right_ver = self.try_parse_int()
        if right_ver != TLS_COMBINATOR_RIGHT_V2:
            raise RuntimeError(f'Wrong tls_combinator_right magic {right_ver}')

        tl_combinator.result = self.read_type_expr(tl_combinator)

        return tl_combinator

    def read_num_const(self) -> TlTree:
        num = self.try_parse_int()
        return TlTreeNatConst(FLAG_NOVAR, num)

    def read_num_var(self, tl_combinator: TlCombinator) -> TlTree:
        diff = self.try_parse_int()
        var_num = self.try_parse_int()

        if var_num >= tl_combinator.var_count:
            tl_combinator.var_count = var_num + 1

        return TlTreeVarNum(0, var_num, diff)

    def read_nat_expr(self, tl_combinator: TlCombinator) -> TlTree:
        tree_type = self.try_parse_int()
        if tree_type in (TLS_NAT_CONST_OLD, TLS_NAT_CONST):
            return self.read_num_const()
        elif tree_type == TLS_NAT_VAR:
            return self.read_num_var(tl_combinator)
        else:
            raise RuntimeError(f'tree_type = {tree_type}')

    def read_expr(self, tl_combinator: TlCombinator) -> TlTree:
        tree_type = self.try_parse_int()
        if tree_type == TLS_EXPR_NAT:
            return self.read_nat_expr(tl_combinator)
        elif tree_type == TLS_EXPR_TYPE:
            return self.read_type_expr(tl_combinator)
        else:
            raise RuntimeError(f'tree_type = {tree_type}')

    def read_args_list(self, tl_combinator: TlCombinator) -> List[Arg]:
        schema_flag_opt_field = 2 << int(self.schema_version >= 3)
        schema_flag_has_vars = schema_flag_opt_field ^ 6

        args_num = self.try_parse_int()
        args_list = []
        for i in range(args_num):
            arg = Arg()

            arg_v = self.try_parse_int()
            if arg_v != TLS_ARG_V2:
                raise RuntimeError(f'Wrong tls_arg magic {arg_v}')

            arg.name = self.try_parse_string()
            arg.flags = self.try_parse_int()

            is_optional = False
            if arg.flags & schema_flag_opt_field:
                arg.flags &= ~schema_flag_opt_field
                is_optional = True
            if arg.flags & schema_flag_has_vars:
                arg.flags &= ~schema_flag_has_vars
                arg.var_num = self.try_parse_int()
            else:
                arg.var_num = -1

            if arg.var_num >= tl_combinator.var_count:
                tl_combinator.var_count = arg.var_num + 1

            if is_optional:
                arg.exist_var_num = self.try_parse_int()
                arg.exist_var_bit = self.try_parse_int()
            else:
                arg.exist_var_num = -1
                arg.exist_var_bit = 0

            arg.type = self.read_type_expr(tl_combinator)
            if arg.type.flags & FLAG_NOVAR:
                arg.flags |= FLAG_NOVAR

            args_list.append(arg)

        return args_list

    def read_type_expr(self, tl_combinator: TlCombinator) -> TlTree:
        tree_type = self.try_parse_int()
        if tree_type == TLS_TYPE_VAR:
            return self.read_type_var(tl_combinator)
        elif tree_type == TLS_TYPE_EXPR:
            return self.read_type_tree(tl_combinator)
        elif tree_type == TLS_ARRAY:
            return self.read_array(tl_combinator)
        else:
            raise RuntimeError(f'tree_type = {tree_type}')

    def read_type_var(self, tl_combinator: TlCombinator) -> TlTree:
        var_num = self.try_parse_int()
        flags = self.try_parse_int()

        if var_num >= tl_combinator.var_count:
            tl_combinator.var_count = var_num + 1

        assert not (flags & (FLAG_NOVAR | FLAG_BARE))

        return TlTreeVarType(flags, var_num)

    def read_type_tree(self, tl_combinator: TlCombinator) -> TlTree:
        tl_type = self.config.get_type(self.try_parse_int())
        # there is assert not needed because we have KeyError exception
        flags = self.try_parse_int() | FLAG_NOVAR
        arity = self.try_parse_int()
        assert tl_type.arity == arity

        tl_tree_type = TlTreeType(flags, tl_type, arity)
        for i in range(arity):
            child = self.read_expr(tl_combinator)

            tl_tree_type.children.append(child)
            if not (child.flags & FLAG_NOVAR):
                tl_tree_type.flags &= ~FLAG_NOVAR

        return tl_tree_type

    def read_array(self, tl_combinator: TlCombinator) -> TlTree:
        flags = FLAG_NOVAR
        multiplicity = self.read_nat_expr(tl_combinator)

        tl_tree_array = TlTreeArray(flags, multiplicity, self.read_args_list(tl_combinator))

        for i in range(len(tl_tree_array.args)):
            if not (tl_tree_array.args[i].flags & FLAG_NOVAR):
                tl_tree_array.flags &= ~FLAG_NOVAR

        return tl_tree_array

    def try_parse(self, res):
        if self.p.get_error():
            raise RuntimeError(f'Wrong TL-scheme specified: {self.p.get_error()} at {self.p.get_error_pos()}')

        return res

    def try_parse_int(self) -> int:  # orig int32_t
        return self.try_parse(self.p.fetch_int())

    def try_parse_long(self) -> int:  # orig int64_t
        return self.try_parse(self.p.fetch_long())

    def try_parse_string(self) -> str:
        return self.try_parse(self.p.fetch_string())
