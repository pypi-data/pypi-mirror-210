from typing import Any, Dict, List, Type, TypeVar, cast

import attr

T = TypeVar("T", bound="ProgramSubdomainCheck")


@attr.s(auto_attribs=True)
class ProgramSubdomainCheck:
    """
    Attributes:
        subdomains (List[Any]):
    """

    subdomains: List[Any]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        subdomains = self.subdomains

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "subdomains": subdomains,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        subdomains = cast(List[Any], d.pop("subdomains"))

        program_subdomain_check = cls(
            subdomains=subdomains,
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
