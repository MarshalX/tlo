from typing import List


class TlTree:
    def __init__(
        self,
        flags: int,  # orig int32_t
    ):
        self.flags = flags

    def get_type(self):
        raise NotImplementedError


class Arg:
    def __init__(
        self,
        name: str,
        flags: int,  # orig int32_t
        var_num: int,
        exist_var_num: int,
        exist_var_bit: int,
        type: 'TlType',
    ):
        self.name = name
        self.flags = flags
        self.var_num = var_num
        self.exist_var_num = exist_var_num
        self.exist_var_bit = exist_var_bit
        self.type = type


class TlCombinator:
    def __init__(
        self,
        id: int,  # orig int32_t
        name: str,
        var_count: int,
        type_id: int,  # orig int32_t
        args: List['Arg'],
        result: 'TlTree',
    ):
        self.id = id
        self.name = name
        self.var_count = var_count
        self.type_id = type_id
        self.args = args
        self.result = result


class TlType:
    def __init__(
        self,
        id: int,  # orig int32_t
        name: str,
        arity: int,
        flags: int,  # orig int32_t
        simple_constructors: int,
        constructors_num: int,  # orig size_t
        constructors: List['TlCombinator'],
    ):
        self.id = id
        self.name = name
        self.arity = arity
        self.flags = flags
        self.simple_constructors = simple_constructors
        self.constructors_num = constructors_num
        self.constructors = constructors

    def add_constructor(self, new_constructor: 'TlCombinator') -> None:
        self.constructors.append(new_constructor)
