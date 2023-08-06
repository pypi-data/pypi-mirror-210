# mypy: disable-error-code="override"
from typing import List, Optional

import aiohttp
from aiohttp import ClientResponseError

from klu.action.constants import (
    ACTION_DATA_ENDPOINT,
    ACTION_ENDPOINT,
    CREATE_ACTION_ENDPOINT,
    DEFAULT_ACTIONS_PAGE_SIZE,
    PLAYGROUND_PROMPT_ENDPOINT,
)
from klu.action.errors import ActionNotFoundError, InvalidActionPromptData
from klu.action.models import Action, PromptResponse
from klu.common.client import KluClientBase
from klu.common.errors import (
    InvalidUpdateParamsError,
    UnknownKluAPIError,
    UnknownKluError,
)
from klu.data.models import Data
from klu.utils.dict_helpers import dict_no_empty
from klu.utils.paginator import Paginator
from klu.workspace.errors import WorkspaceOrUserNotFoundError


class ActionsClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, ACTION_ENDPOINT, Action)
        self._paginator = Paginator(ACTION_ENDPOINT)

    # type: ignore
    async def create(
        self,
        name: str,
        prompt: str,
        app_guid: str,
        model_guid: str,
        action_type: str,
        description: str,
        model_config: Optional[dict] = None,
    ) -> Action:
        """
        Creates new action instance

        Args:
            name (str): Action name
            prompt (str): Action prompt
            model_guid (int): Guid of a model used for action
            app_guid (str): GUID of the application for an action to be attached to
            action_type (str): The type of the action. Can be one of [simple, complex, document-search, full-ai, custom]
            description (str): The description of the action
            model_config (str): Optional action model configuration dict

        Returns:
            Newly created Action object
        """
        return await super().create(
            name=name,
            prompt=prompt,
            app_guid=app_guid,
            model_guid=model_guid,
            agent_type=action_type,
            description=description,
            model_config=model_config,
            url=CREATE_ACTION_ENDPOINT,
        )

    # type: ignore
    async def get(self, guid: str) -> Action:
        """
        Get an action defined by the id

        Args:
            guid (str): The id of an action to retrieve

        Returns:
            Retrieved Action object.
        """
        return await super().get(guid)

    # type: ignore
    async def update(
        self,
        guid: str,
        name: Optional[str] = None,
        prompt: Optional[str] = None,
        description: Optional[str] = None,
        model_config: Optional[str] = None,
    ) -> Action:
        """
        Update action instance with provided data. At least one of parameters should be present.

        Args:
            guid (str): The GUID of the action to update.
            name: Optional[str]. New action name.
            prompt: Optional[str]. New action type.
            description: Optional[str]. New action description.
            model_config: Optional[dict]. New action model_config.

        Returns:
            Action with updated data
        """
        if not name and not prompt and not description and not model_config:
            raise InvalidUpdateParamsError()

        return await super().update(
            **{
                "guid": guid,
                **dict_no_empty(
                    {
                        "name": name,
                        "prompt": prompt,
                        "description": description,
                        "model_config": model_config,
                    }
                ),
            }
        )

    async def delete(self, guid: str) -> Action:
        """
        Delete an action defined by the id

        Args:
            guid (str): The id of an action to delete

        Returns:
            Deleted Action object.
        """
        return await super().delete(guid)

    async def run_action_prompt(
        self,
        action_guid: str,
        prompt: str,
        filter: Optional[str] = None,
        streaming: Optional[bool] = False,
        async_mode: Optional[bool] = False,
        session_guid: Optional[str] = None,
    ) -> PromptResponse:
        """
        Run a prompt with an agent, optionally using streaming.

        Args:
            action_guid (str): The GUID of the agent to run the prompt with.
            prompt (str): The prompt to run with the agent.
            filter (Optional[str]): The filter to use when running the prompt.
            session_guid (Optional[str]): The GUID of the session to run the prompt with.
            streaming (Optional[bool]): Flag that defines whether to use streaming or not.
            async_mode (Optional[bool]): Boolean that identifies whether the async mode should be used. Defaults to False.

        Returns:
            An object result of running the prompt with the message and a feedback_url for providing feedback.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)

            try:
                response = await client.post(
                    ACTION_ENDPOINT,
                    {
                        "prompt": prompt,
                        "filter": filter,
                        "action": action_guid,
                        "streaming": streaming,
                        "async_mode": async_mode,
                        "sessionGuid": session_guid,
                    },
                )
                return PromptResponse(**response)
            except ClientResponseError as e:
                if e.status == 404:
                    raise ActionNotFoundError(action_guid)

                raise UnknownKluAPIError(e.status, e.message)
            except Exception:
                raise UnknownKluError()

    async def run_playground_prompt(
        self,
        prompt: str,
        model_id: int,
        tool_ids: Optional[list] = None,
        index_ids: Optional[list] = None,
        model_config: Optional[dict] = None,
    ) -> PromptResponse:
        """
        Run a prompt with an agent, optionally using streaming.

        Args:
            prompt (str): The prompt to run.
            model_id (int): The ID of the model to use. Can be retrieved by querying the model by guid
            tool_ids (list): Optional list of tool IDs to use. Defaults to an empty array
            index_ids (list): Optional list of index IDs to use. Defaults to an empty array
            model_config (dict): Optional configuration of the model

        Returns:
            An object result of running the prompt with the message and a feedback_url for providing feedback.
        """
        tool_ids = tool_ids or []
        index_ids = index_ids or []

        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)

            try:
                response = await client.post(
                    PLAYGROUND_PROMPT_ENDPOINT,
                    {
                        "prompt": prompt,
                        "toolIds": tool_ids,
                        "modelId": model_id,
                        "indexIds": index_ids,
                        "modelConfig": model_config,
                    },
                )
                return PromptResponse(**response)
            except ClientResponseError as e:
                if e.status == 404:
                    raise WorkspaceOrUserNotFoundError()
                if e.status == 400:
                    raise InvalidActionPromptData(e.message)

                raise UnknownKluAPIError(e.status, e.message)
            except Exception:
                raise UnknownKluError()

    async def get_action_data(self, guid: str) -> List[Data]:
        """
        Retrieves data information for an action.

        Args:
            guid (str): Guid of an action to fetch data for.

        Returns:
            An array of actions found by provided app id.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)

            try:
                response = await client.get(ACTION_DATA_ENDPOINT.format(id=guid))
                return [Data._from_engine_format(data) for data in response]
            except ClientResponseError as e:
                if e.status == 404:
                    raise ActionNotFoundError(guid)

                raise UnknownKluAPIError(e.status, e.message)
            except Exception:
                raise UnknownKluError()

    async def list(self) -> List[Action]:
        """
        Retrieves all actions for a user represented by the used API_KEY.
        Does not rely on internal paginator state, so `reset_pagination` method call can be skipped

        Returns (List[Action]): An array of all actions
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_all(client)

            return [Action._from_engine_format(action) for action in response]

    async def fetch_single_page(
        self, page_number, limit: int = DEFAULT_ACTIONS_PAGE_SIZE
    ) -> List[Action]:
        """
        Retrieves a single page of actions.
        Can be used to fetch a specific page of actions provided a certain per_page config.
        Does not rely on internal paginator state, so `reset_pagination` method call can be skipped

        Args:
            page_number (int): Number of the page to fetch
            limit (int): Number of instances to fetch per page. Defaults to 50

        Returns:
            An array of actions fetched for a queried page. Empty if queried page does not exist
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_single_page(
                client, page_number, limit=limit
            )

            return [Action._from_engine_format(action) for action in response]

    async def fetch_next_page(
        self, limit: int = DEFAULT_ACTIONS_PAGE_SIZE, offset: Optional[int] = None
    ) -> List[Action]:
        """
        Retrieves the next page of actions. Can be used to fetch a flexible number of pages starting.
        The place to start from can be controlled by the offset parameter.
        After using this method, we suggest to call `reset_pagination` method to reset the page cursor.

        Args:
            limit (int): Number of instances to fetch per page. Defaults to 50
            offset (int): The number of instances to skip. Can be used to query the pages of actions skipping certain number of instances.

        Returns:
            An array of actions fetched for a queried page. Empty if the end was reached at the previous step.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await self._paginator.fetch_next_page(
                client, limit=limit, offset=offset
            )

            return [Action._from_engine_format(action) for action in response]

    async def reset_pagination(self):
        self._paginator = Paginator(ACTION_ENDPOINT)
