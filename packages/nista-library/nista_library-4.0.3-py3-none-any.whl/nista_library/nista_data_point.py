import json
import uuid
from typing import Any, List, Optional, Type, TypeVar, Union

import pandas as pd
from pandas import DataFrame
from structlog import get_logger
from zoneinfo import ZoneInfo

from data_point_client import AuthenticatedClient
from data_point_client.api.data_point import (
    data_point_append_execution_result_data,
    data_point_append_time_series_data,
    data_point_create_data_point,
    data_point_get_data,
    data_point_get_data_point,
    data_point_update_constant_data,
    data_point_update_time_series_data,
    data_point_update_week_period_data,
)
from data_point_client.models import GetConstantResponse, GetSeriesResponse
from data_point_client.models.append_execution_result_data_request import (
    AppendExecutionResultDataRequest,
)
from data_point_client.models.data_point_response_base import DataPointResponseBase
from data_point_client.models.append_time_series_request import AppendTimeSeriesRequest
from data_point_client.models.data_point_request import DataPointRequest
from data_point_client.models.day_data_by_hour_transfer import DayDataByHourTransfer
from data_point_client.models.en_data_point_existence_dto import EnDataPointExistenceDTO
from data_point_client.models.get_data_request import GetDataRequest
from data_point_client.models.get_day_period_response import GetDayPeriodResponse
from data_point_client.models.get_week_period_response import GetWeekPeriodResponse
from data_point_client.models.problem_details import ProblemDetails
from data_point_client.models.sub_series_request import SubSeriesRequest
from data_point_client.models.sub_series_request_values import SubSeriesRequestValues
from data_point_client.models.time_series_response_curve import TimeSeriesResponseCurve
from data_point_client.models.update_constant_data_request import (
    UpdateConstantDataRequest,
)
from data_point_client.models.update_time_series_request import UpdateTimeSeriesRequest
from data_point_client.models.update_week_period_request import UpdateWeekPeriodRequest
from data_point_client.models.week_data_transfere import WeekDataTransfere
from data_point_client.types import Response, Unset
from nista_library.nista_connetion import NistaConnection

log = get_logger()

# pylint: disable=C0103
T = TypeVar("T", bound="NistaDataPoint")


