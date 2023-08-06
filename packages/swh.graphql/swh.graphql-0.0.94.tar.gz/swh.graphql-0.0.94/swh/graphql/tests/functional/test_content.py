# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from . import utils
from ..data import get_contents


@pytest.mark.parametrize("content", get_contents())
def test_get_content_with_hashes(client, content):
    query_str = """
    query getContentByHashes($sha1: String!, $sha256: String!,
                     $sha1_git: String!, $blake2s256: String!) {
      contentByHashes(sha1: $sha1, sha256: $sha256, sha1_git: $sha1_git,
              blake2s256: $blake2s256) {
        swhid
        id
        hashes {
          blake2s256
          sha1
          sha1_git
          sha256
        }
        length
        status
        data {
          url
        }
        mimeType {
          encoding
        }
        language {
          lang
        }
        license {
          licenses
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client,
        query_str,
        blake2s256=content.blake2s256.hex(),
        sha1=content.sha1.hex(),
        sha1_git=content.sha1_git.hex(),
        sha256=content.sha256.hex(),
    )
    archive_url = "https://archive.softwareheritage.org/api/1/"
    response = {
        "swhid": str(content.swhid()),
        "id": content.sha1_git.hex(),
        "hashes": {
            "blake2s256": content.blake2s256.hex(),
            "sha1": content.sha1.hex(),
            "sha1_git": content.sha1_git.hex(),
            "sha256": content.sha256.hex(),
        },
        "length": content.length,
        "status": content.status,
        "data": {
            "url": f"{archive_url}content/sha1:{content.sha1.hex()}/raw/",
        },
        "mimeType": None,
        "language": None,
        "license": None,
    }
    assert data["contentByHashes"] == response


@pytest.mark.parametrize("content", get_contents())
def test_get_contents_with_swhid(client, content):
    query_str = """
    query getContents($swhid: SWHID!) {
      contentsBySWHID(swhid: $swhid) {
        swhid
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(content.swhid()))
    assert data["contentsBySWHID"] == [{"swhid": str(content.swhid())}]


def test_get_contents_with_invalid_swhid(client):
    query_str = """
    query getContents($swhid: SWHID!) {
      contentsBySWHID(swhid: $swhid) {
        swhid
      }
    }
    """
    errors = utils.get_error_response(client, query_str, swhid="invalid")
    # API will throw an error in case of an invalid SWHID
    assert len(errors) == 1
    assert "Input error: Invalid SWHID" in errors[0]["message"]


def test_get_contents_with_missing_swhid(client):
    missing_sha1 = "1" * 40
    query_str = """
    query getContents($swhid: SWHID!) {
      contentsBySWHID(swhid: $swhid) {
        swhid
      }
    }
    """
    data, _ = utils.get_query_response(
        client, query_str, swhid=f"swh:1:cnt:{missing_sha1}"
    )
    assert data["contentsBySWHID"] == []


@pytest.mark.parametrize("content", get_contents())
def test_get_contents_with_hashes(client, content):
    query_str = """
    query getContents($sha1: String, $sha1_git: String, $sha256: String,
                     $blake2s256: String) {
      contentsByHashes(sha1: $sha1, sha1_git: $sha1_git, sha256: $sha256,
                      blake2s256: $blake2s256) {
        swhid
      }
    }
    """
    data, _ = utils.get_query_response(
        client,
        query_str,
        sha1=content.sha1.hex(),
        sha1_git=content.sha1_git.hex(),
        sha256=content.sha256.hex(),
        blake2s256=content.blake2s256.hex(),
    )
    assert data["contentsByHashes"] == [{"swhid": str(content.swhid())}]


@pytest.mark.parametrize("content", get_contents())
def test_get_content_with_single_hash(client, content):
    query_str = """
    query getContents($sha1: String, $sha1_git: String, $sha256: String,
                     $blake2s256: String) {
      contentsByHashes(sha1: $sha1, sha1_git: $sha1_git, sha256: $sha256,
                      blake2s256: $blake2s256) {
        swhid
      }
    }
    """
    data, _ = utils.get_query_response(
        client,
        query_str,
        sha1=content.sha1.hex(),
    )
    assert data["contentsByHashes"] == [{"swhid": str(content.swhid())}]

    data, _ = utils.get_query_response(
        client,
        query_str,
        blake2s256=content.blake2s256.hex(),
    )
    assert data["contentsByHashes"] == [{"swhid": str(content.swhid())}]


@pytest.mark.parametrize("content", get_contents())
def test_get_contents_with_one_non_matching_hash(client, content):
    query_str = """
    query getContents($sha1: String, $sha1_git: String, $sha256: String, $blake2s256: String) {
      contentsByHashes(sha1: $sha1, sha1_git: $sha1_git, sha256: $sha256,
                      blake2s256: $blake2s256) {
        swhid
      }
    }
    """
    data, _ = utils.get_query_response(
        client,
        query_str,
        obj_type="contentsByHashes",
        sha1=content.sha1.hex(),
        sha1_git="a" * 20,  # hash is valid, but not matching the object
    )
    assert data["contentsByHashes"] == []


def test_get_content_with_invalid_hashes(client):
    content = get_contents()[0]
    query_str = """
    query getContents($sha1: String, $sha1_git: String, $sha256: String,
                      $blake2s256: String) {
      contentsByHashes(sha1: $sha1, sha1_git: $sha1_git, sha256: $sha256,
                       blake2s256: $blake2s256) {
        swhid
      }
    }
    """
    errors = utils.get_error_response(
        client,
        query_str,
        sha1="invalid",  # Only one hash is invalid
        sha1_git=content.sha1_git.hex(),
        sha256=content.sha256.hex(),
    )
    # API will throw an error in case of an invalid content hash
    assert len(errors) == 1
    assert "Input error: Invalid content hash" in errors[0]["message"]


def test_get_content_with_no_hashes(client):
    query_str = """
    query getContents($sha1: String, $sha1_git: String, $sha256: String, $blake2s256: String) {
      contentsByHashes(sha1: $sha1, sha1_git: $sha1_git, sha256: $sha256,
                      blake2s256: $blake2s256) {
        swhid
      }
    }
    """
    errors = utils.get_error_response(
        client,
        query_str,
    )
    assert len(errors) == 1
    assert (
        "Input error: At least one of the four hashes must be provided"
        in errors[0]["message"]
    )


def test_get_content_as_target(client):
    # SWHID of a test dir with a file entry
    directory_swhid = "swh:1:dir:87b339104f7dc2a8163dec988445e3987995545f"
    query_str = """
    query getDirectory($swhid: SWHID!) {
      directory(swhid: $swhid) {
        swhid
        entries(first: 2) {
          nodes {
            target {
              type
              node {
                ...on Content {
                  swhid
                  length
                }
              }
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=directory_swhid)
    content_obj = data["directory"]["entries"]["nodes"][1]["target"]["node"]
    assert content_obj == {
        "length": 4,
        "swhid": "swh:1:cnt:86bc6b377e9d25f9d26777a4a28d08e63e7c5779",
    }
