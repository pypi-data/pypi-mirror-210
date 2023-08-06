from typing import Mapping, Optional, Union


def ensure_keys_match(*, expected: Mapping, actual: Mapping) -> None:
    if expected.keys() == actual.keys():
        return

    message = "expected keys to match but found:"

    missing_keys = expected.keys() - actual.keys()
    if len(missing_keys) > 0:
        message += f"\nmissing expected keys: {missing_keys}"

    unexpected_keys = actual.keys() - expected.keys()
    if len(unexpected_keys) > 0:
        message += f"\nunexpected keys: {unexpected_keys}"

    raise Exception(message)


def ensure_value_is_non_negative(
    *, name: str, value: Optional[Union[int, float]]
) -> None:
    if value is not None and value < 0:
        raise Exception(f"{name} must not be negative")
