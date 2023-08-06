# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from . import utils
from ..data import get_origins


def test_invalid_get(client):
    query_str = """
    query getOrigin {
      origin(url: "http://example.com/non-existing") {
        url
      }
    }
    """
    utils.assert_missing_object(client, query_str, "origin")


@pytest.mark.parametrize("origin", get_origins())
def test_get(client, storage, origin):
    query_str = """
    query getOrigin($url: String!) {
      origin(url: $url) {
        url
        id
        visits(first: 10) {
          nodes {
            id
          }
        }
        latestVisit {
          visitId
        }
        snapshots(first: 2) {
          nodes {
            id
          }
        }
      }
    }
    """

    response, _ = utils.get_query_response(client, query_str, url=origin.url)
    data_origin = response["origin"]
    storage_origin = storage.origin_get([origin.url])[0]
    visits_and_statuses = storage.origin_visit_get_with_statuses(origin.url).results
    assert data_origin["url"] == storage_origin.url
    assert data_origin["id"] == storage_origin.id.hex()
    assert len(data_origin["visits"]["nodes"]) == len(visits_and_statuses)
    assert data_origin["latestVisit"]["visitId"] == visits_and_statuses[-1].visit.visit
    snapshots = storage.origin_snapshot_get_all(origin.url)
    assert len(data_origin["snapshots"]["nodes"]) == len(snapshots)


@pytest.mark.parametrize("origin", get_origins())
@pytest.mark.parametrize("sort", ["ASC", "DESC"])
def test_visits_sort_order(client, storage, origin, sort):
    query_str = """
    query getOrigin($url: String!, $sort: ListOrder) {
      origin(url: $url) {
        url
        id
        visits(first: 10, sort: $sort) {
          nodes {
            visitId
          }
        }
      }
    }
    """
    response, _ = utils.get_query_response(client, query_str, url=origin.url, sort=sort)
    data_visits = response["origin"]["visits"]["nodes"]
    if sort == "DESC":
        data_visits.reverse()
    assert [
        {"visitId": x.visit} for x in storage.origin_visit_get(origin.url).results
    ] == data_visits


def test_latest_visit_type_filter(client):
    query_str = """
    query getOrigin($url: String!, $visitType: String!) {
      origin(url: $url) {
        latestVisit(visitType: $visitType) {
          visitId
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client, query_str, url=get_origins()[0].url, visitType="git"
    )
    assert data["origin"] == {"latestVisit": {"visitId": 3}}

    data, _ = utils.get_query_response(
        client, query_str, url=get_origins()[0].url, visitType="hg"
    )
    assert data["origin"] == {"latestVisit": None}


def test_latest_visit_require_snapshot_filter(client):
    query_str = """
    query getOrigin($url: String!, $requireSnapshot: Boolean!) {
      origin(url: $url) {
        latestVisit(requireSnapshot: $requireSnapshot) {
          visitId
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client,
        query_str,
        url=get_origins()[1].url,
        requireSnapshot=True,
    )
    assert data["origin"] == {"latestVisit": {"visitId": 2}}


def test_latest_visit_allowed_statuses_filter(client):
    query_str = """
    query getOrigin($url: String!, $allowedStatuses: [VisitStatusState!]!) {
      origin(url: $url) {
        latestVisit(allowedStatuses: $allowedStatuses) {
          visitId
          statuses {
            nodes {
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
        url=get_origins()[1].url,
        allowedStatuses=["partial"],
    )
    assert data["origin"] == {
        "latestVisit": {"statuses": {"nodes": [{"status": "partial"}]}, "visitId": 2}
    }


@pytest.mark.parametrize("origin", get_origins())
def test_latest_snashot(client, origin):
    query_str = """
    query getOrigin($url: String!) {
      origin(url: $url) {
        latestSnapshot {
          swhid
        }
        latestVisit(requireSnapshot: true) {
          latestStatus(requireSnapshot: true) {
            snapshot {
              swhid
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client,
        query_str,
        url=origin.url,
    )
    # origin.latestSnapshot and origin.latestVisit.latestStatus.snapshot must be the same
    assert (
        data["origin"]["latestSnapshot"]
        == data["origin"]["latestVisit"]["latestStatus"]["snapshot"]
    )
