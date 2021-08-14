from typing import List, Dict, Union

from .tl_core import TlBase, TlType, TlCombinator


class TlConfig(TlBase):
    def __init__(
        self,
    ):
        self.types: List['TlType'] = []
        self.id_to_type: Dict[int, 'TlType'] = {}  # orig int32_t
        self.name_to_type: Dict[str, 'TlType'] = {}
        self.functions: List['TlCombinator'] = []
        self.id_to_function: Dict[int, 'TlCombinator'] = {}  # orig int32_t
        self.name_to_function: Dict[str, 'TlCombinator'] = {}

    def add_type(self, type_: 'TlType') -> None:
        self.types.append(type_)
        self.id_to_type[type_.id] = type_
        self.name_to_type[type_.name] = type_

    def get_type(self, type_id_or_name: Union[int, str]) -> 'TlType':  # orig int32_t
        if isinstance(type_id_or_name, int):
            return self.id_to_type[type_id_or_name]
        else:
            return self.name_to_type[type_id_or_name]

    def add_function(self, function: 'TlCombinator') -> None:
        self.functions.append(function)
        self.id_to_function[function.id] = function
        self.name_to_function[function.name] = function

    def get_function(self, function_id_or_name: Union[int, str]) -> 'TlCombinator':  # orig int32_t
        if isinstance(function_id_or_name, int):
            return self.id_to_function[function_id_or_name]
        else:
            return self.name_to_function[function_id_or_name]

    def get_type_count(self) -> int:  # orig size_t
        return len(self.types)

    def get_type_by_num(self, num: int) -> 'TlType':  # orig size_t
        return self.types[num]

    def get_function_count(self) -> int:  # orig size_t
        return len(self.functions)

    def get_function_by_num(self, num: int) -> 'TlCombinator':  # orig size_t
        return self.functions[num]
