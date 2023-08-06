import concurrent.futures
import enum
import gzip
import math
import os
from typing import Dict, List, NewType, Protocol, runtime_checkable

import requests
from pydantic import StrictInt

from preemo.gen.endpoints.batch_allocate_artifact_part_pb2 import (
    AllocateArtifactPartConfig,
    AllocateArtifactPartConfigMetadata,
    BatchAllocateArtifactPartRequest,
)
from preemo.gen.endpoints.batch_create_artifact_pb2 import (
    BatchCreateArtifactRequest,
    CreateArtifactConfig,
)
from preemo.gen.endpoints.batch_finalize_artifact_pb2 import (
    BatchFinalizeArtifactRequest,
    FinalizeArtifactConfig,
)
from preemo.gen.endpoints.batch_get_artifact_download_url_pb2 import (
    BatchGetArtifactDownloadUrlRequest,
    GetArtifactDownloadUrlConfig,
    GetArtifactDownloadUrlConfigMetadata,
)
from preemo.gen.endpoints.batch_get_artifact_pb2 import (
    BatchGetArtifactRequest,
    GetArtifactConfig,
)
from preemo.gen.endpoints.batch_get_artifact_upload_url_pb2 import (
    BatchGetArtifactUploadUrlRequest,
    GetArtifactUploadUrlConfig,
    GetArtifactUploadUrlConfigMetadata,
)
from preemo.gen.models.artifact_type_pb2 import (
    ARTIFACT_TYPE_PARAMS,
    ARTIFACT_TYPE_RESULT,
)
from preemo.worker._env_manager import EnvManager
from preemo.worker._messaging_client import IMessagingClient
from preemo.worker._types import ImmutableModel

ArtifactId = NewType("ArtifactId", str)


class Artifact(ImmutableModel):
    id: ArtifactId
    part_size_threshold: StrictInt


class ArtifactType(enum.Enum):
    PARAMS = "params"
    RESULT = "result"


@runtime_checkable
class IArtifactManager(Protocol):
    def create_artifact(self, *, content: bytes, type_: ArtifactType) -> ArtifactId:
        pass

    def create_artifacts(
        self, *, contents: List[bytes], type_: ArtifactType
    ) -> List[ArtifactId]:
        pass

    def get_artifact(self, *, artifact_id: ArtifactId) -> bytes:
        pass

    def get_artifacts(self, *, artifact_ids: List[ArtifactId]) -> List[bytes]:
        pass


