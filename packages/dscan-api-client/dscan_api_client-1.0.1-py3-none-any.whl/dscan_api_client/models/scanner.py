import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Scanner")


@attr.s(auto_attribs=True)
class Scanner:
    """
    Attributes:
        id (int):
        name (str):
        s_type (str):
        enabled (bool):
        updated_at (datetime.datetime):
        config (Union[Unset, None, str]):
        comment (Union[Unset, None, str]):
        version (Union[Unset, None, str]):
    """

    id: int
    name: str
    s_type: str
    enabled: bool
    updated_at: datetime.datetime
    config: Union[Unset, None, str] = UNSET
    comment: Union[Unset, None, str] = UNSET
    version: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        s_type = self.s_type
        enabled = self.enabled
        updated_at = self.updated_at.isoformat()

        config = self.config
        comment = self.comment
        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "s_type": s_type,
                "enabled": enabled,
                "updated_at": updated_at,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config
        if comment is not UNSET:
            field_dict["comment"] = comment
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        s_type = d.pop("s_type")

        enabled = d.pop("enabled")

        updated_at = isoparse(d.pop("updated_at"))

        config = d.pop("config", UNSET)

        comment = d.pop("comment", UNSET)

        version = d.pop("version", UNSET)

        scanner = cls(
            id=id,
            name=name,
            s_type=s_type,
            enabled=enabled,
            updated_at=updated_at,
            config=config,
            comment=comment,
            version=version,
        )

        scanner.additional_properties = d
        return scanner

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