class NistaDataPoint:
    """Represents a DataPoint from nista.io
    :DATE_FORMAT: Format to use for parse dictionaries
    :DATE_NAME: Column Name for Dates
    :VALUE_NAME: Column Name for Value
    """

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    DATE_NAME = "Date"
    VALUE_NAME = "Value"

    _data_point_response: Optional[DataPointResponseBase] = None

    @property
    def data_point_response(self) -> Optional[DataPointResponseBase]:
        """Loads and interprets the DataPoint if it has not bee loaded.
        :returns: The DataPoint Details from nista.io
        """
        if self._data_point_response is None:
            self._load_details()
        return self._data_point_response

    @classmethod
    def create_new(
        cls: Type[T], connection: NistaConnection, name: str, tags: List[str]
    ) -> Optional[T]:
        """Creates a new DataPoint in nista.io
        :param connection: To be used to connecto to nista.io
        :param name: The new name of the DataPoint
        :param tags: List of Tags to add to the new DataPoint
        :returns: The created DataPoint
        """

        token = connection.get_access_token()
        client = AuthenticatedClient(
            base_url=connection.datapoint_base_url,
            token=token,
            verify_ssl=connection.verify_ssl,
        )

        new_id = uuid.uuid4()
        request = DataPointRequest(
            name=name, description="", existence=EnDataPointExistenceDTO.FULL, tags=tags
        )

        response = data_point_create_data_point.sync(
            client=client,
            data_point_id=str(new_id),
            workspace_id=connection.workspace_id,
            json_body=request,
        )

        if isinstance(response, ProblemDetails):
            log.error(response)
            return None

        data_point = cls(connection=connection, data_point_id=new_id, name=name)
        return data_point

    def __init__(
        self,
        connection: NistaConnection,
        data_point_id: uuid.UUID,
        name: Optional[str] = None,
    ):
        """Load a DataPoint from nista.io
        :param connection: To be used to connecto to nista.io
        :param data_point_id: The Unique ID to load the DataPoint
        :param name: Optional Name to use for this DataPoint
        """

        self.connection = connection
        self.data_point_id = data_point_id
        if name is None:
            self._load_details()
        else:
            self.name = name

    def __str__(self):
        return "NistaDataPoint " + str(self.data_point_id) + " with name " + self.name

    def _load_details(self):
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
        )

        data_point = data_point_get_data_point.sync(
            client=client,
            data_point_id=self.data_point_id,
            workspace_id=self.connection.workspace_id,
        )

        if data_point is None:
            raise ValueError("Cannot load Datapoint")

        if isinstance(data_point, ProblemDetails):
            log.error(data_point)
            raise ValueError("Cannot load Datapoint")

        self._data_point_response = data_point
        self.name = self.data_point_response.name

    # pylint: disable=too-many-arguments
    def get_data_point_data(
        self,
        request: GetDataRequest,
        post_fix: bool = False,
        timeout: float = 30,
    ) -> Union[
        List[DataFrame], float, Unset, WeekDataTransfere, DayDataByHourTransfer, None
    ]:
        """Retrieves the Data from a DataPoint
        :param request: Request details for retrieving Data
        :param post_fix: Append nista.io instance name after DataPoint Name
        :param timeout: How long to wait for response
        :return: The DataPoint Data
        """

        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
            timeout=timeout,
        )

        byte_content = data_point_get_data.sync_detailed(
            client=client,
            data_point_id=str(self.data_point_id),
            workspace_id=self.connection.workspace_id,
            json_body=request,
        ).content

        log.debug("Received Response from nista.io", content=byte_content)

        content_text = byte_content.decode("utf-8")
        jscon_content = json.loads(content_text)

        content_type = jscon_content["discriminator"]

        if content_type == "GetSeriesResponse":
            series_response = GetSeriesResponse.from_dict(jscon_content)
            curves = series_response.curves

            if isinstance(curves, list):
                data_frames = []
                # pylint: disable=E1133
                for curve in curves:
                    # pylint: enable=E1133
                    curve_dict = curve.curve
                    if isinstance(curve_dict, TimeSeriesResponseCurve):
                        data_frame = self._from_time_frames(
                            time_frames=curve_dict.to_dict(), post_fix=post_fix
                        )
                        data_frames.append(data_frame)

                return data_frames

        if content_type == "GetConstantResponse":
            constant_response = GetConstantResponse.from_dict(jscon_content)
            if constant_response is not None:
                return constant_response.value

        if content_type == "GetWeekPeriodResponse":
            week_response = GetWeekPeriodResponse.from_dict(jscon_content)
            if week_response is not None:
                return week_response.week_data

        if content_type == "GetDayPeriodResponse":
            day_response = GetDayPeriodResponse.from_dict(jscon_content)
            if day_response is not None:
                return day_response.day_data

        return None

    def append_data_point_data(
        self,
        data: Union[List[DataFrame], float],
        unit: Optional[str] = None,
        timeout: float = 5.0,
    ) -> Optional[Response[Union[Any, ProblemDetails]]]:
        """Append data to an existing DataPoint
        :param data: To be added to a DataPoint
        :param unit: The Unit to set on the DataPoint Store
        :param timeout: How long to wait for response
        """

        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
            timeout=timeout,
        )

        if isinstance(data, list):
            sub_series: List[SubSeriesRequest] = []
            for data_frame in data:
                data_dict = self._to_dict(data_frame)
                value = SubSeriesRequestValues.from_dict(src_dict=data_dict)
                request = SubSeriesRequest(values=value)
                sub_series.append(request)

            append_request = AppendTimeSeriesRequest(sub_series=sub_series, unit=unit)

            return data_point_append_time_series_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=append_request,
            )

        return None

    def append_data_point_result_parts(
        self,
        data: Union[List[DataFrame], float],
        unit: Optional[str],
        execution_id: uuid.UUID,
        timeout: float = 5.0,
    ) -> Optional[Response[Union[Any, ProblemDetails]]]:
        """Append data as an execution Result. This method is used for nista.io Internal Execution handling
        :param data: To be added to a DataPoint
        :param unit: The Unit to set on the DataPoint Store
        :param execution_id: the execution ID that this data is assignable to
        :param timeout: How long to wait for response
        """
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
            timeout=timeout,
        )

        if isinstance(data, list):
            sub_series: List[SubSeriesRequest] = []
            for data_frame in data:
                data_dict = self._to_dict(data_frame)
                value = SubSeriesRequestValues.from_dict(src_dict=data_dict)
                request = SubSeriesRequest(values=value)
                sub_series.append(request)

            append_request = AppendExecutionResultDataRequest(
                sub_series=sub_series, unit=unit, execution_id=str(execution_id)
            )

            return data_point_append_execution_result_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=append_request,
            )

        return None

    def set_data_point_data(
        self,
        data: Union[List[DataFrame], float, WeekDataTransfere],
        unit: Optional[str] = None,
        execution_id: Optional[str] = None,
        time_zone: Optional[ZoneInfo] = None,
    ) -> Optional[Response[Union[Any, ProblemDetails]]]:
        """Replace or Set DataPoint Data with new Data. This bumps the DataPoint Version
        :param data: To be added to a DataPoint
        :param unit: The Unit to set on the DataPoint Store
        :param execution_id: the execution ID that this data is assignable to
        :param time_zone: The Time Zone of the newly added Data
        """
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url,
            token=token,
            verify_ssl=self.connection.verify_ssl,
        )

        if isinstance(data, WeekDataTransfere):
            week_update_request = UpdateWeekPeriodRequest(
                execution_id=execution_id, unit=unit, week_data=data
            )
            return data_point_update_week_period_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=week_update_request,
            )

        if isinstance(data, list):
            sub_series: List[SubSeriesRequest] = []
            if time_zone is None:
                time_zone = ZoneInfo("UTC")

            for data_frame in data:
                data_dict = self._to_dict(data_frame)
                value = SubSeriesRequestValues.from_dict(src_dict=data_dict)
                request = SubSeriesRequest(values=value)
                sub_series.append(request)

            timeseries_update_request = UpdateTimeSeriesRequest(
                sub_series=sub_series,
                unit=unit,
                execution_id=execution_id,
                time_zone=time_zone.key,
            )

            return data_point_update_time_series_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=timeseries_update_request,
            )

        if isinstance(data, float):
            constant_request = UpdateConstantDataRequest(
                value=data,
                unit=unit,
                execution_id=execution_id,
            )

            return data_point_update_constant_data.sync_detailed(
                workspace_id=self.connection.workspace_id,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=constant_request,
            )

        return None

    def _to_dict(self, data_frame: DataFrame):
        result = {}
        dct = data_frame.to_dict()[self.VALUE_NAME]
        for key in dct.keys():
            value = dct[key]
            key_string = key.strftime(self.DATE_FORMAT)
            result[key_string] = value
        return result

    def _from_time_frames(
        self, time_frames: dict, post_fix: bool, date_format: str = DATE_FORMAT
    ) -> DataFrame:
        if not isinstance(time_frames, dict):
            raise TypeError

        value_column_name = self.name

        if value_column_name is None:
            value_column_name = self.VALUE_NAME

        if post_fix:
            value_column_name = (
                value_column_name + "_nista.io_" + str(self.data_point_id)
            )

        log.debug("Reading data as Pandas DataFrame")

        data_record = []
        for date in time_frames:
            value = time_frames[date]
            data_record.append({self.DATE_NAME: date, value_column_name: value})

        data_frame = pd.DataFrame.from_records(
            data_record, columns=[self.DATE_NAME, value_column_name]
        )

        data_frame[self.DATE_NAME] = pd.to_datetime(
            data_frame[self.DATE_NAME], format=date_format
        )

        data_frame[value_column_name] = pd.to_numeric(data_frame[value_column_name])

        data_frame = data_frame.set_index(data_frame[self.DATE_NAME])
        data_frame = data_frame.drop([self.DATE_NAME], axis=1)

        return data_frame