class ArtifactManager:
    @staticmethod
    def _calculate_part_count(*, content_length: int, part_size_threshold: int) -> int:
        return max(1, math.ceil(content_length / part_size_threshold))

    def __init__(
        self,
        *,
        messaging_client: IMessagingClient,
    ) -> None:
        self._messaging_client = messaging_client

    def _write_content(self, *, content: memoryview, url: str) -> None:
        if EnvManager.is_development:
            # treat url as file path
            os.makedirs(os.path.dirname(url), exist_ok=True)
            with open(url, "wb") as fout:
                fout.write(content)
        else:
            response = requests.put(
                url=url,
                data=gzip.compress(content),
                headers={
                    "Content-Encoding": "gzip",
                    "Content-Type": "application/octet-stream",
                },
            )

            # TODO(adrian@preemo.io, 06/15/2023): should retry if it fails
            if not response.ok:
                raise Exception(f"unexpected response while uploading: {response}")

    def _read_content(self, *, url: str) -> bytes:
        if EnvManager.is_development:
            # treat url as file path
            with open(url, "rb") as fin:
                return fin.read()
        else:
            response = requests.get(
                url=url,
                headers={
                    "Accept-Encoding": "gzip",
                    "Content-Type": "application/octet-stream",
                },
            )

            # TODO(adrian@preemo.io, 06/15/2023): should retry if it fails
            if not response.ok:
                raise Exception(f"unexpected response while downloading: {response}")

            return response.content

    def _create_artifacts(
        self,
        *,
        count: int,
        type_: ArtifactType,
    ) -> List[Artifact]:
        if type_ == ArtifactType.PARAMS:
            artifact_type = ARTIFACT_TYPE_PARAMS
        elif type_ == ArtifactType.RESULT:
            artifact_type = ARTIFACT_TYPE_RESULT
        else:
            raise AssertionError(f"Expected code to be unreachable, but got: {type_}")

        configs_by_index = {
            i: CreateArtifactConfig(artifact_type=artifact_type) for i in range(count)
        }
        response = self._messaging_client.batch_create_artifact(
            BatchCreateArtifactRequest(configs_by_index=configs_by_index)
        )

        return [
            Artifact(
                id=ArtifactId(result.artifact_id),
                part_size_threshold=result.part_size_threshold,
            )
            for _, result in sorted(
                response.results_by_index.items(), key=lambda x: x[0]
            )
        ]

    def create_artifact(self, *, content: bytes, type_: ArtifactType) -> ArtifactId:
        artifact_ids = self.create_artifacts(contents=[content], type_=type_)
        if len(artifact_ids) != 1:
            raise Exception("expected exactly one artifact to be created")

        return artifact_ids[0]

    def create_artifacts(
        self, *, contents: List[bytes], type_: ArtifactType
    ) -> List[ArtifactId]:
        artifacts = self._create_artifacts(count=len(contents), type_=type_)
        if len(artifacts) != len(contents):
            raise Exception("expected artifacts and contents lengths to be equal")

        allocate_configs_by_artifact_id: Dict[str, AllocateArtifactPartConfig] = {}
        upload_configs_by_artifact_id: Dict[str, GetArtifactUploadUrlConfig] = {}
        for artifact, content in zip(artifacts, contents):
            part_count = ArtifactManager._calculate_part_count(
                content_length=len(content),
                part_size_threshold=artifact.part_size_threshold,
            )

            allocate_configs_by_artifact_id[artifact.id] = AllocateArtifactPartConfig(
                metadatas_by_part_number={
                    part_number: AllocateArtifactPartConfigMetadata()
                    for part_number in range(part_count)
                }
            )

            upload_configs_by_artifact_id[artifact.id] = GetArtifactUploadUrlConfig(
                metadatas_by_part_number={
                    part_number: GetArtifactUploadUrlConfigMetadata()
                    for part_number in range(part_count)
                }
            )

        self._messaging_client.batch_allocate_artifact_part(
            BatchAllocateArtifactPartRequest(
                configs_by_artifact_id=allocate_configs_by_artifact_id
            )
        )

        get_url_response = self._messaging_client.batch_get_artifact_upload_url(
            BatchGetArtifactUploadUrlRequest(
                configs_by_artifact_id=upload_configs_by_artifact_id
            )
        )

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=EnvManager.max_upload_threads
        ) as executor:
            futures = []
            for artifact, content in zip(artifacts, contents):
                content_view = memoryview(content)
                result = get_url_response.results_by_artifact_id[artifact.id]

                for part_number, metadata in result.metadatas_by_part_number.items():
                    start_index = part_number * artifact.part_size_threshold
                    part_content = content_view[
                        start_index : start_index + artifact.part_size_threshold
                    ]

                    futures.append(
                        executor.submit(
                            self._write_content,
                            content=part_content,
                            url=metadata.signed_url,
                        )
                    )

            # TODO(adrian@preemo.io, 06/15/2023): add exception handling
            done, not_done = concurrent.futures.wait(
                futures, return_when=concurrent.futures.ALL_COMPLETED
            )

            if len(not_done) != 0:
                raise Exception("expected incomplete future set to be empty")

            if len(done) != len(futures):
                raise Exception("expected all futures to have completed")

            for future in done:
                # this will raise any exceptions raised in the thread
                future.result()

        self._messaging_client.batch_finalize_artifact(
            BatchFinalizeArtifactRequest(
                configs_by_artifact_id={
                    artifact.id: FinalizeArtifactConfig(
                        total_size=len(content),
                        part_count=ArtifactManager._calculate_part_count(
                            content_length=len(content),
                            part_size_threshold=artifact.part_size_threshold,
                        ),
                    )
                    for artifact, content in zip(artifacts, contents)
                }
            )
        )

        return [artifact.id for artifact in artifacts]

    def get_artifact(self, *, artifact_id: ArtifactId) -> bytes:
        contents = self.get_artifacts(artifact_ids=[artifact_id])
        if len(contents) != 1:
            raise Exception("expected exactly one artifact to be retrieved")

        return contents[0]

    def get_artifacts(self, *, artifact_ids: List[ArtifactId]) -> List[bytes]:
        get_artifact_response = self._messaging_client.batch_get_artifact(
            BatchGetArtifactRequest(
                configs_by_artifact_id={
                    artifact_id: GetArtifactConfig() for artifact_id in artifact_ids
                }
            )
        )

        configs_by_artifact_id = {
            artifact_id: GetArtifactDownloadUrlConfig(
                metadatas_by_part_number={
                    part_number: GetArtifactDownloadUrlConfigMetadata()
                    for part_number in range(result.part_count)
                }
            )
            for artifact_id, result in get_artifact_response.results_by_artifact_id.items()
        }
        get_url_response = self._messaging_client.batch_get_artifact_download_url(
            BatchGetArtifactDownloadUrlRequest(
                configs_by_artifact_id=configs_by_artifact_id
            )
        )

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=EnvManager.max_download_threads
        ) as executor:
            futures_by_artifact_id_and_part_number: Dict[
                ArtifactId, Dict[int, concurrent.futures.Future]
            ] = {}
            for (
                artifact_id,
                artifact_part_result,
            ) in get_url_response.results_by_artifact_id.items():
                futures_by_part_number: Dict[int, concurrent.futures.Future] = {}
                for (
                    part_number,
                    metadata,
                ) in artifact_part_result.metadatas_by_part_number.items():
                    futures_by_part_number[part_number] = executor.submit(
                        self._read_content,
                        url=metadata.signed_url,
                    )

                futures_by_artifact_id_and_part_number[
                    ArtifactId(artifact_id)
                ] = futures_by_part_number

            futures = [
                future
                for futures_by_part_number in futures_by_artifact_id_and_part_number.values()
                for future in futures_by_part_number.values()
            ]
            done, not_done = concurrent.futures.wait(
                futures,
                return_when=concurrent.futures.ALL_COMPLETED,
            )

            if len(not_done) != 0:
                raise Exception("expected incomplete future set to be empty")

            if len(done) != len(futures):
                raise Exception("expected all futures to have completed")

            results: List[bytes] = []
            for artifact_id in artifact_ids:
                futures_by_part_number = futures_by_artifact_id_and_part_number[
                    artifact_id
                ]
                get_artifact_result = get_artifact_response.results_by_artifact_id[
                    artifact_id
                ]

                # TODO(adrian@preemo.io, 06/20/2023): Consider other options for constructing the byte result,
                # such as a memory-mapped file or BytesIO
                result = bytearray()
                for part_number, future in sorted(
                    futures_by_part_number.items(), key=lambda x: x[0]
                ):
                    content = future.result()

                    if part_number < get_artifact_result.part_count - 1:
                        # not the final part
                        if len(content) != get_artifact_result.part_size_threshold:
                            raise Exception(
                                "expected content size to equal part_size_threshold"
                            )

                    result.extend(content)

                if len(result) != get_artifact_result.total_size:
                    raise Exception("expected result object size to equal total_size")

                # TODO(adrian@preemo.io, 06/20/2023): do i need to convert to bytes here? Is bytearray just masquerading as bytes?
                results.append(result)

        return results
