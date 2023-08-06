# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from . import utils
from ..data import get_directories


@pytest.mark.parametrize("directory", get_directories())
def test_get_directory(client, directory):
    query_str = """
    query getDirectory($swhid: SWHID!) {
      directory(swhid: $swhid) {
        swhid
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(directory.swhid()))
    assert data["directory"] == {"swhid": str(directory.swhid())}


def test_get_directory_with_invalid_swhid(client):
    query_str = """
    query getDirectory($swhid: SWHID!) {
      directory(swhid: $swhid) {
        swhid
      }
    }
    """
    errors = utils.get_error_response(client, query_str, swhid="swh:1:dir:invalid")
    # API will throw an error in case of an invalid SWHID
    assert len(errors) == 1
    assert "Input error: Invalid SWHID" in errors[0]["message"]


def test_get_revision_directory(client):
    query_str = """
    query getRevision($swhid: SWHID!) {
      revision(swhid: $swhid) {
        swhid
        directory {
          swhid
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client,
        query_str,
        swhid="swh:1:rev:66c7c1cd9673275037140f2abff7b7b11fc9439c",
    )
    assert data["revision"]["directory"] == {
        "swhid": "swh:1:dir:0101010101010101010101010101010101010101",
    }


def test_get_target_directory(client):
    # TargetDirectoryNode is returned from snapshotbranch, release
    # and directory entry nodes. Release node is used for testing here
    query_str = """
    query getRelease($swhid: SWHID!) {
      release(swhid: $swhid) {
        swhid
        target {
          node {
            ...on Directory {
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
        swhid="swh:1:rel:ee4d20e80af850cc0f417d25dc5073792c5010d2",
    )
    assert data["release"]["target"]["node"] == {
        "swhid": "swh:1:dir:0505050505050505050505050505050505050505"
    }


def test_get_directory_with_unknown_swhid(client):
    unknown_sha1 = "1" * 40
    query_str = """
    query getDirectory($swhid: SWHID!) {
      directory(swhid: $swhid) {
        swhid
      }
    }
    """
    utils.assert_missing_object(
        client,
        query_str,
        obj_type="directory",
        swhid=f"swh:1:dir:{unknown_sha1}",
    )
