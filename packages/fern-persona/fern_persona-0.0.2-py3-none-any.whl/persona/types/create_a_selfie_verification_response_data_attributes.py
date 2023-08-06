# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

import pydantic

from ..core.datetime_utils import serialize_datetime


class CreateASelfieVerificationResponseDataAttributes(pydantic.BaseModel):
    status: typing.Optional[str]
    created_at: typing.Optional[str] = pydantic.Field(alias="created-at")
    created_at_ts: typing.Optional[int] = pydantic.Field(alias="created-at-ts")
    submitted_at: typing.Optional[typing.Any] = pydantic.Field(alias="submitted-at")
    submitted_at_ts: typing.Optional[typing.Any] = pydantic.Field(alias="submitted-at-ts")
    completed_at: typing.Optional[typing.Any] = pydantic.Field(alias="completed-at")
    completed_at_ts: typing.Optional[typing.Any] = pydantic.Field(alias="completed-at-ts")
    country_code: typing.Optional[typing.Any] = pydantic.Field(alias="country-code")
    entity_confidence_reasons: typing.Optional[typing.List[typing.Any]] = pydantic.Field(
        alias="entity-confidence-reasons"
    )
    document_similarity_score: typing.Optional[typing.Any] = pydantic.Field(alias="document-similarity-score")
    selfie_similarity_score_left: typing.Optional[typing.Any] = pydantic.Field(alias="selfie-similarity-score-left")
    selfie_similarity_score_right: typing.Optional[typing.Any] = pydantic.Field(alias="selfie-similarity-score-right")
    checks: typing.Optional[typing.List[typing.Any]]
    capture_method: typing.Optional[typing.Any] = pydantic.Field(alias="capture-method")

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
