from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Optional


class BasicEnum(Enum):
    """
    Basic class for enums across the projects. Adds basic functions to list names and values.
    Overrides comparison function to allow comparing against string values.
    """

    __hash__ = Enum.__hash__

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other.upper()
        return super().__eq__(other)

    @classmethod
    def list_values(cls) -> list:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_names(cls) -> list:
        return list(map(lambda c: c.name, cls))


class BasicStringEnum(str, BasicEnum):
    """
    Basic class for string-based enums across the projects.
    Allows to have human-readable representation of enum as a value and convert between such value and key.
    """

    def __str__(self):
        return self.value

    @classmethod
    def get(cls, member: str) -> Optional["BasicStringEnum"]:
        """
        Get a member of an Enum by its string representation
        """
        member = member.upper().replace(" ", "_")
        try:
            return cls.__members__[member]
        except KeyError:
            return None

    def get_human_string(self):
        return self.value.replace("_", " ").capitalize() if self.value else None


class BaseDataClass:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    """
        This is the function that helps us to create an object in a way that any unknown kwargs passed will be ignored
    """

    @classmethod
    def _create_instance(cls, **kwargs):
        instance = cls.__new__(cls)
        instance._init_with_base_class(**kwargs)
        return instance

    def _init_with_base_class(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class BaseEngineModel(BaseDataClass, metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def _from_engine_format(cls, data: dict) -> "BaseEngineModel":
        pass

    @abstractmethod
    def _to_engine_format(self) -> dict:
        pass
