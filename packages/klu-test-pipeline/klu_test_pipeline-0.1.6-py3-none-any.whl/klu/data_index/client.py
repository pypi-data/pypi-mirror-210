# mypy: disable-error-code="override"
from typing import Optional

import aiohttp
from aiohttp import ClientResponseError

from klu.common.client import KluClientBase
from klu.common.errors import (
    InvalidUpdateParamsError,
    UnknownKluAPIError,
    UnknownKluError,
)
from klu.data_index.constants import (
    DATA_INDEX_ENDPOINT,
    DATA_INDEX_STATUS_ENDPOINT,
    PROCESS_DATA_INDEX_ENDPOINT,
    UPLOAD_PRE_SIGNED_URL_ENDPOINT,
)
from klu.data_index.errors import DataIndexNotFoundError
from klu.data_index.models import (
    DataIndex,
    DataIndexStatusEnum,
    FileData,
    PreSignUrlPostData,
)
from klu.utils.dict_helpers import dict_no_empty
from klu.utils.file_upload import upload_to_pre_signed_url
from klu.workspace.errors import WorkspaceOrUserNotFoundError


class DataIndexClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, DATA_INDEX_ENDPOINT, DataIndex)

    async def create(
        self,
        name: str,
        description: str,
        splitter: Optional[str] = None,
        file_data: Optional[FileData] = None,
    ) -> DataIndex:
        """
        Creates a new index based on the provided data.

        Args:
            name (str): The name of the index
            description (str): The description of the index
            file_data (Optional[FileData]): Metadata of the file to be uploaded.
                Can be omitted if only the data_index skeleton has to be created
            splitter (Optional[str]): The column splitter - filter by the user when they are dealing with a multi
                tenanted environment.

        Returns:
            dict with a message about successful index creation and id of a newly created index file.
        Use this id to check the status of dataIndex processing.
        """
        file_url = await self.upload_index_file(file_data) if file_data else None
        data_index = {
            "name": name,
            "splitter": splitter,
            "description": description,
        }
        if file_url:
            data_index["file_url"] = file_url

        return await super().create(**data_index)

    # type: ignore
    async def get(self, guid: str) -> DataIndex:
        """
        Retrieves data_index information based on the id.

        Args:
            guid (str): id of a data_index object to fetch.

        Returns:
            DataIndex object found by provided id
        """
        return await super().get(guid)

    # type: ignore
    async def update(
        self, guid: str, name: Optional[str] = None, description: Optional[str] = None
    ) -> DataIndex:
        """
        Update data_index data. At least one of the params has to be provided

        Args:
            guid (str): ID of a data_index to update.
            name: Optional[str]. New data_index name
            description: Optional[str]. New data_index description

        Returns:
            Updated application instance
        """

        if not name and not description:
            raise InvalidUpdateParamsError()

        return await super().update(
            **{
                "guid": guid,
                **dict_no_empty({"name": name, "description": description}),
            }
        )

    # type: ignore
    async def delete(self, guid: str) -> DataIndex:
        """
        Delete existing data_index information defined by the id.

        Args:
            guid (str): The id of a data_index to delete.

        Returns:
            Deleted DataIndex object
        """
        return await super().delete(guid)

    async def get_status(self, guid: int) -> DataIndexStatusEnum:
        """
        Retrieves the status of an index creation task based on the provided index ID.

        Args:
            guid (int): The ID of the data index.

        Returns:
            string representing te data_index status
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(DATA_INDEX_STATUS_ENDPOINT.format(id=guid))
            except ClientResponseError as e:
                if e.status == 404:
                    raise DataIndexNotFoundError(guid)

                raise UnknownKluAPIError(e.status, e.message)

            return DataIndexStatusEnum.get(response.get("status"))  # type: ignore

    async def process_data_index(
        self, data_index_guid: str, file_name: str, splitter: Optional[str] = None
    ) -> dict:
        """
        Processes existing index identified by provided data_index id using provider column splitter

        Args:
            data_index_guid (str): Guid of data index to process
            file_name (str): Name of the file uploaded before that should be used for DataIndex processing.
                splitter (Optional[str]): The column splitter - filter by the user when they are dealing with a multi
                tenanted environment.

        Returns:
            dict with a message about successful index creation
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(
                    PROCESS_DATA_INDEX_ENDPOINT,
                    {
                        "splitter": splitter,
                        "filename": file_name,
                        "guid": data_index_guid,
                    },
                )
            except ClientResponseError as e:
                # TODO differentiate between missing data_index and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise WorkspaceOrUserNotFoundError()

                raise UnknownKluAPIError(e.status, e.message)
            except Exception:
                raise UnknownKluError()

            return {"message": response.get("msg")}

    async def upload_index_file(self, file_data: FileData) -> str:
        """
        Upload system file to Klu storage for later usage in data_index creation. Maximum supported file size is 50 MB.

        Args:
            file_data (FileData): Metadata of the file to be uploaded. For more details, see the FileData class docs.

        Returns:
            URL to the uploaded file. This URL should be used during the data_index creation flow.
        """
        async with aiohttp.ClientSession() as session:
            pre_signed_url_data = await self.get_index_upload_pre_signed_url(
                file_data.file_name
            )
            await upload_to_pre_signed_url(
                session, pre_signed_url_data, file_data.file_path
            )

            return pre_signed_url_data.object_url

    async def get_index_upload_pre_signed_url(
        self, file_name: str
    ) -> PreSignUrlPostData:
        """
        Get pre-signed url to upload files to use for data_indexes creation. Maximum supported file size is 50 MB.
        This method should only be used if you don't want to use `upload_model_file` function to upload the file without
        the need to get into pre_signed_url upload flow.

        Args:
            file_name (str): The name of the file to be uploaded. Has to be unique among the files you uploaded before.
                Otherwise, the new file will override the previously uploaded one by the same file_name

        Returns:
            pre-signed url data including url, which is the pre-signed url that can be used to upload the file.
            Also includes 'fields' property that contains dict with data that
            has to be passed alongside the file during the upload
            And object_url property that contains the url that can be used to access the file location after the upload.
            This same object_url can be used during the data_index creation.
            For a usage example check out the `upload_index_file` function
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(
                    UPLOAD_PRE_SIGNED_URL_ENDPOINT,
                    {
                        "file_name": file_name,
                    },
                )
            except ClientResponseError as e:
                # TODO differentiate between missing data_index and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise WorkspaceOrUserNotFoundError()

                raise UnknownKluAPIError(e.status, e.message)

            return PreSignUrlPostData(**response)
