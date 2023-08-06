# mypy: disable-error-code="override"
from typing import Optional

import aiohttp
from aiohttp import ClientResponseError

from klu.common.client import KluClientBase
from klu.common.errors import InvalidUpdateParamsError, UnknownKluAPIError
from klu.model.constants import MODEL_ENDPOINT
from klu.model.errors import UnknownModelProviderError
from klu.model.models import Model
from klu.utils.dict_helpers import dict_no_empty


class ModelsClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, MODEL_ENDPOINT, Model)

    async def create(self, llm: str, workspace_model_provider_id: int) -> Model:
        """
                Creates a model based on the data provided.

                Args:
                    llm (str): Model llm. Required
                    workspace_model_provider_id (str): Unique identifier of model provider.
                        Can be retrieved from a model providers listing endpoint.

                Returns:
        A newly created Model object.
        """
        return await super().create(
            llm=llm, workspaceModelProviderId=workspace_model_provider_id
        )

    async def get(self, guid: str) -> Model:
        """
        Retrieves model  information based on the id.

        Args:
            guid (str): GUID of a model to fetch. The one that was used during the model creation

        Returns:
            Model object
        """
        return await super().get(guid)

    async def update(
        self, guid: str, llm: Optional[str] = None, key: Optional[str] = None
    ) -> Model:
        """
        Update model data. At least one of the params has to be provided

        Args:
            guid (str): Guid of a data_index to update.
            llm: Optional[str]. New data_index name
            key: Optional[str]. New data_index description

        Returns:
            Updated application instance
        """
        if not llm and not key:
            raise InvalidUpdateParamsError()

        return await super().update(
            **{"guid": guid, **dict_no_empty({"llm": llm, "key": key})}
        )

    async def delete(self, guid: str) -> Model:
        """
        Delete model based on the id.

        Args:
            guid (str): ID of a model to delete.

        Returns:
            Deleted model object
        """
        return await super().delete(guid)

    async def validate_provider_api_key(self, api_key: str, provider: str) -> bool:
        """
        Validates API keys for provided api_key and provider values.

        Args:
            api_key (str): Model api_key
            provider (str): Model provider. Required. Should be one of the following: [OpenAI, HuggingFace, NLPCloud, GooseAI, AI21 & Anthropic]

        Returns:
            A JSON response with a message about successful creation if model was created.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(
                    MODEL_ENDPOINT,
                    {
                        "api_key": api_key,
                        "provider": provider,
                    },
                )
                return bool(response.get("validated"))
            except ClientResponseError as e:
                if e.status == 404:
                    raise UnknownModelProviderError(provider)

                raise UnknownKluAPIError(e.status, e.message)
