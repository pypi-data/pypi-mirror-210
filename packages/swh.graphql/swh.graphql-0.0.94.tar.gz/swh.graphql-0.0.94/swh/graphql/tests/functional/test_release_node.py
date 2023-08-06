# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import base64

import pytest

from swh.model.model import ObjectType

from . import utils
from ..data import (
    get_contents,
    get_directories,
    get_releases,
    get_releases_with_empty_target,
    get_releases_with_target,
    get_revisions,
)


@pytest.mark.parametrize("release", get_releases())
def test_get_release(client, release):
    query_str = """
    query getRelease($swhid: SWHID!) {
      release(swhid: $swhid) {
        swhid
        name {
          text
          base64
        }
        message {
          text
        }
        author {
          email {
            text
          }
          name {
            text
          }
          fullname {
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
        target {
          type
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(release.swhid()))

    assert data["release"] == {
        "swhid": str(release.swhid()),
        "name": {
            "text": release.name.decode(),
            "base64": base64.b64encode(release.name).decode("ascii"),
        },
        "message": {"text": release.message.decode()},
        "author": [
            {
                "email": {"text": release.author.email.decode()},
                "name": {"text": release.author.name.decode()},
                "fullname": {"text": release.author.fullname.decode()},
            }
        ]
        if release.author
        else [],
        "date": {
            "date": release.date.to_datetime().isoformat(),
            "offset": {
                "text": release.date.offset_bytes.decode(),
                "base64": base64.b64encode(release.date.offset_bytes).decode("ascii"),
            },
        }
        if release.date
        else None,
        "target": {"type": release.target_type.value},
    }


def test_get_release_with_invalid_swhid(client):
    query_str = """
    query getRelease($swhid: SWHID!) {
      release(swhid: $swhid) {
        swhid
      }
    }
    """
    errors = utils.get_error_response(client, query_str, swhid="swh:1:rel:invalid")
    # API will throw an error in case of an invalid SWHID
    assert len(errors) == 1
    assert "Input error: Invalid SWHID" in errors[0]["message"]


@pytest.mark.parametrize("release_with_target", get_releases_with_target())
def test_get_release_targets(client, release_with_target):
    query_str = """
    query getRelease($swhid: SWHID!) {
      release(swhid: $swhid) {
        target {
          type
          swhid
          node {
            ...on Revision {
              swhid
            }
            ...on Release {
              swhid
            }
            ...on Directory {
              swhid
            }
            ...on Content {
              swhid
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client, query_str, swhid=str(release_with_target.swhid())
    )

    if release_with_target.target_type == ObjectType.REVISION:
        target_swhid = get_revisions()[0].swhid()
    elif release_with_target.target_type == ObjectType.RELEASE:
        target_swhid = get_releases()[0].swhid()
    elif release_with_target.target_type == ObjectType.DIRECTORY:
        target_swhid = get_directories()[0].swhid()
    elif release_with_target.target_type == ObjectType.CONTENT:
        target_swhid = get_contents()[0].swhid()
    assert data["release"] == {
        "target": {
            "type": release_with_target.target_type.value,
            "swhid": str(target_swhid),
            "node": {"swhid": str(target_swhid)},
        }
    }


def test_get_release_target_unknown(client):
    # Clinet can request all the possible options if the target type
    # is unknown. The data under the right type will be returned

    # The target is of type Revision in this case
    # ie: both swhid and message will be available in the response
    swhid = get_releases_with_target()[0].swhid()
    query_str = """
    query getRelease($swhid: SWHID!) {
      release(swhid: $swhid) {
        target {
          type
          node {
            ...on Revision {
              swhid
              message {
                text
              }
            }
            ...on Release {
              swhid
            }
            ...on Directory {
              swhid
            }
            ...on Content {
              swhid
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(swhid))
    assert data["release"] == {
        "target": {
            "type": "revision",
            "node": {
                "message": {"text": "hello"},
                "swhid": str(get_revisions()[0].swhid()),
            },
        },
    }


def test_get_release_with_unknown_swhid(client):
    unknown_sha1 = "1" * 40
    query_str = """
    query getRelease($swhid: SWHID!) {
      release(swhid: $swhid) {
        swhid
      }
    }
    """
    utils.assert_missing_object(
        client,
        query_str,
        obj_type="release",
        swhid=f"swh:1:rel:{unknown_sha1}",
    )


def test_get_release_with_empty_target(client):
    swhid = get_releases_with_empty_target()[0].swhid()
    query_str = """
    query getRelease($swhid: SWHID!) {
      release(swhid: $swhid) {
        target {
          type
        }
      }
    }"""
    data, err = utils.get_query_response(client, query_str, swhid=str(swhid))
    assert data == {"release": {"target": None}}
    assert err is None
