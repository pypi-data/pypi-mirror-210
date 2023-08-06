# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from . import utils
from ..data import get_snapshots


@pytest.mark.parametrize("snapshot", get_snapshots())
def test_get_snapshot(client, snapshot):
    query_str = """
    query getSnapshot($swhid: SWHID!) {
      snapshot(swhid: $swhid) {
        id
        swhid
        branches(first:5) {
          nodes {
            type
            name {
              text
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(snapshot.swhid()))
    assert data["snapshot"]["swhid"] == str(snapshot.swhid())
    assert data["snapshot"]["id"] == snapshot.id.hex()
    assert len(data["snapshot"]["branches"]["nodes"]) == len(snapshot.branches)


def test_get_snapshot_missing_swhid(client):
    query_str = """
    query getSnapshot($swhid: SWHID!) {
      snapshot(swhid: $swhid) {
        swhid
      }
    }
    """
    utils.assert_missing_object(
        client,
        query_str,
        obj_type="snapshot",
        swhid="swh:1:snp:0949d7a8c96347dba09be8d79085b8207f345412",
    )


def test_get_snapshot_invalid_swhid(client):
    query_str = """
    query getSnapshot($swhid: SWHID!) {
      snapshot(swhid: $swhid) {
        swhid
      }
    }
    """
    errors = utils.get_error_response(client, query_str, swhid="swh:1:snp:invalid")
    assert len(errors) == 1
    assert "Input error: Invalid SWHID" in errors[0]["message"]
