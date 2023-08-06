import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.program import Program


T = TypeVar("T", bound="ScanDetailed")


@attr.s(auto_attribs=True)
class ScanDetailed:
    """
    Attributes:
        id (int):
        program (Program): Adds nested create feature
        name (str):
        status (int):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        issues_found (Union[Unset, None, int]):
        comment (Union[Unset, None, str]):
        reason (Union[Unset, None, str]):
        s_type (Union[Unset, None, str]):
        n_type (Union[Unset, None, str]):
    """

    id: int
    program: "Program"
    name: str
    status: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    issues_found: Union[Unset, None, int] = UNSET
    comment: Union[Unset, None, str] = UNSET
    reason: Union[Unset, None, str] = UNSET
    s_type: Union[Unset, None, str] = UNSET
    n_type: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        program = self.program.to_dict()

        name = self.name
        status = self.status
        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        issues_found = self.issues_found
        comment = self.comment
        reason = self.reason
        s_type = self.s_type
        n_type = self.n_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "program": program,
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

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.program import Program

        d = src_dict.copy()
        id = d.pop("id")

        program = Program.from_dict(d.pop("program"))

        name = d.pop("name")

        status = d.pop("status")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        issues_found = d.pop("issues_found", UNSET)

        comment = d.pop("comment", UNSET)

        reason = d.pop("reason", UNSET)

        s_type = d.pop("s_type", UNSET)

        n_type = d.pop("n_type", UNSET)

        scan_detailed = cls(
            id=id,
            program=program,
            name=name,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            issues_found=issues_found,
            comment=comment,
            reason=reason,
            s_type=s_type,
            n_type=n_type,
        )

        scan_detailed.additional_properties = d
        return scan_detailed

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
