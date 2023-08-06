# This file was auto-generated by Fern from our API Definition.

import enum
import typing

T_Result = typing.TypeVar("T_Result")


class ModelTypeEnum(str, enum.Enum):
    GENERATE = "GENERATE"
    CLASSIFY = "CLASSIFY"

    def visit(self, generate: typing.Callable[[], T_Result], classify: typing.Callable[[], T_Result]) -> T_Result:
        if self is ModelTypeEnum.GENERATE:
            return generate()
        if self is ModelTypeEnum.CLASSIFY:
            return classify()
