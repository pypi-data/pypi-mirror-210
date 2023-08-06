# mypy: disable-error-code="override"
from typing import List, Optional

import aiohttp
from aiohttp import ClientResponseError

from klu.action.models import Action
from klu.application.constants import (
    APPLICATION_ACTIONS_ENDPOINT,
    APPLICATION_DATA_ENDPOINT,
    APPLICATION_ENDPOINT,
    DEFAULT_APPS_PAGE_SIZE,
)
from klu.application.errors import ApplicationNotFoundError
from klu.application.models import Application
from klu.common.client import KluClientBase
from klu.common.errors import InvalidUpdateParamsError, UnknownKluAPIError
from klu.data.models import Data
from klu.utils.dict_helpers import dict_no_empty
from klu.utils.paginator import Paginator


class ApplicationsClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, APPLICATION_ENDPOINT, Application)
        self._paginator = Paginator(APPLICATION_ENDPOINT)

    async def create(self, name: str, app_type: str, description: str) -> Application:
        """
        Creates new application instance

        Args:
            name: str. Name of a new application
            app_type: str. Type of new application
            description: str. Description of a new application

        Returns:
            Newly created Application object
        """
        return await super().create(
            name=name,
            app_type=app_type,
            description=description,
        )

    async def get(self, guid: str) -> Application:
        """
        Retrieves app  information based on the app id.

        Args:
            guid (str): GUID of an application to fetch. The one that was used during the app creation

        Returns:
            Application object
        """
        return await super().get(guid)

    async def update(
        self,
        guid: str,
        name: Optional[str] = None,
        app_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Application:
        """
        Update application metadata. At least one of the params has to be provided

        Args:
            guid (str): GUID of an application to fetch. The one that was used during the app creation
            name: Optional[str]. New application name
            app_type: Optional[str]. New application type
            description: Optional[str]. New application description

        Returns:
            Updated application instance
        """

        if not name and not app_type and not description:
            raise InvalidUpdateParamsError()

        return await super().update(
            **{
                "guid": guid,
                **dict_no_empty(
                    {"name": name, "app_type": app_type, "description": description}
                ),
            }
        )

    async def delete(self, guid: str) -> Application:
        """
        Delete existing application information defined by the app id.

        Args:
            guid (str): The id of an application to delete.

        Returns:
            Deleted application object
        """
        return await super().delete(guid)

    async def get_app_data(self, app_guid: str) -> List[Data]:
        """
        Retrieves app data information based on the app GUID.

        Args:
            app_guid (str): GUID of an application to fetch data for. The one that was returned during the app creation

        Returns:
            An array of data objects, found by provided app id.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.get(
                    APPLICATION_DATA_ENDPOINT.format(id=app_guid)
                )
                return [Data._from_engine_format(data) for data in response]
            except ClientResponseError as e:
                if e.status == 404:
                    raise ApplicationNotFoundError(app_guid)

                raise UnknownKluAPIError(e.status, e.message)

    async def get_app_actions(self, app_guid: str) -> List[Action]:
        """
        Retrieves app actions information based on the app GUID.

        Args:
            app_guid (str): GUID of an application to fetch actions for. The one that was used during the app creation

        Returns:
            An array of actions, found by provided app id.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.get(
                    APPLICATION_ACTIONS_ENDPOINT.format(id=app_guid)
                )
                return [Action._from_engine_format(action) for action in response]
            except ClientResponseError as e:
                if e.status == 404:
                    raise ApplicationNotFoundError(app_guid)

                raise UnknownKluAPIError(e.status, e.message)

    async def list(self) -> List[Application]:
        """
        Retrieves all apps attached to a workspace.
        Does not rely on internal paginator state, so `reset_pagination` method call can be skipped

        Returns:
            An array of all apps
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_all(client)

            return [
                Application._from_engine_format(application) for application in response
            ]

    async def fetch_single_page(
        self, page_number, limit: int = DEFAULT_APPS_PAGE_SIZE
    ) -> List[Application]:
        """
        Retrieves a single page of applications.
        Can be used to fetch a specific page of applications provided a certain per_page config.
        Does not rely on internal paginator state, so `reset_pagination` method call can be skipped

        Args:
            page_number (int): Number of the page to fetch
            limit (int): Number of instances to fetch per page. Defaults to 50

        Returns:
            An array of apps fetched for a queried page. Empty if queried page does not exist
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_single_page(
                client, page_number, limit=limit
            )

            return [
                Application._from_engine_format(application) for application in response
            ]

    async def fetch_next_page(
        self, limit: int = DEFAULT_APPS_PAGE_SIZE, offset: Optional[int] = None
    ) -> List[Application]:
        """
        Retrieves the next page of applications. Can be used to fetch a flexible number of pages starting.
        The place to start from can be controlled by the offset parameter.
        After using this method, we suggest to call `reset_pagination` method to reset the page cursor.

        Args:
            limit (int): Number of instances to fetch per page. Defaults to 50
            offset (int): The number of apps to skip. Can be used to query the pages of applications skipping certain number of instances.

        Returns:
            An array of apps fetched for a queried page. Empty if the end was reached at the previous step.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_next_page(
                client, limit=limit, offset=offset
            )

            return [
                Application._from_engine_format(application) for application in response
            ]

    async def reset_pagination(self):
        self._paginator = Paginator(APPLICATION_ENDPOINT)
