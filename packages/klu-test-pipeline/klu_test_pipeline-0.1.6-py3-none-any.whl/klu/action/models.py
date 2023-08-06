"""
This module provides data models for the Action.
"""
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from klu.common.models import BaseDataClass, BaseEngineModel


@dataclass
class Action(BaseEngineModel):
    """
    This class represents the Action data model returned from the Klu engine
    """

    guid: str
    name: str
    prompt: str
    app_id: int
    model_id: int
    action_type: str
    description: Optional[str]
    model_config: Optional[dict]
    experiment_id: Optional[int] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @classmethod
    def _from_engine_format(cls, data: dict) -> "Action":
        return cls._create_instance(
            **{
                "app_id": data.pop("appId", None),
                "model_id": data.pop("modelId", None),
                "updated_at": data.pop("updatedAt", None),
                "created_at": data.pop("createdAt", None),
                "action_type": data.pop("agent_type", None),
                "experiment_id": data.pop("experimentId", None),
            },
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(self)

        return {
            "appId": base_dict.pop("app_id", None),
            "modelId": base_dict.pop("model_id", None),
            "updatedAt": base_dict.pop("updated_at", None),
            "createdAt": base_dict.pop("created_at", None),
            "agent_type": base_dict.pop("action_type", None),
            "experimentId": base_dict.pop("experiment_id", None),
            **base_dict,
        }


@dataclass
class PromptResponse(BaseDataClass):
    """
    This class represents the Response data model returned from the Klu engine in response to action prompting.
    """

    msg: str
    streaming: bool
    result_url: Optional[str] = None
    feedback_url: Optional[str] = None
    streaming_url: Optional[str] = None
