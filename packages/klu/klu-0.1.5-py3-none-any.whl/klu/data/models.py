from abc import ABC
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from klu.common.models import BaseEngineModel


@dataclass
class DataWithId(BaseEngineModel, ABC):
    id: int
    guid: str


@dataclass
class DataWithFeedbackUrl(BaseEngineModel, ABC):
    feedback_url: int


@dataclass
class DataBaseClass(BaseEngineModel):
    issue: Optional[int] = None
    input: Optional[str] = None
    action: Optional[int] = None
    output: Optional[str] = None
    rating: Optional[int] = None
    metadata: Optional[dict] = None
    correction: Optional[str] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @classmethod
    def _from_engine_format(cls, data: dict) -> "DataBaseClass":
        return cls._create_instance(
            **{
                "updated_at": data.pop("updatedAt", None),
                "created_at": data.pop("createdAt", None),
            },
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})

        base_dict.pop("updated_at", None)
        base_dict.pop("created_at", None)

        return base_dict


# We need this way of inheritance to append optional field after the required ones.
@dataclass
class Data(DataBaseClass, DataWithId):
    @classmethod
    def _from_engine_format(cls, data: dict) -> "Data":
        return cls._create_instance(
            **{
                "updated_at": data.pop("updatedAt", None),
                "created_at": data.pop("createdAt", None),
            },
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})

        base_dict.pop("updated_at", None)
        base_dict.pop("created_at", None)

        return base_dict


@dataclass
class ActionData(DataBaseClass, DataWithFeedbackUrl):
    @classmethod
    def _from_engine_format(cls, data: dict) -> "ActionData":
        return cls._create_instance(
            **{
                "updated_at": data.pop("updatedAt", None),
                "created_at": data.pop("createdAt", None),
            },
            **data,
        )

    def _to_engine_format(self) -> dict:
        base_dict = asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})

        base_dict.pop("updated_at", None)
        base_dict.pop("created_at", None)

        return base_dict
