import concurrent.futures

import grpc

from preemo.gen.services.sdk_pb2_grpc import add_SdkServiceServicer_to_server
from preemo.worker._artifact_manager import IArtifactManager
from preemo.worker._function_registry import FunctionRegistry
from preemo.worker._sdk_service import SdkService


class SdkServer:
    def __init__(
        self,
        *,
        artifact_manager: IArtifactManager,
        function_registry: FunctionRegistry,
        sdk_server_port: int,
    ) -> None:
        server = grpc.server(
            concurrent.futures.ThreadPoolExecutor(max_workers=1),
            # This option prevents multiple servers from reusing the same port (see https://groups.google.com/g/grpc-io/c/RB69llv2tC4/m/7E__iL3LAwAJ)
            options=(("grpc.so_reuseport", 0),),
        )

        def close() -> None:
            server.stop(grace=10)  # seconds

        add_SdkServiceServicer_to_server(
            SdkService(
                artifact_manager=artifact_manager,
                function_registry=function_registry,
                terminate_server=close,
            ),
            server,
        )

        server.add_insecure_port(f"0.0.0.0:{sdk_server_port}")
        server.start()

        print(f"sdk server has started on port {sdk_server_port}")

        self._server = server

    def wait_until_close(self) -> None:
        self._server.wait_for_termination()
