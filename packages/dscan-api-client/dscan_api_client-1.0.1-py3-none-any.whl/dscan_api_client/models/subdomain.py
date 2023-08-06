import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Subdomain")


@attr.s(auto_attribs=True)
class Subdomain:
    """
    Attributes:
        id (int):
        name (str):
        is_primary (bool):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        status (Union[Unset, int]):
        enabled (Union[Unset, bool]):
        program (Union[Unset, None, int]):
        scan (Union[Unset, None, int]):
    """

    id: int
    name: str
    is_primary: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: Union[Unset, int] = UNSET
    enabled: Union[Unset, bool] = UNSET
    program: Union[Unset, None, int] = UNSET
    scan: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        is_primary = self.is_primary
        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        status = self.status
        enabled = self.enabled
        program = self.program
        scan = self.scan

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "is_primary": is_primary,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if program is not UNSET:
            field_dict["program"] = program
        if scan is not UNSET:
            field_dict["scan"] = scan

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        is_primary = d.pop("is_primary")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        status = d.pop("status", UNSET)

        enabled = d.pop("enabled", UNSET)

        program = d.pop("program", UNSET)

        scan = d.pop("scan", UNSET)

        subdomain = cls(
            id=id,
            name=name,
            is_primary=is_primary,
            created_at=created_at,
            updated_at=updated_at,
            status=status,
            enabled=enabled,
            program=program,
            scan=scan,
        )

        subdomain.additional_properties = d
        return subdomain

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
