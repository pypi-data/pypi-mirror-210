import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchedTask")


@attr.s(auto_attribs=True)
class PatchedTask:
    """
    Attributes:
        id (Union[Unset, int]):
        task_id (Union[Unset, str]):
        status (Union[Unset, str]):
        is_finished (Union[Unset, None, bool]):
        created_at (Union[Unset, datetime.datetime]):
        updated_at (Union[Unset, datetime.datetime]):
        task_name (Union[Unset, None, str]):
        scan (Union[Unset, None, int]):
    """

    id: Union[Unset, int] = UNSET
    task_id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    is_finished: Union[Unset, None, bool] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    task_name: Union[Unset, None, str] = UNSET
    scan: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        task_id = self.task_id
        status = self.status
        is_finished = self.is_finished
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        task_name = self.task_name
        scan = self.scan

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if task_id is not UNSET:
            field_dict["task_id"] = task_id
        if status is not UNSET:
            field_dict["status"] = status
        if is_finished is not UNSET:
            field_dict["is_finished"] = is_finished
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if task_name is not UNSET:
            field_dict["task_name"] = task_name
        if scan is not UNSET:
            field_dict["scan"] = scan

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        task_id = d.pop("task_id", UNSET)

        status = d.pop("status", UNSET)

        is_finished = d.pop("is_finished", UNSET)

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

        task_name = d.pop("task_name", UNSET)

        scan = d.pop("scan", UNSET)

        patched_task = cls(
            id=id,
            task_id=task_id,
            status=status,
            is_finished=is_finished,
            created_at=created_at,
            updated_at=updated_at,
            task_name=task_name,
            scan=scan,
        )

        patched_task.additional_properties = d
        return patched_task

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
