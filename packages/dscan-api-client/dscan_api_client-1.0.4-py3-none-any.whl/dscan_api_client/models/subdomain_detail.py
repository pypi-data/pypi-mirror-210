import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="SubdomainDetail")


@attr.s(auto_attribs=True)
class SubdomainDetail:
    """
    Attributes:
        id (int):
        is_online (bool):
        created_at (datetime.datetime):
        status_code (Union[Unset, None, int]):
        content_length (Union[Unset, None, int]):
        content_type (Union[Unset, None, str]):
        asn_info (Union[Unset, None, str]):
        cdn (Union[Unset, None, str]):
        technology (Union[Unset, None, str]):
        title (Union[Unset, None, str]):
        url (Union[Unset, None, str]):
        subdomain (Union[Unset, None, int]):
    """

    id: int
    is_online: bool
    created_at: datetime.datetime
    status_code: Union[Unset, None, int] = UNSET
    content_length: Union[Unset, None, int] = UNSET
    content_type: Union[Unset, None, str] = UNSET
    asn_info: Union[Unset, None, str] = UNSET
    cdn: Union[Unset, None, str] = UNSET
    technology: Union[Unset, None, str] = UNSET
    title: Union[Unset, None, str] = UNSET
    url: Union[Unset, None, str] = UNSET
    subdomain: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        is_online = self.is_online
        created_at = self.created_at.isoformat()

        status_code = self.status_code
        content_length = self.content_length
        content_type = self.content_type
        asn_info = self.asn_info
        cdn = self.cdn
        technology = self.technology
        title = self.title
        url = self.url
        subdomain = self.subdomain

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "is_online": is_online,
                "created_at": created_at,
            }
        )
        if status_code is not UNSET:
            field_dict["status_code"] = status_code
        if content_length is not UNSET:
            field_dict["content_length"] = content_length
        if content_type is not UNSET:
            field_dict["content_type"] = content_type
        if asn_info is not UNSET:
            field_dict["asn_info"] = asn_info
        if cdn is not UNSET:
            field_dict["cdn"] = cdn
        if technology is not UNSET:
            field_dict["technology"] = technology
        if title is not UNSET:
            field_dict["title"] = title
        if url is not UNSET:
            field_dict["url"] = url
        if subdomain is not UNSET:
            field_dict["subdomain"] = subdomain

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        is_online = d.pop("is_online")

        created_at = isoparse(d.pop("created_at"))

        status_code = d.pop("status_code", UNSET)

        content_length = d.pop("content_length", UNSET)

        content_type = d.pop("content_type", UNSET)

        asn_info = d.pop("asn_info", UNSET)

        cdn = d.pop("cdn", UNSET)

        technology = d.pop("technology", UNSET)

        title = d.pop("title", UNSET)

        url = d.pop("url", UNSET)

        subdomain = d.pop("subdomain", UNSET)

        subdomain_detail = cls(
            id=id,
            is_online=is_online,
            created_at=created_at,
            status_code=status_code,
            content_length=content_length,
            content_type=content_type,
            asn_info=asn_info,
            cdn=cdn,
            technology=technology,
            title=title,
            url=url,
            subdomain=subdomain,
        )

        subdomain_detail.additional_properties = d
        return subdomain_detail

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
