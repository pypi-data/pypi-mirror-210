"""
This module provides data models for the DataIndex.
"""
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from klu.common.models import BaseDataClass, BaseEngineModel, BasicStringEnum


class DataIndexStatusEnum(BasicStringEnum):
    """The enum used to represent DataIndex processing task status. Based on celery statuses."""

    # The task is waiting for execution.
    PENDING = "PENDING"
    # The task has been started.
    STARTED = "STARTED"

    # The task is to be retried, possibly because of failure.
    RETRY = "RETRY"
    # The task raised an exception, or has exceeded the retry limit.
    FAILURE = "FAILURE"
    # The task executed successfully.
    SUCCESS = "SUCCESS"


@dataclass
class DataIndex(BaseEngineModel):
    """
    This class represents the DataIndex model returned from the Klu engine
    """

    guid: str
    name: str
    processed: bool

    type_id: int
    task_id: str
    file_url: str
    index_url: str
    loader_id: int
    workspace_id: int
    created_by_id: str

    description: Optional[str]
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @classmethod
    def _from_engine_format(cls, data: dict) -> "DataIndex":
        return cls._create_instance(
            **{
                "type_id": data.pop("typeId", None),
                "task_id": data.pop("taskId", None),
                "file_url": data.pop("fileUrl", None),
                "index_url": data.pop("indexUrl", None),
                "loader_id": data.pop("loaderId", None),
                "updated_at": data.pop("updatedAt", None),
                "created_at": data.pop("createdAt", None),
                "workspace_id": data.pop("workspaceId", None),
                "created_by_id": data.pop("createdById", None),
            },
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(self)

        return {
            "typeId": base_dict.pop("type_id", None),
            "taskId": base_dict.pop("task_id", None),
            "fileUrl": base_dict.pop("file_url", None),
            "indexUrl": base_dict.pop("index_url", None),
            "loaderId": base_dict.pop("loader_id", None),
            "updatedAt": base_dict.pop("updated_at", None),
            "createdAt": base_dict.pop("created_at", None),
            "workspaceId": base_dict.pop("workspace_id", None),
            "createdById": base_dict.pop("created_by_id", None),
            **base_dict,
        }


@dataclass
class PreSignUrlPostData(BaseDataClass):
    """
    Data that represents response from pre-signed url generation.
    url - pre-signed url that can be used to upload the file.
    fields - dict with data that has to be passed alongside the file during the upload
    object_url - contains the url that can be used to access the file location after the upload.
    This same object_url can be used during the data_index creation.
    """

    url: str
    fields: dict
    object_url: str


@dataclass
class FileData(BaseDataClass):
    """
    file_name (str): The name of the file to be uploaded. Has to be unique among the files you uploaded before.
    file_path (str): The path to a file in your system.
    The file path can be an absolute path, a relative path, or a path that includes variables like ~ or $HOME
    """

    file_path: str
    file_name: str
