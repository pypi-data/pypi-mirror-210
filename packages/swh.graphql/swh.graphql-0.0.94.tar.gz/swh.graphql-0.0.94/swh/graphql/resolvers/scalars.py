# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import datetime
from typing import Optional

from ariadne import ScalarType

from swh.graphql.errors import InvalidInputError
from swh.graphql.utils import utils
from swh.model.exceptions import ValidationError
from swh.model.swhids import CoreSWHID

datetime_scalar = ScalarType("DateTime")
swhid_scalar = ScalarType("SWHID")
id_scalar = ScalarType("ID")


@id_scalar.serializer
def serialize_id(value) -> str:
    if isinstance(value, str):
        value = value.encode()
    return value.hex()


@datetime_scalar.serializer
def serialize_datetime(value: Optional[datetime.datetime]) -> Optional[str]:
    return None if value is None else utils.get_formatted_date(value)


@swhid_scalar.value_parser
def validate_swhid(value):
    try:
        swhid = CoreSWHID.from_string(value)
    except ValidationError as e:
        raise InvalidInputError("Invalid SWHID", e)
    return swhid


@swhid_scalar.serializer
def serialize_swhid(value):
    return str(value)
