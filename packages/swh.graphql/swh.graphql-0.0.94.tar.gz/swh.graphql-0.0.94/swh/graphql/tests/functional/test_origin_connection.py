# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import Optional

from . import utils
from ..data import get_origins


def get_origins_from_api(
    client, first: int, urlPattern: Optional[str] = None, **args
) -> tuple:
    query_str = """
    query getOrigins($first: Int!, $urlPattern: String) {
      origins(first: $first, urlPattern: $urlPattern) {
        nodes {
          url
        }
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    return utils.get_query_response(
        client, query_str, first=first, urlPattern=urlPattern
    )


def test_get(client):
    data, _ = get_origins_from_api(client, first=10)
    assert len(data["origins"]["nodes"]) == len(get_origins())


def test_get_filter_by_pattern(client):
    data, _ = get_origins_from_api(client, first=10, urlPattern='"somewhere.org/den"')
    assert len(data["origins"]["nodes"]) == 1


def test_get_filter_by_non_existing_pattern(client):
    data, _ = get_origins_from_api(
        client, first=10, urlPattern='"somewhere.org/den/test/"'
    )
    assert len(data["origins"]["nodes"]) == 0


def test_basic_pagination(client):
    data, _ = get_origins_from_api(client, first=len(get_origins()))
    assert data["origins"]["totalCount"] is None
    assert len(data["origins"]["nodes"]) == len(get_origins())
    assert data["origins"]["pageInfo"] == {"hasNextPage": False, "endCursor": None}
