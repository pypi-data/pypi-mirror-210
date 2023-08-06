# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from . import utils
from ..data import (  # get_contents,; get_directories,; get_snapshots,
    get_contents,
    get_directories,
    get_releases,
    get_revisions,
    get_snapshots,
)


def test_invalid_swhid(client):
    query_str = """
    query resolve($swhid: SWHID!) {
      resolveSWHID(swhid: $swhid) {
        __typename
      }
    }
    """
    errors = utils.get_error_response(client, query_str, swhid="swh:1:dir:invalid")
    # API will throw an error in case of an invalid SWHID
    assert len(errors) == 1
    assert "Input error: Invalid SWHID" in errors[0]["message"]


@pytest.mark.parametrize(
    "swhid",
    [
        "swh:1:rel:0949d7a8c96347dba09be8d79085b8207f345412",
        "swh:1:rev:0949d7a8c96347dba09be8d79085b8207f345412",
        "swh:1:dir:0949d7a8c96347dba09be8d79085b8207f345412",
        "swh:1:cnt:0949d7a8c96347dba09be8d79085b8207f345412",
        "swh:1:snp:0949d7a8c96347dba09be8d79085b8207f345412",
    ],
)
def test_missing_swhid(client, swhid):
    query_str = """
    query resolve($swhid: SWHID!) {
      resolveSWHID(swhid: $swhid) {
        __typename
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=swhid)
    # API will return None in case of a valid, non existing SWHID
    assert data == {"resolveSWHID": None}


@pytest.mark.parametrize("snapshot", get_snapshots())
def test_snapshot_swhid_resolve(client, snapshot):
    query_str = """
    query resolve($swhid: SWHID!) {
      resolveSWHID(swhid: $swhid) {
        __typename
        ... on Snapshot {
          swhid
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(snapshot.swhid()))
    assert data == {
        "resolveSWHID": [
            {
                "__typename": "Snapshot",
                "swhid": str(snapshot.swhid()),
            },
        ]
    }


@pytest.mark.parametrize("revision", get_revisions())
def test_revision_swhid_resolve(client, revision):
    query_str = """
    query resolve($swhid: SWHID!) {
      resolveSWHID(swhid: $swhid) {
        __typename
        ... on Revision {
          swhid
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(revision.swhid()))
    assert data == {
        "resolveSWHID": [
            {
                "__typename": "Revision",
                "swhid": str(revision.swhid()),
            }
        ]
    }


@pytest.mark.parametrize("release", get_releases())
def test_release_swhid_resolve(client, release):
    query_str = """
    query resolve($swhid: SWHID!) {
      resolveSWHID(swhid: $swhid) {
        __typename
        ... on Release {
          swhid
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(release.swhid()))
    assert data == {
        "resolveSWHID": [
            {
                "__typename": "Release",
                "swhid": str(release.swhid()),
            }
        ]
    }


@pytest.mark.parametrize("directory", get_directories())
def test_directory_swhid_resolve(client, directory):
    query_str = """
    query resolve($swhid: SWHID!) {
      resolveSWHID(swhid: $swhid) {
        __typename
        ... on Directory {
          swhid
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(directory.swhid()))
    assert data == {
        "resolveSWHID": [
            {
                "__typename": "Directory",
                "swhid": str(directory.swhid()),
            },
        ]
    }


@pytest.mark.parametrize("content", get_contents())
def test_content_swhid_resolve(client, content):
    query_str = """
    query resolve($swhid: SWHID!) {
      resolveSWHID(swhid: $swhid) {
        __typename
        ... on Content {
          swhid
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(content.swhid()))
    assert data == {
        "resolveSWHID": [
            {
                "__typename": "Content",
                "swhid": str(content.swhid()),
            },
        ]
    }
