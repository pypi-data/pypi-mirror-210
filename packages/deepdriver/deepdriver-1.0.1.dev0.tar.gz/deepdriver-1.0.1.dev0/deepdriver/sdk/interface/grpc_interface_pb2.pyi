from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ArtifactEntry(_message.Message):
    __slots__ = ["digest", "key", "lfsYN", "metadata", "path", "repoTag", "size", "status", "type"]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    LFSYN_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    REPOTAG_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    digest: str
    key: str
    lfsYN: str
    metadata: str
    path: str
    repoTag: str
    size: int
    status: str
    type: str
    def __init__(self, path: _Optional[str] = ..., digest: _Optional[str] = ..., size: _Optional[int] = ..., status: _Optional[str] = ..., lfsYN: _Optional[str] = ..., repoTag: _Optional[str] = ..., key: _Optional[str] = ..., type: _Optional[str] = ..., metadata: _Optional[str] = ...) -> None: ...

class ArtifactRecord(_message.Message):
    __slots__ = ["artifact_entry", "description", "digest", "expName", "metadata", "name", "run_id", "teamName", "type", "versioning"]
    ARTIFACT_ENTRY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    EXPNAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TEAMNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSIONING_FIELD_NUMBER: _ClassVar[int]
    artifact_entry: _containers.RepeatedCompositeFieldContainer[ArtifactEntry]
    description: str
    digest: str
    expName: str
    metadata: str
    name: str
    run_id: int
    teamName: str
    type: str
    versioning: str
    def __init__(self, run_id: _Optional[int] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., digest: _Optional[str] = ..., description: _Optional[str] = ..., versioning: _Optional[str] = ..., metadata: _Optional[str] = ..., teamName: _Optional[str] = ..., expName: _Optional[str] = ..., artifact_entry: _Optional[_Iterable[_Union[ArtifactEntry, _Mapping]]] = ...) -> None: ...

