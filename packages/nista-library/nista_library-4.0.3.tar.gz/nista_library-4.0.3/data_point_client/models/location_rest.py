from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="LocationRest")


@attr.s(auto_attribs=True)
class LocationRest:
    """
    Attributes:
        discriminator (str):
    """

    discriminator: str

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        location_rest = cls(
            discriminator=discriminator,
        )

        return location_rest
