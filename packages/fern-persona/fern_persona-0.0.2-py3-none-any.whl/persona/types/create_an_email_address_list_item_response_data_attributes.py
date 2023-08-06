# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

import pydantic

from ..core.datetime_utils import serialize_datetime


class CreateAnEmailAddressListItemResponseDataAttributes(pydantic.BaseModel):
    status: typing.Optional[str]
    archived_at: typing.Optional[typing.Any] = pydantic.Field(alias="archived-at")
    updated_at: typing.Optional[str] = pydantic.Field(alias="updated-at")
    created_at: typing.Optional[str] = pydantic.Field(alias="created-at")
    match_count: typing.Optional[int] = pydantic.Field(alias="match-count")
    value: typing.Optional[str]
    match_type: typing.Optional[str] = pydantic.Field(alias="match-type")

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
