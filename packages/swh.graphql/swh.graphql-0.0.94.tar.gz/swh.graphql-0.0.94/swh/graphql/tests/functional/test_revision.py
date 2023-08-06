# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import base64

import pytest

from swh.model.swhids import CoreSWHID

from . import utils
from ..data import (
    get_revisions,
    get_revisions_with_none_date,
    get_revisions_with_parents,
)


@pytest.mark.parametrize("revision", get_revisions())
def test_get_revision(client, revision):
    query_str = """
    query getRevision($swhid: SWHID!) {
      revision(swhid: $swhid) {
        swhid
        message {
          text
        }
        author {
          fullname {
            text
          }
          name {
            text
          }
          email {
            text
          }
        }
        committer {
          fullname {
            text
          }
          name {
            text
          }
          email {
            text
          }
        }
        date {
          date
          offset {
            text
            base64
          }
        }
        committerDate {
          date
          offset {
            text
            base64
          }
        }
        type
        directory {
          swhid
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(revision.swhid()))

    assert data["revision"] == {
        "swhid": str(revision.swhid()),
        "message": {"text": revision.message.decode()},
        "author": [
            {
                "fullname": {"text": revision.author.fullname.decode()},
                "name": {"text": revision.author.name.decode()},
                "email": {"text": revision.author.email.decode()},
            }
        ],
        "committer": [
            {
                "fullname": {"text": revision.committer.fullname.decode()},
                "name": {"text": revision.committer.name.decode()},
                "email": {"text": revision.committer.email.decode()},
            }
        ],
        "date": {
            "date": revision.date.to_datetime().isoformat(),
            "offset": {
                "text": revision.date.offset_bytes.decode(),
                "base64": base64.b64encode(revision.date.offset_bytes).decode("ascii"),
            },
        }
        if revision.date
        else None,
        "committerDate": {
            "date": revision.committer_date.to_datetime().isoformat(),
            "offset": {
                "text": revision.committer_date.offset_bytes.decode(),
                "base64": base64.b64encode(revision.committer_date.offset_bytes).decode(
                    "ascii"
                ),
            },
        }
        if revision.committer_date
        else None,
        "type": revision.type.value,
        "directory": {
            "swhid": str(CoreSWHID(object_id=revision.directory, object_type="dir")),
        },
    }


def test_get_revision_with_invalid_swhid(client):
    query_str = """
    query getRevision($swhid: SWHID!) {
      revision(swhid: $swhid) {
        swhid
      }
    }
    """
    errors = utils.get_error_response(client, query_str, swhid="swh:1:cnt:invalid")
    # API will throw an error in case of an invalid SWHID
    assert len(errors) == 1
    assert "Input error: Invalid SWHID" in errors[0]["message"]


def test_get_revision_as_target(client):
    # SWHID of a snapshot with revision as target
    snapshot_swhid = "swh:1:snp:9e78d7105c5e0f886487511e2a92377b4ee4c32a"
    query_str = """
    query getSnapshot($swhid: SWHID!) {
      snapshot(swhid: $swhid) {
        branches(first: 1, types: [revision]) {
          nodes {
            target {
              node {
                ...on Revision {
                  swhid
                }
              }
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=snapshot_swhid)
    revision_obj = data["snapshot"]["branches"]["nodes"][0]["target"]["node"]
    assert revision_obj == {
        "swhid": "swh:1:rev:66c7c1cd9673275037140f2abff7b7b11fc9439c"
    }


def test_get_revision_log(client):
    revision_swhid = get_revisions_with_parents()[0].swhid()
    query_str = """
    query getRevision($swhid: SWHID!) {
      revision(swhid: $swhid) {
        swhid
        revisionLog(first: 2) {
          totalCount
          nodes {
            swhid
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(revision_swhid))
    assert data["revision"]["revisionLog"] == {
        "totalCount": 3,
        "nodes": [
            {"swhid": str(revision_swhid)},
            {"swhid": str(get_revisions()[0].swhid())},
        ],
    }


def test_get_revision_parents(client):
    revision_swhid = get_revisions_with_parents()[0].swhid()
    query_str = """
    query getRevision($swhid: SWHID!) {
      revision(swhid: $swhid) {
        swhid
        parents {
          totalCount
          nodes {
            swhid
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(revision_swhid))

    assert data["revision"]["parents"] == {
        "totalCount": 2,
        "nodes": [
            {"swhid": str(get_revisions()[0].swhid())},
            {"swhid": str(get_revisions()[1].swhid())},
        ],
    }


def test_get_revision_with_unknown_swhid(client):
    unknown_sha1 = "1" * 40
    query_str = """
    query getRevision($swhid: SWHID!) {
      revision(swhid: $swhid) {
        swhid
      }
    }
    """
    utils.assert_missing_object(
        client,
        query_str,
        obj_type="revision",
        swhid=f"swh:1:rev:{unknown_sha1}",
    )


def test_get_revisions_with_none_date(client):
    revision_swhid = get_revisions_with_none_date()[0].swhid()
    query_str = """
    query getRevision($swhid: SWHID!) {
      revision(swhid: $swhid) {
        swhid
        date {
          date
          offset {
            text
            base64
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(revision_swhid))
    assert data == {"revision": {"swhid": str(revision_swhid), "date": None}}
