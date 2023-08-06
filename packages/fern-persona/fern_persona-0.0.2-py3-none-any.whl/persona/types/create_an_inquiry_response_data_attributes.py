# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

import pydantic

from ..core.datetime_utils import serialize_datetime


class CreateAnInquiryResponseDataAttributes(pydantic.BaseModel):
    status: typing.Optional[str]
    subject: typing.Optional[typing.Any]
    reference_id: typing.Optional[typing.Any] = pydantic.Field(alias="reference-id")
    created_at: typing.Optional[str] = pydantic.Field(alias="created-at")
    completed_at: typing.Optional[typing.Any] = pydantic.Field(alias="completed-at")
    expired_at: typing.Optional[typing.Any] = pydantic.Field(alias="expired-at")

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        allow_population_by_field_name = True
        json_encoders = {dt.datetime: serialize_datetime}
