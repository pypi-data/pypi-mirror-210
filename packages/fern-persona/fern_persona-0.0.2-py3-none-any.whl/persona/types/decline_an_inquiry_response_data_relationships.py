# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

import pydantic

from ..core.datetime_utils import serialize_datetime
from .decline_an_inquiry_response_data_relationships_account import DeclineAnInquiryResponseDataRelationshipsAccount
from .decline_an_inquiry_response_data_relationships_reports import DeclineAnInquiryResponseDataRelationshipsReports
from .decline_an_inquiry_response_data_relationships_template import DeclineAnInquiryResponseDataRelationshipsTemplate
from .decline_an_inquiry_response_data_relationships_verifications import (
    DeclineAnInquiryResponseDataRelationshipsVerifications,
)


class DeclineAnInquiryResponseDataRelationships(pydantic.BaseModel):
    account: typing.Optional[DeclineAnInquiryResponseDataRelationshipsAccount]
    template: typing.Optional[DeclineAnInquiryResponseDataRelationshipsTemplate]
    reports: typing.Optional[DeclineAnInquiryResponseDataRelationshipsReports]
    verifications: typing.Optional[DeclineAnInquiryResponseDataRelationshipsVerifications]

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        json_encoders = {dt.datetime: serialize_datetime}
