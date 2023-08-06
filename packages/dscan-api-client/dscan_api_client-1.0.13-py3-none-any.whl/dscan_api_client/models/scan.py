import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.status_enum import StatusEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="Scan")


@attr.s(auto_attribs=True)
class Scan:
    """
    Attributes:
        id (int):
        name (str):
        status (StatusEnum): * `0` - Just Added - Will be Scheduled Soon
            * `1` - Scheduled/Started Enum Phase
            * `2` - Ready for HTTPX
            * `3` - HTTPX Started/Ongoing
            * `4` - Ready for Nuclei
            * `5` - Nuclei Started
            * `6` - Scan Finished
        issues_found (Union[Unset, None, int]):
        comment (Union[Unset, None, str]):
        created_at (Optional[datetime.datetime]):
        updated_at (Optional[datetime.datetime]):
        reason (Union[Unset, None, str]):
        s_type (Union[Unset, None, str]):
        n_type (Union[Unset, None, str]):
        program (Union[Unset, None, int]):
    """

    id: int
    name: str
    status: StatusEnum
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    issues_found: Union[Unset, None, int] = UNSET
    comment: Union[Unset, None, str] = UNSET
    reason: Union[Unset, None, str] = UNSET
    s_type: Union[Unset, None, str] = UNSET
    n_type: Union[Unset, None, str] = UNSET
    program: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        status = self.status.value

        issues_found = self.issues_found
        comment = self.comment
        created_at = self.created_at.isoformat() if self.created_at else None

        updated_at = self.updated_at.isoformat() if self.updated_at else None

        reason = self.reason
        s_type = self.s_type
        n_type = self.n_type
        program = self.program

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if issues_found is not UNSET:
            field_dict["issues_found"] = issues_found
        if comment is not UNSET:
            field_dict["comment"] = comment
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
        id = d.pop("id")

        name = d.pop("name")

        status = StatusEnum(d.pop("status"))

        issues_found = d.pop("issues_found", UNSET)

        comment = d.pop("comment", UNSET)

        _created_at = d.pop("created_at")
        created_at: Optional[datetime.datetime]
        if _created_at is None:
            created_at = None
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at")
        updated_at: Optional[datetime.datetime]
        if _updated_at is None:
            updated_at = None
        else:
            updated_at = isoparse(_updated_at)

        reason = d.pop("reason", UNSET)

        s_type = d.pop("s_type", UNSET)

        n_type = d.pop("n_type", UNSET)

        program = d.pop("program", UNSET)

        scan = cls(
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

        scan.additional_properties = d
        return scan

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
