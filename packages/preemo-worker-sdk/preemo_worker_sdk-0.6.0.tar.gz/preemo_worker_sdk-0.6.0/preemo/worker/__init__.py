from threading import Thread as _Thread
from typing import Optional as _Optional

from preemo.gen.endpoints.sdk_server_ready_pb2 import (
    SdkServerReadyRequest as _SdkServerReadyRequest,
)
from preemo.worker._artifact_manager import ArtifactManager as _ArtifactManager
from preemo.worker._artifact_manager import IArtifactManager as _IArtifactManager
from preemo.worker._env_manager import EnvManager as _EnvManager
from preemo.worker._function_registry import FunctionRegistry as _FunctionRegistry
from preemo.worker._messaging_client import IMessagingClient as _IMessagingClient
from preemo.worker._messaging_client import (
    LocalMessagingClient as _LocalMessagingClient,
)
from preemo.worker._messaging_client import MessagingClient as _MessagingClient
from preemo.worker._sdk_server import SdkServer as _SdkServer
from preemo.worker._worker_client import WorkerClient as _WorkerClient


def _construct_messaging_client() -> _IMessagingClient:
    if _EnvManager.worker_server_url is None:
        return _LocalMessagingClient()

    return _MessagingClient(worker_server_url=_EnvManager.worker_server_url)


def _start_sdk_server(
    *, artifact_manager: _IArtifactManager, function_registry: _FunctionRegistry
) -> _Optional[_SdkServer]:
    if _EnvManager.sdk_server_port is None:
        return None

    server = _SdkServer(
        artifact_manager=artifact_manager,
        function_registry=function_registry,
        sdk_server_port=_EnvManager.sdk_server_port,
    )
    # This thread will keep the process running until the server is closed
    _Thread(target=lambda: server.wait_until_close()).start()

    return server


def _construct_worker_client() -> _WorkerClient:
    messaging_client = _construct_messaging_client()
    artifact_manager = _ArtifactManager(messaging_client=messaging_client)

    function_registry = _FunctionRegistry()
    sdk_server = _start_sdk_server(
        artifact_manager=artifact_manager, function_registry=function_registry
    )

    if sdk_server is not None:
        messaging_client.sdk_server_ready(_SdkServerReadyRequest())

    return _WorkerClient(
        artifact_manager=artifact_manager,
        function_registry=function_registry,
        messaging_client=messaging_client,
    )


# provide shorthand for functions
__all__ = ["get_function", "parallel", "register"]

_worker_client = _construct_worker_client()

get_function = _worker_client.get_function
parallel = _worker_client.parallel
register = _worker_client.register
