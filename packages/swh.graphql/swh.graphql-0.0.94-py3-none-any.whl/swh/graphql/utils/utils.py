# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import base64
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from swh.graphql.errors import InvalidInputError

if TYPE_CHECKING:
    from swh.graphql.resolvers.base_connection import ConnectionData

from swh.storage.interface import ListOrder, PagedResult

ENCODING = "utf-8"


def get_b64_string(source) -> str:
    if isinstance(source, str):
        source = source.encode(ENCODING)
    return base64.b64encode(source).decode("ascii")


def get_encoded_cursor(cursor: Optional[str]) -> Optional[str]:
    if cursor is None:
        return None
    return get_b64_string(cursor)


def get_decoded_cursor(cursor: Optional[str]) -> Optional[str]:
    if cursor is None:
        return None
    return base64.b64decode(cursor, validate=True).decode()


def get_formatted_date(date: datetime) -> str:
    # FIXME, handle error + return other formats
    return date.isoformat()


def get_storage_list_order(order: str) -> ListOrder:
    mapping = {"ASC": ListOrder.ASC, "DESC": ListOrder.DESC}
    if order not in mapping:
        raise InvalidInputError("Invalid sort order")
    return mapping[order]


def get_local_paginated_data(source: List, first: int, after=0) -> "ConnectionData":
    """
    Pagination at the GraphQL level
    This is a temporary fix and inefficient. Should eventually be moved to the
    backend (storage) level
    """
    from swh.graphql.resolvers.base_connection import ConnectionData

    # FIXME, handle data errors here
    after = 0 if after is None else int(after)
    end_cursor = after + first
    results = source[after:end_cursor]
    next_page_token = None
    if len(source) > end_cursor:
        next_page_token = str(end_cursor)
    return ConnectionData(
        paged_result=PagedResult(results=results, next_page_token=next_page_token),
        total_count=len(source),
    )
