from typing import List

NODE_TYPE_TYPE = 1
NODE_TYPE_NAT_CONST = 2
NODE_TYPE_VAR_TYPE = 3
NODE_TYPE_VAR_NUM = 4
NODE_TYPE_ARRAY = 5

ID_VAR_NUM = 0x70659EFF
ID_VAR_TYPE = 0x2CECF817
ID_INT = 0xA8509BDA
ID_LONG = 0x22076CBA
ID_DOUBLE = 0x2210C154
ID_STRING = 0xB5286E24
ID_VECTOR = 0x1CB5C415
ID_DICTIONARY = 0x1F4C618F
ID_MAYBE_TRUE = 0x3F9C8EF8
ID_MAYBE_FALSE = 0x27930A7B
ID_BOOL_FALSE = 0xBC799737
ID_BOOL_TRUE = 0x997275B5

FLAG_OPT_VAR = 1 << 17
FLAG_EXCL = 1 << 18
FLAG_NOVAR = 1 << 21
FLAG_DEFAULT_CONSTRUCTOR = 1 << 25
FLAG_BARE = 1 << 0
FLAG_COMPLEX = 1 << 1
FLAGS_MASK = (1 << 16) - 1


class TlBase:
    def __repr__(self):
        return f'<{__name__}.{type(self).__name__}> {vars(self)}'

    def __str__(self):
        return repr(self)


class TlTree(TlBase):
    def __init__(
        self,
        flags: int,  # orig int32_t
    ):
        self.flags = flags

    def get_type(self):
        raise NotImplementedError


class TlTreeType(TlTree):
    def __init__(
        self,
        flags: int,
        type_: 'TlType',
        child_count: int,  # unused count of items to create list
    ):
        super().__init__(flags)
        self.type = type_
        self.children = []

    def get_type(self):
        return NODE_TYPE_TYPE


class TlTreeNatConst(TlTree):
    def __init__(
        self,
        flags: int,
        num: int,
    ):
        super().__init__(flags)
        self.num = num

    def get_type(self):
        return NODE_TYPE_NAT_CONST


class TlTreeVarType(TlTree):
    def __init__(
        self,
        flags: int,
        var_num: int,
    ):
        super().__init__(flags)
        self.var_num = var_num

    def get_type(self):
        return NODE_TYPE_VAR_TYPE


class TlTreeVarNum(TlTree):
    def __init__(
        self,
        flags: int,
        var_num: int,
        diff: int,
    ):
        super().__init__(flags)
        self.var_num = var_num
        self.diff = diff

    def get_type(self):
        return NODE_TYPE_VAR_NUM


class TlTreeArray(TlTree):
    def __init__(
        self,
        flags: int,
        multiplicity: TlTree,
        a: List['Arg'],
    ):
        super().__init__(flags)
        self.multiplicity = multiplicity
        self.args = a

    def get_type(self):
        return NODE_TYPE_ARRAY


class Arg(TlBase):
    def __init__(
        self,
        name: str = None,
        flags: int = None,  # orig int32_t
        var_num: int = None,
        exist_var_num: int = None,
        exist_var_bit: int = None,
        type: 'TlType' = None,
    ):
        self.name = name
        self.flags = flags
        self.var_num = var_num
        self.exist_var_num = exist_var_num
        self.exist_var_bit = exist_var_bit
        self.type = type


class TlCombinator(TlBase):
    def __init__(
        self,
        id_: int = None,  # orig int32_t
        name: str = None,
        var_count: int = None,
        type_id: int = None,  # orig int32_t
        args: List['Arg'] = None,
        result: 'TlTree' = None,
    ):
        self.id = id_
        self.name = name
        self.var_count = var_count
        self.type_id = type_id
        self.args = args
        self.result = result


class TlType(TlBase):
    def __init__(
        self,
        id_: int = None,  # orig int32_t
        name: str = None,
        arity: int = None,
        flags: int = None,  # orig int32_t
        simple_constructors: int = None,
        constructors_num: int = None,  # orig size_t
        constructors: List['TlCombinator'] = None,
    ):
        self.id = id_
        self.name = name
        self.arity = arity
        self.flags = flags
        self.simple_constructors = simple_constructors
        self.constructors_num = constructors_num
        self.constructors = constructors

    def add_constructor(self, new_constructor: 'TlCombinator') -> None:
        self.constructors.append(new_constructor)
