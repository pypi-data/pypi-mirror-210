import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.domain import Domain


T = TypeVar("T", bound="Program")


@attr.s(auto_attribs=True)
class Program:
    """Adds nested create feature

    Attributes:
        id (int):
        name (str):
        url (str):
        bounty (bool):
        enabled (bool):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        domain (Union[Unset, List['Domain']]):
    """

    id: int
    name: str
    url: str
    bounty: bool
    enabled: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    domain: Union[Unset, List["Domain"]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        url = self.url
        bounty = self.bounty
        enabled = self.enabled
        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        domain: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.domain, Unset):
            domain = []
            for domain_item_data in self.domain:
                domain_item = domain_item_data.to_dict()

                domain.append(domain_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "url": url,
                "bounty": bounty,
                "enabled": enabled,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if domain is not UNSET:
            field_dict["domain"] = domain

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.domain import Domain

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        url = d.pop("url")

        bounty = d.pop("bounty")

        enabled = d.pop("enabled")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        domain = []
        _domain = d.pop("domain", UNSET)
        for domain_item_data in _domain or []:
            domain_item = Domain.from_dict(domain_item_data)

            domain.append(domain_item)

        program = cls(
            id=id,
            name=name,
            url=url,
            bounty=bounty,
            enabled=enabled,
            created_at=created_at,
            updated_at=updated_at,
            domain=domain,
        )

        program.additional_properties = d
        return program

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
