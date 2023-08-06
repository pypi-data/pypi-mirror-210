import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Task")


@attr.s(auto_attribs=True)
class Task:
    """
    Attributes:
        id (int):
        task_id (str):
        status (str):
        is_finished (Union[Unset, None, bool]):
        created_at (Optional[datetime.datetime]):
        updated_at (Optional[datetime.datetime]):
        task_name (Union[Unset, None, str]):
        scan (Union[Unset, None, int]):
    """

    id: int
    task_id: str
    status: str
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    is_finished: Union[Unset, None, bool] = UNSET
    task_name: Union[Unset, None, str] = UNSET
    scan: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        task_id = self.task_id
        status = self.status
        is_finished = self.is_finished
        created_at = self.created_at.isoformat() if self.created_at else None

        updated_at = self.updated_at.isoformat() if self.updated_at else None

        task_name = self.task_name
        scan = self.scan

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "task_id": task_id,
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if is_finished is not UNSET:
            field_dict["is_finished"] = is_finished
        if task_name is not UNSET:
            field_dict["task_name"] = task_name
        if scan is not UNSET:
            field_dict["scan"] = scan

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        task_id = d.pop("task_id")

        status = d.pop("status")

        is_finished = d.pop("is_finished", UNSET)

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

        task_name = d.pop("task_name", UNSET)

        scan = d.pop("scan", UNSET)

        task = cls(
            id=id,
            task_id=task_id,
            status=status,
            is_finished=is_finished,
            created_at=created_at,
            updated_at=updated_at,
            task_name=task_name,
            scan=scan,
        )

        task.additional_properties = d
        return task

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
