import os
from typing import Final, Optional


def _get_string_env(name: str) -> Optional[str]:
    value = os.getenv(key=name)
    if value is None or len(value) == 0:
        return None

    return value


# TODO(adrian@preemo.io, 05/24/2023): test this
def _get_optional_int_env(name: str) -> Optional[int]:
    value = _get_string_env(name)
    if value is None:
        return None

    try:
        return int(value)
    except ValueError:
        raise Exception(f"expected int for env variable: {name}")


def _get_int_env(name: str, *, default: Optional[int] = None) -> int:
    value = _get_optional_int_env(name)
    if value is None:
        if default is None:
            raise Exception(f"missing required env variable: {name}")

        return default

    return value


def _get_positive_int_env(name: str, *, default: Optional[int] = None) -> int:
    value = _get_int_env(name, default=default)
    if value <= 0:
        raise Exception(f"expected positive int for env variable: {name}")

    return value


def _get_bool_env(name: str, *, default: Optional[bool] = None) -> bool:
    value = _get_string_env(name)
    if value is None:
        if default is None:
            raise Exception(f"missing required env variable: {name}")

        return default

    lower_value = value.lower()
    if lower_value == "true":
        return True

    if lower_value == "false":
        return False

    raise Exception(f"expected bool for env variable: {name}")


class EnvManager:
    is_development: Final = _get_bool_env("PREEMO_IS_DEVELOPMENT", default=False)

    max_download_threads: Final = _get_positive_int_env(
        "PREEMO_MAX_DOWNLOAD_THREADS", default=5
    )

    max_upload_threads: Final = _get_positive_int_env(
        "PREEMO_MAX_UPLOAD_THREADS", default=5
    )

    sdk_server_port: Final = _get_optional_int_env("PREEMO_SDK_SERVER_PORT")

    worker_server_url: Final = _get_string_env("PREEMO_WORKER_SERVER_URL")
