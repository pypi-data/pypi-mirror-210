"""
This module provides data models for the Model.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from klu.common.models import BaseEngineModel


@dataclass
class Model(BaseEngineModel):
    """
    This class represents the Model data returned from the Klu engine
    """

    id: int
    llm: str
    guid: str
    model_name: str
    created_by_id: str
    workspace_model_provider_id: int
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @classmethod
    def _from_engine_format(cls, data: dict) -> "Model":
        return cls._create_instance(
            **{
                "updated_at": data.pop("updatedAt", None),
                "created_at": data.pop("createdAt", None),
                "created_by_id": data.pop("createdById", None),
                "workspace_model_provider_id": data.pop(
                    "workspaceModelProviderId", None
                ),
            },
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )

        base_dict.pop("updated_at", None)
        base_dict.pop("created_at", None)
        base_dict.pop("created_by_id", None)
        base_dict.pop("workspace_model_provider_id", None)

        return base_dict
