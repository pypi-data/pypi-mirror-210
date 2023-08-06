from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProgramSubdomainCheck")


@attr.s(auto_attribs=True)
class ProgramSubdomainCheck:
    """
    Attributes:
        data_blob (str):
        scan_id (Union[Unset, str]):
    """

    data_blob: str
    scan_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data_blob = self.data_blob
        scan_id = self.scan_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_blob": data_blob,
            }
        )
        if scan_id is not UNSET:
            field_dict["scan_id"] = scan_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_blob = d.pop("data_blob")

        scan_id = d.pop("scan_id", UNSET)

        program_subdomain_check = cls(
            data_blob=data_blob,
            scan_id=scan_id,
        )

        program_subdomain_check.additional_properties = d
        return program_subdomain_check

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
