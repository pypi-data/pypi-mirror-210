# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

import pydantic

from ..core.datetime_utils import serialize_datetime
from .report_action_resume_continuous_monitoring_response_data_relationships_report_template_data import (
    ReportActionResumeContinuousMonitoringResponseDataRelationshipsReportTemplateData,
)


class ReportActionResumeContinuousMonitoringResponseDataRelationshipsReportTemplate(pydantic.BaseModel):
    data: typing.Optional[ReportActionResumeContinuousMonitoringResponseDataRelationshipsReportTemplateData]

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        json_encoders = {dt.datetime: serialize_datetime}
