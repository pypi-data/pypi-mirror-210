from typing import Callable, List, Optional, Union

from google.protobuf.struct_pb2 import NULL_VALUE

from preemo.gen.endpoints.batch_execute_function_pb2 import BatchExecuteFunctionRequest
from preemo.gen.endpoints.check_function_pb2 import CheckFunctionRequest
from preemo.gen.endpoints.register_function_pb2 import (
    CpuRequirements,
    GpuRequirements,
    RegisterFunctionRequest,
    ResourceRequirements,
)
from preemo.gen.models.registered_function_pb2 import RegisteredFunction
from preemo.gen.models.value_pb2 import Value
from preemo.worker._artifact_manager import ArtifactId, ArtifactType, IArtifactManager
from preemo.worker._bytes import ByteDict, convert_byte_dict_to_bytes
from preemo.worker._function_registry import FunctionRegistry
from preemo.worker._messaging_client import IMessagingClient
from preemo.worker._types import assert_never
from preemo.worker._validation import ensure_value_is_non_negative


class Result:
    # TODO(adrian@preemo.io, 06/20/2023): need to sort out how this class
    # can be used when error handling, status checking, etc
    # Perhaps futures should be used instead
    def __init__(
        self, *, artifact_id: ArtifactId, artifact_manager: IArtifactManager
    ) -> None:
        self._artifact_id = artifact_id
        self._artifact_manager = artifact_manager

    def get(self) -> bytes:
        return self._artifact_manager.get_artifact(artifact_id=self._artifact_id)


class Function:
    def __init__(
        self,
        *,
        artifact_manager: IArtifactManager,
        messaging_client: IMessagingClient,
        name: str,
        namespace: Optional[str],
    ) -> None:
        self._artifact_manager = artifact_manager
        self._messaging_client = messaging_client
        self.name = name
        self.namespace = namespace

        self._ensure_function_is_registered()

    def _ensure_function_is_registered(self) -> None:
        # check_function raises an error if the function is not found
        self._messaging_client.check_function(
            CheckFunctionRequest(
                function_to_check=RegisteredFunction(
                    name=self.name, namespace=self.namespace
                )
            )
        )

    def __call__(self, params: Optional[bytes] = None) -> Optional[Result]:
        if params is None:
            function_parameter = Value(null_value=NULL_VALUE)
        else:
            artifact_id = self._artifact_manager.create_artifact(
                content=params, type_=ArtifactType.PARAMS
            )
            function_parameter = Value(artifact_id=artifact_id)

        response = self._messaging_client.batch_execute_function(
            BatchExecuteFunctionRequest(
                function_to_execute=RegisteredFunction(
                    name=self.name, namespace=self.namespace
                ),
                parameters_by_index={0: function_parameter},
            )
        )

        function_result = response.results_by_index[0]

        kind = function_result.WhichOneof("kind")
        if kind is None:
            raise Exception("expected kind to be defined")

        if kind == "null_value":
            return None

        if kind == "artifact_id":
            return Result(
                artifact_id=ArtifactId(function_result.artifact_id),
                artifact_manager=self._artifact_manager,
            )

        assert_never(kind)


