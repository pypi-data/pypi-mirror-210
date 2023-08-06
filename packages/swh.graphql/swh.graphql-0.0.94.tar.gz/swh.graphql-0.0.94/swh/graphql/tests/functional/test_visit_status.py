# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from . import utils
from ..data import get_origins, get_visit_status, get_visits


@pytest.mark.parametrize(
    "visit, visit_status", list(zip(get_visits(), get_visit_status()))
)
def test_get_visit_status(client, visit, visit_status):
    query_str = """
    query getVisit($origin: String!, $visitId: Int!) {
      visit(originUrl: $origin, visitId: $visitId) {
        statuses(first: 3) {
          nodes {
            status
            date
            type
            snapshot {
              swhid
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client, query_str, origin=visit.origin, visitId=visit.visit
    )
    assert data["visit"]["statuses"]["nodes"][0] == {
        "date": visit_status.date.isoformat(),
        "snapshot": {"swhid": f"swh:1:snp:{visit_status.snapshot.hex()}"}
        if visit_status.snapshot is not None
        else None,
        "status": visit_status.status,
        "type": visit_status.type,
    }


def test_visit_status_pagination(client):
    # visit status is using a different cursor, hence separate test
    query_str = """
    query getVisit($origin: String!, $visitId: Int!) {
      visit(originUrl: $origin, visitId: $visitId) {
        statuses(first: 1) {
          pageInfo {
            hasNextPage
            endCursor
          }
          edges {
            node {
              status
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client, query_str, origin=get_origins()[0].url, visitId=1
    )
    # request again with the endcursor
    end_cursor = data["visit"]["statuses"]["pageInfo"]["endCursor"]
    query_str = """
    query getVisit($origin: String!, $visitId: Int!, $after: String) {
      visit(originUrl: $origin, visitId: $visitId) {
        statuses(first: 1, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          edges {
            node {
              status
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client,
        query_str,
        origin=get_origins()[0].url,
        visitId=1,
        after=end_cursor,
    )
    assert data["visit"]["statuses"] == {
        "edges": [
            {
                "node": {"status": "ongoing"},
            }
        ],
        "pageInfo": {"endCursor": None, "hasNextPage": False},
    }
