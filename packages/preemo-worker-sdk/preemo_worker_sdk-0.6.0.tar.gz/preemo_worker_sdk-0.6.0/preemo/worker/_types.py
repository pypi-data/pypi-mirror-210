from typing import NoReturn

from pydantic import BaseModel, StrictStr

_ASSERT_NEVER_REPR_MAX_LENGTH = 100


# Copied from https://github.com/python/cpython/blob/main/Lib/typing.py#L2467
# typing.assert_never and typing.Never were added in python 3.11, but NoReturn is functionally equivalent in prior versions
def assert_never(arg: NoReturn, /) -> NoReturn:
    """Statically assert that a line of code is unreachable.
    Example::
        def int_or_str(arg: int | str) -> None:
            match arg:
                case int():
                    print("It's an int")
                case str():
                    print("It's a str")
                case _:
                    assert_never(arg)
    If a type checker finds that a call to assert_never() is
    reachable, it will emit an error.
    At runtime, this throws an exception when called.
    """
    value = repr(arg)
    if len(value) > _ASSERT_NEVER_REPR_MAX_LENGTH:
        value = value[:_ASSERT_NEVER_REPR_MAX_LENGTH] + "..."
    raise AssertionError(f"Expected code to be unreachable, but got: {value}")


class ImmutableModel(BaseModel):
    class Config:
        allow_mutation = False


class StringValue(ImmutableModel):
    value: StrictStr

    def __hash__(self) -> int:
        return hash(self.value)
