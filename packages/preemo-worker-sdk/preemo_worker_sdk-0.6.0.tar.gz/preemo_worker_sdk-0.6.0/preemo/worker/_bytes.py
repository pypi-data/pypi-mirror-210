from typing import Literal, TypedDict, Union, cast


class MebibyteDict(TypedDict):
    MiB: int


class GibibyteDict(TypedDict):
    GiB: int


ByteDict = Union[MebibyteDict, GibibyteDict]

KiB = 1024
MiB = 1024 * KiB
GiB = 1024 * MiB

mebibyte_literal: Literal["MiB"] = "MiB"
gibibyte_literal: Literal["GiB"] = "GiB"


def convert_mebibytes_to_bytes(mebibyte_dict: MebibyteDict) -> int:
    return mebibyte_dict[mebibyte_literal] * MiB


def convert_gibibytes_to_bytes(gibibyte_dict: GibibyteDict) -> int:
    return gibibyte_dict[gibibyte_literal] * GiB


def convert_byte_dict_to_bytes(byte_dict: ByteDict) -> int:
    # We have to cast here because mypy will not implement type narrowing for TypedDict
    # See https://github.com/python/mypy/issues/11080

    if mebibyte_literal in byte_dict:
        return convert_mebibytes_to_bytes(cast(MebibyteDict, byte_dict))

    if gibibyte_literal in byte_dict:
        return convert_gibibytes_to_bytes(cast(GibibyteDict, byte_dict))

    raise Exception(f"byte_dict had unexpected keys: {byte_dict}")
