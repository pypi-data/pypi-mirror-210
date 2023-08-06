# Copyright (C) 2023 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information
from unittest.mock import ANY, call

from swh.core import statsd

from . import utils
from ..data import get_directories, get_origins


def test_node_usage_logger(client, mocker):
    statsd_report = mocker.patch.object(statsd.Statsd, "_report")
    query_str = """
    query getOrigin($url: String!) {
      origin(url: $url) {
        url
      }
    }
    """
    response, _ = utils.get_query_response(client, query_str, url=get_origins()[0].url)
    statsd_calls = statsd_report.mock_calls
    assert statsd_calls == [
        # total count
        call("query_total", "c", 1, None, 1),
        # node duration
        call("node_query_seconds", "ms", ANY, {"node": "origin"}, 1),
        # total query  duration
        call("query_seconds", "ms", ANY, {}, 1),
    ]


def test_connection_usage_logger(client, mocker):
    statsd_report = mocker.patch.object(statsd.Statsd, "_report")
    query_str = """
    query getOrigins($first: Int!) {
      origins(first: $first) {
        nodes {
          url
        }
      }
    }
    """
    response, _ = utils.get_query_response(client, query_str, first=10)
    statsd_calls = statsd_report.mock_calls
    assert statsd_calls == [
        # total count
        call("query_total", "c", 1, None, 1),
        # connection duration
        call("connection_query_seconds", "ms", ANY, {"connection": "origins"}, 1),
        # total query  duration
        call("query_seconds", "ms", ANY, {}, 1),
    ]


def test_list_usage_logger(client, mocker):
    statsd_report = mocker.patch.object(statsd.Statsd, "_report")
    query_str = """
    query resolve($swhid: SWHID!) {
      resolveSWHID(swhid: $swhid) {
        ... on Directory {
          swhid
        }
      }
    }
    """
    response, _ = utils.get_query_response(
        client, query_str, swhid=str(get_directories()[0].swhid())
    )
    statsd_calls = statsd_report.mock_calls
    assert statsd_calls == [
        # total count
        call("query_total", "c", 1, None, 1),
        # list duration
        call("list_query_seconds", "ms", ANY, {"list": "resolve-swhid"}, 1),
        # total query  duration
        call("query_seconds", "ms", ANY, {}, 1),
    ]


def test_multiple_entrypoints_query_logger(client, mocker):
    statsd_report = mocker.patch.object(statsd.Statsd, "_report")
    query_str = """
    query big($url: String!, $first: Int!) {
      origins(first: $first) {
        nodes {
          url
        }
      }

      origin(url: $url) {
        url
      }
    }
    """
    response, _ = utils.get_query_response(
        client, query_str, url=get_origins()[0].url, first=2
    )
    statsd_calls = statsd_report.mock_calls
    assert statsd_calls == [
        # total count
        call("query_total", "c", 1, None, 1),
        ANY,
        ANY,
        # total query  duration
        call("query_seconds", "ms", ANY, {}, 1),
    ]
    # call order could change after moving to async
    assert call("node_query_seconds", "ms", ANY, {"node": "origin"}, 1) in statsd_calls
    assert (
        call("connection_query_seconds", "ms", ANY, {"connection": "origins"}, 1)
        in statsd_calls
    )
