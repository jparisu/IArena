from __future__ import annotations
from dataclasses import fields
from typing import Mapping, Any, TypeVar, Generic

YamlMapping = Mapping[str, Any]

T = TypeVar("T", bound="YamlMixing")

class YamlMixing(Generic[T]):
    """
    Abstract class to generate dataclasses that can be initialized from a YAML map.
    This class provides two methods:
    - update: update the instance attributes from a YAML map (in-place).
    - from_yaml: create a new instance from a YAML map (class method).

    Both methods ignore keys that do not correspond to any attribute of the dataclass.
    """

    def __init__(self, yaml: YamlMapping = None):
        if yaml is not None:
            self.update(yaml)


    def update(self: T, yaml: YamlMapping) -> T:
        allowed = {f.name for f in fields(self)}
        for k, v in yaml.items():
            if k in allowed:
                setattr(self, k, v)
        return self


    @classmethod
    def from_yaml(cls: type[T], yaml: YamlMapping) -> T:
        object = cls()
        object.update(yaml)
        return object
