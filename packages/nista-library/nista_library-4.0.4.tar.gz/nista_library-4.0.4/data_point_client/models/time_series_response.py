from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.time_series_response_curve import TimeSeriesResponseCurve


T = TypeVar("T", bound="TimeSeriesResponse")


@attr.s(auto_attribs=True)
class TimeSeriesResponse:
    """
    Attributes:
        discriminator (str):
        series_id (Union[Unset, str]):
        curve (Union[Unset, None, TimeSeriesResponseCurve]):
    """

    discriminator: str
    series_id: Union[Unset, str] = UNSET
    curve: Union[Unset, None, "TimeSeriesResponseCurve"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        series_id = self.series_id
        curve: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.curve, Unset):
            curve = self.curve.to_dict() if self.curve else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if series_id is not UNSET:
            field_dict["seriesId"] = series_id
        if curve is not UNSET:
            field_dict["curve"] = curve

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_series_response_curve import TimeSeriesResponseCurve

        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        series_id = d.pop("seriesId", UNSET)

        _curve = d.pop("curve", UNSET)
        curve: Union[Unset, None, TimeSeriesResponseCurve]
        if _curve is None:
            curve = None
        elif isinstance(_curve, Unset):
            curve = UNSET
        else:
            curve = TimeSeriesResponseCurve.from_dict(_curve)

        time_series_response = cls(
            discriminator=discriminator,
            series_id=series_id,
            curve=curve,
        )

        time_series_response.additional_properties = d
        return time_series_response

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
