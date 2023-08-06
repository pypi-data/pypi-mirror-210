# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from swh.graphql import server
from swh.model.swhids import CoreSWHID, ObjectType

from . import utils
from ..data import (
    get_directories,
    get_directories_with_nested_path,
    get_directories_with_special_name_entries,
)


def get_target_type(target_type):
    mapping = {"file": "content", "dir": "directory", "rev": "revision"}
    return mapping.get(target_type)


def test_get_directory_entry_missing_path(client):
    directory = get_directories()[0]
    path = "missing"
    query_str = """
    query getDirEntry($swhid: SWHID!, $path: String!) {
      directoryEntry(directorySWHID: $swhid, path: $path) {
        name {
          text
        }
        target {
          type
          swhid
          node {
            ...on Content {
              swhid
            }
          }
        }
      }
    }
    """
    utils.assert_missing_object(
        client,
        query_str,
        "directoryEntry",
        swhid=str(directory.swhid()),
        path=path,
    )


@pytest.mark.parametrize(
    "directory", get_directories() + get_directories_with_nested_path()
)
def test_get_directory_entry(client, directory):
    storage = server.get_storage()
    query_str = """
    query getDirEntry($swhid: SWHID!, $path: String!) {
      directoryEntry(directorySWHID: $swhid, path: $path) {
        name {
          text
        }
        target {
          type
          swhid
          node {
            ...on Content {
              swhid
            }
            ...on Directory {
              swhid
            }
            ...on Revision {
              swhid
            }
          }
        }
      }
    }
    """
    for entry in storage.directory_ls(directory.id, recursive=True):
        data, _ = utils.get_query_response(
            client,
            query_str,
            swhid=str(directory.swhid()),
            path=entry["name"].decode(),
        )
        swhid = None
        node_exists = True
        if entry["type"] == "file" and entry["target"] is not None:
            swhid = CoreSWHID(object_type=ObjectType.CONTENT, object_id=entry["target"])
        elif entry["type"] == "dir" and entry["target"] is not None:
            swhid = CoreSWHID(
                object_type=ObjectType.DIRECTORY, object_id=entry["target"]
            )
        elif entry["type"] == "rev" and entry["target"] is not None:
            swhid = CoreSWHID(
                object_type=ObjectType.REVISION, object_id=entry["target"]
            )
        if entry["target"] == b"\x11" * 20:
            # This is a non existing object, just the target reference exists
            node_exists = False
        assert data["directoryEntry"] == {
            "name": {"text": entry["name"].decode()},
            "target": {
                "type": get_target_type(entry["type"]),
                "swhid": str(swhid) if swhid else None,
                "node": {"swhid": str(swhid)} if (swhid and node_exists) else None,
            },
        }


@pytest.mark.parametrize("directory", get_directories())
def test_get_directory_entry_connection(client, directory):
    query_str = """
    query getDirectory($swhid: SWHID!) {
      directory(swhid: $swhid) {
        swhid
        entries(first: 10) {
          totalCount
          nodes {
            name {
              text
            }
            target {
              type
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(client, query_str, swhid=str(directory.swhid()))
    directory_entries = data["directory"]["entries"]["nodes"]
    assert len(directory_entries) == len(directory.entries)
    assert data["directory"]["entries"]["totalCount"] == len(directory.entries)
    output = [
        {
            "name": {"text": de.name.decode()},
            "target": {"type": get_target_type(de.type)},
        }
        for de in directory.entries
    ]
    for each_entry in output:
        assert each_entry in directory_entries


@pytest.mark.parametrize("directory", get_directories())
def test_directory_entry_connection_filter_by_name(client, directory):
    storage = server.get_storage()
    for dir_entry in storage.directory_ls(directory.id):
        name_include = dir_entry["name"][:-1].decode()
        query_str = """
        query getDirectory($swhid: SWHID!, $nameInclude: String) {
          directory(swhid: $swhid) {
            swhid
            entries(nameInclude: $nameInclude) {
              nodes {
                name {
                  text
                }
                target {
                  type
                }
              }
            }
          }
        }
        """
        data, _ = utils.get_query_response(
            client,
            query_str,
            swhid=str(directory.swhid()),
            nameInclude=name_include,
        )
        for entry in data["directory"]["entries"]["nodes"]:
            assert name_include in entry["name"]["text"]
            assert entry["target"]["type"] == get_target_type(dir_entry["type"])


def test_directory_entry_connection_filter_by_name_special_chars(client):
    directory = get_directories_with_special_name_entries()[0]
    query_str = """
    query getDirectory($swhid: SWHID!, $nameInclude: String) {
      directory(swhid: $swhid) {
        entries(nameInclude: $nameInclude) {
          nodes {
            name {
              text
            }
            target {
              type
            }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client,
        query_str,
        swhid=str(directory.swhid()),
        nameInclude="ssSSé",
    )
    assert data["directory"]["entries"]["nodes"][0] == {
        "name": {"text": "ßßétEÉt"},
        "target": {
            "type": "content",
        },
    }
