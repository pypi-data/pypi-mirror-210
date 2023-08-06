import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.day_data_by_hour_transfer import DayDataByHourTransfer


T = TypeVar("T", bound="DayPeriodDataPointData")


@attr.s(auto_attribs=True)
class DayPeriodDataPointData:
    """
    Attributes:
        discriminator (str):
        status (Union[Unset, None, str]):
        error_message (Union[Unset, None, str]):
        unit (Union[Unset, None, str]):
        number_of_entries (Union[Unset, int]):
        day_data (Union[Unset, None, DayDataByHourTransfer]):
        date (Union[Unset, None, datetime.datetime]):
    """

    discriminator: str
    status: Union[Unset, None, str] = UNSET
    error_message: Union[Unset, None, str] = UNSET
    unit: Union[Unset, None, str] = UNSET
    number_of_entries: Union[Unset, int] = UNSET
    day_data: Union[Unset, None, "DayDataByHourTransfer"] = UNSET
    date: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        status = self.status
        error_message = self.error_message
        unit = self.unit
        number_of_entries = self.number_of_entries
        day_data: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.day_data, Unset):
            day_data = self.day_data.to_dict() if self.day_data else None

        date: Union[Unset, None, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat() if self.date else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if unit is not UNSET:
            field_dict["unit"] = unit
        if number_of_entries is not UNSET:
            field_dict["numberOfEntries"] = number_of_entries
        if day_data is not UNSET:
            field_dict["dayData"] = day_data
        if date is not UNSET:
            field_dict["date"] = date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.day_data_by_hour_transfer import DayDataByHourTransfer

        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        status = d.pop("status", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        unit = d.pop("unit", UNSET)

        number_of_entries = d.pop("numberOfEntries", UNSET)

        _day_data = d.pop("dayData", UNSET)
        day_data: Union[Unset, None, DayDataByHourTransfer]
        if _day_data is None:
            day_data = None
        elif isinstance(_day_data, Unset):
            day_data = UNSET
        else:
            day_data = DayDataByHourTransfer.from_dict(_day_data)

        _date = d.pop("date", UNSET)
        date: Union[Unset, None, datetime.datetime]
        if _date is None:
            date = None
        elif isinstance(_date, Unset):
            date = UNSET
        else:
            date = isoparse(_date)

        day_period_data_point_data = cls(
            discriminator=discriminator,
            status=status,
            error_message=error_message,
            unit=unit,
            number_of_entries=number_of_entries,
            day_data=day_data,
            date=date,
        )

        day_period_data_point_data.additional_properties = d
        return day_period_data_point_data

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
