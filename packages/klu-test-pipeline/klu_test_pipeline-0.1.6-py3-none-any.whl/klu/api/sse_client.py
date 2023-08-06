import json
from typing import AsyncIterator

from aiohttp_sse_client import client as sse_client

from klu.api.constants import (
    BEGIN_STREAM_CONTENT,
    END_STREAM_CONTENT,
    NO_MESSAGES_CONTENT,
)
from klu.common.errors import UnknownKluError


class SSEClient:
    @staticmethod
    async def get_streaming_data(streaming_url: str) -> AsyncIterator[str]:
        """
        Get a streams of messages from an SQS queue for a specific channel.

        Args:
            streaming_url (str): The url you received from run_action_prompt with streaming param set to True.

        Returns:
            An asynchronous generator, which can be used to read chunks of data from the streaming url. Usage example:
                async for chunk in get_streaming_data():
                    # Process the chunk of data here
        """
        try:
            async with sse_client.EventSource(streaming_url) as event_source:
                async for event in event_source:
                    message = event.data
                    if message == END_STREAM_CONTENT or message == NO_MESSAGES_CONTENT:
                        await event_source.close()
                        break

                    if message != BEGIN_STREAM_CONTENT:
                        token = json.loads(message)["token"]
                        yield token
        except Exception:
            raise UnknownKluError()
