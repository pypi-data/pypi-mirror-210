# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

import pydantic

from ..core.datetime_utils import serialize_datetime
from .create_a_government_id_document_request_data_attributes_back_photo import (
    CreateAGovernmentIdDocumentRequestDataAttributesBackPhoto,
)
from .create_a_government_id_document_request_data_attributes_front_photo import (
    CreateAGovernmentIdDocumentRequestDataAttributesFrontPhoto,
)


class CreateAGovernmentIdDocumentRequestDataAttributes(pydantic.BaseModel):
    inquiry_id: str = pydantic.Field(alias="inquiry-id")
    country_code: str = pydantic.Field(
        alias="country-code", description=("ISO 3166-1 alpha-2 code of the ID’s issuing country.\n")
    )
    selected_id_class: typing.Optional[typing.List[str]] = pydantic.Field(alias="selected-id-class")
    front_photo: typing.Optional[CreateAGovernmentIdDocumentRequestDataAttributesFrontPhoto] = pydantic.Field(
        alias="front-photo", description=("Front of ID.\n")
    )
    back_photo: typing.Optional[CreateAGovernmentIdDocumentRequestDataAttributesBackPhoto] = pydantic.Field(
        alias="back-photo", description=("Back of ID.\n")
    )

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
