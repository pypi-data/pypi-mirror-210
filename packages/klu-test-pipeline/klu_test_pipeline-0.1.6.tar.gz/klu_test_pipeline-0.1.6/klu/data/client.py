# mypy: disable-error-code="override"
from typing import Optional

from klu.common.client import KluClientBase
from klu.data.constants import DATA_ENDPOINT
from klu.data.models import Data


class DataClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, DATA_ENDPOINT, Data)

    async def create(
        self,
        issue: str,
        input: str,
        output: str,
        action: str,
        rating: int,
        correction: str,
        action_guid: str,
        session_guid: str,
        meta_data: Optional[dict] = None,
    ) -> Data:
        """
        Creates new data instance for an action_id provided.

        Args:
            issue (str): Data issue
            input (str): Input value of action execution
            output (str): The result of action execution
            action (str): Data action value
            rating (int): Data rating
            action_guid (str): Guid of an action data belongs to
            session_guid (str): Guid of a session data belongs to
            meta_data (dict): Data meta_data
            correction (str): Data correction

        Returns:
            Created Data object
        """
        return await super().create(
            issue=issue,
            input=input,
            output=output,
            action=action,
            rating=rating,
            meta_data=meta_data,
            correction=correction,
            action_guid=action_guid,
            session_guid=session_guid,
        )

    async def get(self, guid: str) -> Data:
        """
        Retrieves data information based on the data ID.

        Args:
            guid (str): ID of a datum object to fetch.

        Returns:
            An object
        """
        return await super().get(guid)

    async def update(self, guid: str, output: str) -> Data:
        """
        Updated data information based on the data ID and provided payload. Currently, only supports `output` update.

        Args:
            guid (str): ID of a datum object to update.
            output (str): New 'output' data field value.

        Returns:
            Newly updated Data object
        """
        return await super().update(guid=guid, output=output)

    async def delete(self, guid: str) -> Data:
        return await super().delete(guid)
