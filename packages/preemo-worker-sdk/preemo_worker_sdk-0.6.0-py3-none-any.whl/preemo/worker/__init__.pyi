from typing import Callable, List, Optional, TypedDict, Union

class Result:
    def get(self) -> bytes: ...

class Function:
    def __call__(self, params: Optional[bytes] = None) -> Optional[Result]: ...

class MebibyteDict(TypedDict):
    MiB: int

class GibibyteDict(TypedDict):
    GiB: int

ByteDict = Union[MebibyteDict, GibibyteDict]

def get_function(name: str, *, namespace: Optional[str] = None) -> Function: ...
def parallel(
    function: Function,
    *,
    params: Optional[List[bytes]] = None,
    count: Optional[int] = None,
) -> List[Optional[Result]]: ...
def register(
    outer_function: Optional[Callable] = ...,
    *,
    cpu_cores: Optional[Union[int, float]] = ...,
    gpu_count: Optional[int] = ...,
    gpu_model: Optional[str] = ...,
    memory: Optional[ByteDict] = ...,
    name: Optional[str] = ...,
    namespace: Optional[str] = ...,
    storage: Optional[ByteDict] = ...,
) -> Callable: ...
