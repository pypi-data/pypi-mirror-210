import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchedScan")


@attr.s(auto_attribs=True)
class PatchedScan:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, str]):
        status (Union[Unset, int]):
        issues_found (Union[Unset, None, int]):
        comment (Union[Unset, None, str]):
        created_at (Union[Unset, datetime.datetime]):
        updated_at (Union[Unset, datetime.datetime]):
        reason (Union[Unset, None, str]):
        s_type (Union[Unset, None, str]):
        n_type (Union[Unset, None, str]):
        program (Union[Unset, None, int]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    status: Union[Unset, int] = UNSET
    issues_found: Union[Unset, None, int] = UNSET
    comment: Union[Unset, None, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    reason: Union[Unset, None, str] = UNSET
    s_type: Union[Unset, None, str] = UNSET
    n_type: Union[Unset, None, str] = UNSET
    program: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        status = self.status
        issues_found = self.issues_found
        comment = self.comment
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        reason = self.reason
        s_type = self.s_type
        n_type = self.n_type
        program = self.program

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status
        if issues_found is not UNSET:
            field_dict["issues_found"] = issues_found
        if comment is not UNSET:
            field_dict["comment"] = comment
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if reason is not UNSET:
            field_dict["reason"] = reason
        if s_type is not UNSET:
            field_dict["s_type"] = s_type
        if n_type is not UNSET:
            field_dict["n_type"] = n_type
        if program is not UNSET:
            field_dict["program"] = program

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        status = d.pop("status", UNSET)

        issues_found = d.pop("issues_found", UNSET)

        comment = d.pop("comment", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        reason = d.pop("reason", UNSET)

        s_type = d.pop("s_type", UNSET)

        n_type = d.pop("n_type", UNSET)

        program = d.pop("program", UNSET)

        patched_scan = cls(
            id=id,
            name=name,
            status=status,
            issues_found=issues_found,
            comment=comment,
            created_at=created_at,
            updated_at=updated_at,
            reason=reason,
            s_type=s_type,
            n_type=n_type,
            program=program,
        )

        patched_scan.additional_properties = d
        return patched_scan

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
