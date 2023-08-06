import dataclasses
from typing import Optional, Type, TypeVar, List

T = TypeVar("T")


@dataclasses.dataclass
class FunctionParamsMeta:
    class ArgsTypeEnum:
        NORMAL = 1
        CLASS = 2
        INSTANCE = 3

    args_name: str
    args_class: Optional[Type]
    args_type: int


def get_function_params_meta_list(func) -> List[FunctionParamsMeta]:
    annotations = func.__annotations__
    all_params = func.__code__.co_varnames
    result = []
    for param in all_params:
        if param == "self":
            result.append(
                FunctionParamsMeta(
                    args_name=param,
                    args_class=None,
                    args_type=FunctionParamsMeta.ArgsTypeEnum.INSTANCE,
                )
            )
        elif param == "cls":
            result.append(
                FunctionParamsMeta(
                    args_name=param,
                    args_class=None,
                    args_type=FunctionParamsMeta.ArgsTypeEnum.CLASS,
                )
            )
        else:
            result.append(
                FunctionParamsMeta(
                    args_name=param,
                    args_class=annotations[param],
                    args_type=FunctionParamsMeta.ArgsTypeEnum.NORMAL,
                )
            )
    return result