class ConfigItem(_message.Message):
    __slots__ = ["key", "valueAsBool", "valueAsFloat", "valueAsInt", "valueAsLong", "valueAsString"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUEASBOOL_FIELD_NUMBER: _ClassVar[int]
    VALUEASFLOAT_FIELD_NUMBER: _ClassVar[int]
    VALUEASINT_FIELD_NUMBER: _ClassVar[int]
    VALUEASLONG_FIELD_NUMBER: _ClassVar[int]
    VALUEASSTRING_FIELD_NUMBER: _ClassVar[int]
    key: str
    valueAsBool: bool
    valueAsFloat: float
    valueAsInt: int
    valueAsLong: int
    valueAsString: str
    def __init__(self, key: _Optional[str] = ..., valueAsString: _Optional[str] = ..., valueAsInt: _Optional[int] = ..., valueAsFloat: _Optional[float] = ..., valueAsLong: _Optional[int] = ..., valueAsBool: bool = ...) -> None: ...

class DownloadFileRequest(_message.Message):
    __slots__ = ["artifactName", "artifactType", "artifact_id", "authorization", "expName", "lfsYN", "path", "repoTag", "teamName", "versioning"]
    ARTIFACTNAME_FIELD_NUMBER: _ClassVar[int]
    ARTIFACTTYPE_FIELD_NUMBER: _ClassVar[int]
    ARTIFACT_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    EXPNAME_FIELD_NUMBER: _ClassVar[int]
    LFSYN_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    REPOTAG_FIELD_NUMBER: _ClassVar[int]
    TEAMNAME_FIELD_NUMBER: _ClassVar[int]
    VERSIONING_FIELD_NUMBER: _ClassVar[int]
    artifactName: str
    artifactType: str
    artifact_id: int
    authorization: str
    expName: str
    lfsYN: str
    path: str
    repoTag: str
    teamName: str
    versioning: str
    def __init__(self, path: _Optional[str] = ..., artifact_id: _Optional[int] = ..., artifactName: _Optional[str] = ..., artifactType: _Optional[str] = ..., teamName: _Optional[str] = ..., expName: _Optional[str] = ..., versioning: _Optional[str] = ..., lfsYN: _Optional[str] = ..., repoTag: _Optional[str] = ..., authorization: _Optional[str] = ...) -> None: ...

class DownloadFileResponse(_message.Message):
    __slots__ = ["contents", "digest", "rsp_result"]
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    RSP_RESULT_FIELD_NUMBER: _ClassVar[int]
    contents: bytes
    digest: str
    rsp_result: ResponseResult
    def __init__(self, rsp_result: _Optional[_Union[ResponseResult, _Mapping]] = ..., contents: _Optional[bytes] = ..., digest: _Optional[str] = ...) -> None: ...

class FileItem(_message.Message):
    __slots__ = ["contents", "filepath"]
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    FILEPATH_FIELD_NUMBER: _ClassVar[int]
    contents: bytes
    filepath: FilePath
    def __init__(self, filepath: _Optional[_Union[FilePath, _Mapping]] = ..., contents: _Optional[bytes] = ...) -> None: ...

class FilePath(_message.Message):
    __slots__ = ["path", "root_path"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    ROOT_PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    root_path: str
    def __init__(self, path: _Optional[str] = ..., root_path: _Optional[str] = ...) -> None: ...

class FileRecord(_message.Message):
    __slots__ = ["file"]
    FILE_FIELD_NUMBER: _ClassVar[int]
    file: FileItem
    def __init__(self, file: _Optional[_Union[FileItem, _Mapping]] = ...) -> None: ...

class LogItem(_message.Message):
    __slots__ = ["key", "valueAsBool", "valueAsFloat", "valueAsInt", "valueAsLong", "valueAsString"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUEASBOOL_FIELD_NUMBER: _ClassVar[int]
    VALUEASFLOAT_FIELD_NUMBER: _ClassVar[int]
    VALUEASINT_FIELD_NUMBER: _ClassVar[int]
    VALUEASLONG_FIELD_NUMBER: _ClassVar[int]
    VALUEASSTRING_FIELD_NUMBER: _ClassVar[int]
    key: str
    valueAsBool: bool
    valueAsFloat: float
    valueAsInt: int
    valueAsLong: int
    valueAsString: str
    def __init__(self, key: _Optional[str] = ..., valueAsString: _Optional[str] = ..., valueAsInt: _Optional[int] = ..., valueAsFloat: _Optional[float] = ..., valueAsLong: _Optional[int] = ..., valueAsBool: bool = ...) -> None: ...

class LogStep(_message.Message):
    __slots__ = ["num"]
    NUM_FIELD_NUMBER: _ClassVar[int]
    num: int
    def __init__(self, num: _Optional[int] = ...) -> None: ...

class ResponseResult(_message.Message):
    __slots__ = ["message", "result"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    message: str
    result: str
    def __init__(self, result: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class RunInfo(_message.Message):
    __slots__ = ["run_id"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: int
    def __init__(self, run_id: _Optional[int] = ...) -> None: ...

class SendAlertRequest(_message.Message):
    __slots__ = ["alertMessage", "expName", "runId", "teamName"]
    ALERTMESSAGE_FIELD_NUMBER: _ClassVar[int]
    EXPNAME_FIELD_NUMBER: _ClassVar[int]
    RUNID_FIELD_NUMBER: _ClassVar[int]
    TEAMNAME_FIELD_NUMBER: _ClassVar[int]
    alertMessage: str
    expName: str
    runId: int
    teamName: str
    def __init__(self, runId: _Optional[int] = ..., teamName: _Optional[str] = ..., expName: _Optional[str] = ..., alertMessage: _Optional[str] = ...) -> None: ...

class SendAlertResponse(_message.Message):
    __slots__ = ["rsp_result"]
    RSP_RESULT_FIELD_NUMBER: _ClassVar[int]
    rsp_result: ResponseResult
    def __init__(self, rsp_result: _Optional[_Union[ResponseResult, _Mapping]] = ...) -> None: ...

class TotalFileInfo(_message.Message):
    __slots__ = ["digest", "entry"]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    digest: str
    entry: _containers.RepeatedCompositeFieldContainer[ArtifactEntry]
    def __init__(self, digest: _Optional[str] = ..., entry: _Optional[_Iterable[_Union[ArtifactEntry, _Mapping]]] = ...) -> None: ...

class UpdateConfigRequest(_message.Message):
    __slots__ = ["authorization", "expName", "item", "runId", "teamName"]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    EXPNAME_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    RUNID_FIELD_NUMBER: _ClassVar[int]
    TEAMNAME_FIELD_NUMBER: _ClassVar[int]
    authorization: str
    expName: str
    item: _containers.RepeatedCompositeFieldContainer[ConfigItem]
    runId: int
    teamName: str
    def __init__(self, runId: _Optional[int] = ..., item: _Optional[_Iterable[_Union[ConfigItem, _Mapping]]] = ..., teamName: _Optional[str] = ..., expName: _Optional[str] = ..., authorization: _Optional[str] = ...) -> None: ...

class UpdateConfigResponse(_message.Message):
    __slots__ = ["rsp_result"]
    RSP_RESULT_FIELD_NUMBER: _ClassVar[int]
    rsp_result: ResponseResult
    def __init__(self, rsp_result: _Optional[_Union[ResponseResult, _Mapping]] = ...) -> None: ...

class UploadArtifactRequest(_message.Message):
    __slots__ = ["artifact", "authorization"]
    ARTIFACT_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    artifact: ArtifactRecord
    authorization: str
    def __init__(self, artifact: _Optional[_Union[ArtifactRecord, _Mapping]] = ..., authorization: _Optional[str] = ...) -> None: ...

class UploadArtifactResponse(_message.Message):
    __slots__ = ["artifact_id", "rsp_result"]
    ARTIFACT_ID_FIELD_NUMBER: _ClassVar[int]
    RSP_RESULT_FIELD_NUMBER: _ClassVar[int]
    artifact_id: int
    rsp_result: ResponseResult
    def __init__(self, artifact_id: _Optional[int] = ..., rsp_result: _Optional[_Union[ResponseResult, _Mapping]] = ...) -> None: ...

class UploadFileRequest(_message.Message):
    __slots__ = ["artifactName", "artifactType", "artifact_id", "authorization", "digest", "expName", "file", "last_file_yn", "runName", "run_id", "teamName", "total_file_info", "uploadType"]
    ARTIFACTNAME_FIELD_NUMBER: _ClassVar[int]
    ARTIFACTTYPE_FIELD_NUMBER: _ClassVar[int]
    ARTIFACT_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    EXPNAME_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    LAST_FILE_YN_FIELD_NUMBER: _ClassVar[int]
    RUNNAME_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TEAMNAME_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FILE_INFO_FIELD_NUMBER: _ClassVar[int]
    UPLOADTYPE_FIELD_NUMBER: _ClassVar[int]
    artifactName: str
    artifactType: str
    artifact_id: int
    authorization: str
    digest: str
    expName: str
    file: FileRecord
    last_file_yn: str
    runName: str
    run_id: int
    teamName: str
    total_file_info: TotalFileInfo
    uploadType: str
    def __init__(self, uploadType: _Optional[str] = ..., file: _Optional[_Union[FileRecord, _Mapping]] = ..., artifact_id: _Optional[int] = ..., run_id: _Optional[int] = ..., artifactName: _Optional[str] = ..., artifactType: _Optional[str] = ..., digest: _Optional[str] = ..., last_file_yn: _Optional[str] = ..., authorization: _Optional[str] = ..., teamName: _Optional[str] = ..., expName: _Optional[str] = ..., runName: _Optional[str] = ..., total_file_info: _Optional[_Union[TotalFileInfo, _Mapping]] = ...) -> None: ...

class UploadFileResponse(_message.Message):
    __slots__ = ["rsp_result"]
    RSP_RESULT_FIELD_NUMBER: _ClassVar[int]
    rsp_result: ResponseResult
    def __init__(self, rsp_result: _Optional[_Union[ResponseResult, _Mapping]] = ...) -> None: ...

class UploadLogRequest(_message.Message):
    __slots__ = ["authorization", "expName", "item", "run", "step", "teamName"]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    EXPNAME_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    RUN_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    TEAMNAME_FIELD_NUMBER: _ClassVar[int]
    authorization: str
    expName: str
    item: _containers.RepeatedCompositeFieldContainer[LogItem]
    run: RunInfo
    step: LogStep
    teamName: str
    def __init__(self, item: _Optional[_Iterable[_Union[LogItem, _Mapping]]] = ..., step: _Optional[_Union[LogStep, _Mapping]] = ..., run: _Optional[_Union[RunInfo, _Mapping]] = ..., teamName: _Optional[str] = ..., expName: _Optional[str] = ..., authorization: _Optional[str] = ...) -> None: ...

class UploadLogResponse(_message.Message):
    __slots__ = ["rsp_result"]
    RSP_RESULT_FIELD_NUMBER: _ClassVar[int]
    rsp_result: ResponseResult
    def __init__(self, rsp_result: _Optional[_Union[ResponseResult, _Mapping]] = ...) -> None: ...

class UseArtifactRequest(_message.Message):
    __slots__ = ["artifact_name", "artifact_tag", "artifact_type", "authorization", "exp_name", "run_id", "team_name"]
    ARTIFACT_NAME_FIELD_NUMBER: _ClassVar[int]
    ARTIFACT_TAG_FIELD_NUMBER: _ClassVar[int]
    ARTIFACT_TYPE_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    EXP_NAME_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_NAME_FIELD_NUMBER: _ClassVar[int]
    artifact_name: str
    artifact_tag: str
    artifact_type: str
    authorization: str
    exp_name: str
    run_id: int
    team_name: str
    def __init__(self, artifact_name: _Optional[str] = ..., artifact_type: _Optional[str] = ..., artifact_tag: _Optional[str] = ..., team_name: _Optional[str] = ..., exp_name: _Optional[str] = ..., run_id: _Optional[int] = ..., authorization: _Optional[str] = ...) -> None: ...

class UseArtifactResponse(_message.Message):
    __slots__ = ["artifact", "artifact_id", "rsp_result"]
    ARTIFACT_FIELD_NUMBER: _ClassVar[int]
    ARTIFACT_ID_FIELD_NUMBER: _ClassVar[int]
    RSP_RESULT_FIELD_NUMBER: _ClassVar[int]
    artifact: ArtifactRecord
    artifact_id: int
    rsp_result: ResponseResult
    def __init__(self, artifact_id: _Optional[int] = ..., rsp_result: _Optional[_Union[ResponseResult, _Mapping]] = ..., artifact: _Optional[_Union[ArtifactRecord, _Mapping]] = ...) -> None: ...
