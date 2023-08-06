# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from . import utils
from ..data import get_directories, get_origins


# Using Origin object to run functional tests for pagination
def get_origin_nodes(client, first, after=""):
    query_str = """
    query getOrigins($first: Int!, $after: String) {
      origins(first: $first, after: $after) {
        nodes {
          id
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    return utils.get_query_response(client, query_str, first=first, after=after)


def test_pagination(client):
    # requesting the max number of nodes available
    # endCursor must be None
    data, _ = get_origin_nodes(client, first=len(get_origins()))
    assert len(data["origins"]["nodes"]) == len(get_origins())
    assert data["origins"]["pageInfo"] == {"hasNextPage": False, "endCursor": None}


def test_first_arg(client):
    data, _ = get_origin_nodes(client, first=1)
    assert len(data["origins"]["nodes"]) == 1
    assert data["origins"]["pageInfo"]["hasNextPage"] is True


def test_invalid_first_arg(client):
    data, errors = get_origin_nodes(client, first=-1)
    assert data["origins"] is None
    assert (len(errors)) == 2  # one error for origins and anotehr one for pageInfo
    assert (
        errors[0]["message"]
        == "Pagination error: Value for argument 'first' is invalid; it must be between 0 and 1000"  # noqa: B950
    )


def test_too_big_first_arg(client, high_query_cost):
    data, errors = get_origin_nodes(client, 1001)  # max page size is 1000
    assert data["origins"] is None
    assert (len(errors)) == 2
    assert (
        errors[0]["message"]
        == "Pagination error: Value for argument 'first' is invalid; it must be between 0 and 1000"  # noqa: B950
    )


def test_after_arg(client):
    first_data, _ = get_origin_nodes(client, first=1)
    end_cursor = first_data["origins"]["pageInfo"]["endCursor"]
    # get again with endcursor as the after argument
    data, _ = get_origin_nodes(client, first=1, after=end_cursor)
    assert len(data["origins"]["nodes"]) == 1
    assert data["origins"]["pageInfo"] == {"hasNextPage": False, "endCursor": None}


def test_invalid_after_arg(client):
    data, errors = get_origin_nodes(client, first=1, after="invalid")
    assert data["origins"] is None
    assert (len(errors)) == 2
    assert (
        errors[0]["message"] == "Pagination error: Invalid value for argument 'after'"
    )


def test_edge_cursor(client):
    # Use DirectoryEntry connection to test connection edges
    # The same code is used in all the other connections, hence a single test
    directory = get_directories()[1]
    query_str = """
    query getDirectory($swhid: SWHID!, $entries_first: Int!, $entries_after: String) {
      directory(swhid: $swhid) {
        entries(first: $entries_first, after: $entries_after) {
          edges {
            cursor
            node {
              name {
                text
              }
            }
          }
          pageInfo {
            endCursor
            hasNextPage
          }
          nodes {
             name {
               text
             }
          }
        }
      }
    }
    """
    data, _ = utils.get_query_response(
        client, query_str, swhid=str(directory.swhid()), entries_first=1
    )
    entries = data["directory"]["entries"]
    # Make sure the first node object in edges and nodes is the same
    assert entries["edges"][0]["node"] == entries["nodes"][0]
    assert entries["edges"][0]["node"] == {
        "name": {"text": directory.entries[1].name.decode()}
    }
    assert entries["pageInfo"]["hasNextPage"] is True
    # FIXME, Following behaviour is not in compliance with the relay spec.
    # last-item-cursor and endcursor should be the same as per relay.
    # This test will fail once the pagination becomes fully relay complaint.
    assert entries["pageInfo"]["endCursor"] != entries["edges"][-1]["cursor"]
    # Make another query with the after argument, after argument is the first item
    # cursor here, result will be the same as the last one
    new_data, _ = utils.get_query_response(
        client,
        query_str,
        swhid=str(directory.swhid()),
        entries_first=1,
        entries_after=entries["edges"][0]["cursor"],
    )
    assert new_data == data
    # Make another query with the end cursor from the first query
    final_data, _ = utils.get_query_response(
        client,
        query_str,
        swhid=str(directory.swhid()),
        entries_first=2,
        entries_after=entries["pageInfo"]["endCursor"],
    )
    final_result_entries = final_data["directory"]["entries"]
    # endcursor from the first query will be the first item cursor here
    # FIXME, this behaviour is not in compliance with the relay spec.
    # With relay spec, items after the given cursor ($after) will be returned
    assert (
        final_result_entries["edges"][0]["cursor"] == entries["pageInfo"]["endCursor"]
    )
    assert final_result_entries["nodes"] == [
        {"name": {"text": directory.entries[0].name.decode()}},
        {"name": {"text": directory.entries[2].name.decode()}},
    ]
