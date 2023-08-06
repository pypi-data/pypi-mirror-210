# This file was auto-generated by Fern from our API Definition.

import enum
import typing

T_Result = typing.TypeVar("T_Result")


class EnvironmentEnum(str, enum.Enum):
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

    def visit(
        self,
        development: typing.Callable[[], T_Result],
        staging: typing.Callable[[], T_Result],
        production: typing.Callable[[], T_Result],
    ) -> T_Result:
        if self is EnvironmentEnum.DEVELOPMENT:
            return development()
        if self is EnvironmentEnum.STAGING:
            return staging()
        if self is EnvironmentEnum.PRODUCTION:
            return production()