# TODO(adrian@preemo.io, 05/11/2023): add logging
class WorkerClient:
    @staticmethod
    def _convert_cores_to_millicores(cores: Union[int, float]) -> int:
        value = 1000 * cores
        if isinstance(value, int):
            return value

        if not value.is_integer():
            raise Exception("cores precision must not exceed 3 decimal places")

        return int(value)

    @staticmethod
    def _construct_resource_requirements(
        *,
        cpu_cores: Optional[Union[int, float]] = None,
        gpu_count: Optional[int] = None,
        gpu_model: Optional[str] = None,
        memory: Optional[ByteDict] = None,
        storage: Optional[ByteDict] = None,
    ) -> Optional[ResourceRequirements]:
        if all(o is None for o in [cpu_cores, gpu_count, gpu_model, memory, storage]):
            return None

        memory_in_bytes = None if memory is None else convert_byte_dict_to_bytes(memory)

        storage_in_bytes = (
            None if storage is None else convert_byte_dict_to_bytes(storage)
        )

        ensure_value_is_non_negative(name="cpu_cores", value=cpu_cores)
        ensure_value_is_non_negative(name="gpu_count", value=gpu_count)
        ensure_value_is_non_negative(name="memory", value=memory_in_bytes)
        ensure_value_is_non_negative(name="storage", value=storage_in_bytes)

        if gpu_model is None:
            if gpu_count is not None:
                raise Exception(
                    "cannot specify gpu_count without also specifying a gpu_model"
                )

            millicores = (
                None
                if cpu_cores is None
                else WorkerClient._convert_cores_to_millicores(cpu_cores)
            )

            return ResourceRequirements(
                cpu=CpuRequirements(
                    millicores=millicores,
                    memory_in_bytes=memory_in_bytes,
                    storage_in_bytes=storage_in_bytes,
                )
            )

        if cpu_cores is not None:
            raise Exception(
                "cannot specify cpu_cores while specifying a gpu_model (perhaps you meant gpu_count?)"
            )

        return ResourceRequirements(
            gpu=GpuRequirements(
                gpu_model=gpu_model,
                gpu_count=gpu_count,
                memory_in_bytes=memory_in_bytes,
                storage_in_bytes=storage_in_bytes,
            )
        )

    def __init__(
        self,
        *,
        artifact_manager: IArtifactManager,
        function_registry: FunctionRegistry,
        messaging_client: IMessagingClient,
    ) -> None:
        self._artifact_manager = artifact_manager
        self._messaging_client = messaging_client
        self._function_registry = function_registry

    def get_function(self, name: str, *, namespace: Optional[str] = None) -> Function:
        return Function(
            artifact_manager=self._artifact_manager,
            messaging_client=self._messaging_client,
            name=name,
            namespace=namespace,
        )

    def parallel(
        self,
        function: Function,
        *,
        params: Optional[List[bytes]] = None,
        count: Optional[int] = None,
    ) -> List[Optional[Result]]:
        # TODO(adrian@preemo.io, 06/20/2023): should take an optional config argument includes stuff like max batch size

        if params is None:
            if count is None:
                raise ValueError("either params or count must be specified")

            if count <= 0:
                raise ValueError("count must be positive")

            function_parameters_by_index = {
                i: Value(null_value=NULL_VALUE) for i in range(count)
            }
        else:
            if count is not None:
                raise ValueError("params and count must not both be specified")

            if len(params) == 0:
                return []

            artifact_ids = self._artifact_manager.create_artifacts(
                contents=params, type_=ArtifactType.PARAMS
            )
            function_parameters_by_index = {
                i: Value(artifact_id=artifact_id)
                for i, artifact_id in enumerate(artifact_ids)
            }

        response = self._messaging_client.batch_execute_function(
            BatchExecuteFunctionRequest(
                function_to_execute=RegisteredFunction(
                    name=function.name, namespace=function.namespace
                ),
                parameters_by_index=function_parameters_by_index,
            )
        )

        results: List[Optional[Result]] = []
        for _, function_result in sorted(
            response.results_by_index.items(), key=lambda x: x[0]
        ):
            kind = function_result.WhichOneof("kind")
            if kind is None:
                raise Exception("expected kind to be defined")

            if kind == "null_value":
                results.append(None)
            elif kind == "artifact_id":
                results.append(
                    Result(
                        artifact_id=ArtifactId(function_result.artifact_id),
                        artifact_manager=self._artifact_manager,
                    )
                )
            else:
                assert_never(kind)

        return results

    def register(
        self,
        outer_function: Optional[Callable] = None,
        *,
        cpu_cores: Optional[Union[int, float]] = None,
        gpu_count: Optional[int] = None,
        # TODO(adrian@preemo.io, 06/01/2023): create an enum of supported options to make the gpu_model parameter easier to use
        gpu_model: Optional[str] = None,
        memory: Optional[ByteDict] = None,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        storage: Optional[ByteDict] = None,
    ) -> Callable:
        def decorator(function: Callable) -> Callable:
            if name is None:
                function_name = function.__name__
            else:
                function_name = name

            self._function_registry.register_function(
                function, name=function_name, namespace=namespace
            )

            resource_requirements = WorkerClient._construct_resource_requirements(
                cpu_cores=cpu_cores,
                gpu_count=gpu_count,
                gpu_model=gpu_model,
                memory=memory,
                storage=storage,
            )

            self._messaging_client.register_function(
                RegisterFunctionRequest(
                    function_to_register=RegisteredFunction(
                        name=function_name, namespace=namespace
                    ),
                    resource_requirements=resource_requirements,
                )
            )

            return function

        if outer_function is None:
            return decorator

        return decorator(outer_function)
