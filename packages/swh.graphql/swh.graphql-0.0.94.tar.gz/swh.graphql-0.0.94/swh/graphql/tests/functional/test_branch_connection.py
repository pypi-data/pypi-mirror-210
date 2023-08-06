# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from . import utils
from ..data import get_releases, get_snapshots_with_multiple_alias


def get_branches(client, **kwargs) -> tuple:
    query_str = """
    query getSnapshot($swhid: SWHID!, $first: Int!, $after: String, $types: [BranchType],
    $nameInclude: String, $excludePrefix: String) {
      snapshot(swhid: $swhid) {
        branches(first: $first, after: $after, types: $types, nameInclude: $nameInclude,
        nameExcludePrefix: $excludePrefix ) {
          pageInfo {
            endCursor
          }
          nodes {
            name {
              text
            }
            type
            target {
              type
              resolveChain {
                text
              }
              swhid
              node {
                __typename
                ...on Revision {
                  swhid
                }
                ...on Release {
                  swhid
                }
                ...on Content {
                  swhid
                }
                ...on Directory {
                  swhid
                }
                ...on Snapshot {
                  swhid
                }
              }
            }
          }
        }
      }
    }
    """
    return utils.get_query_response(client, query_str, **kwargs)


def test_get_data(client):
    swhid = "swh:1:snp:0e7f84ede9a254f2cd55649ad5240783f557e65f"
    data, errors = get_branches(client, swhid=swhid, first=10, types=["revision"])
    assert len(data["snapshot"]["branches"]["nodes"]) == 1
    # filter 'type' will return a single revision object and is used to assert data
    node = data["snapshot"]["branches"]["nodes"][0]
    assert node == {
        "name": {"text": "target/revision"},
        "type": "revision",
        "target": {
            "type": "revision",
            "resolveChain": None,
            "swhid": "swh:1:rev:66c7c1cd9673275037140f2abff7b7b11fc9439c",
            "node": {
                "__typename": "Revision",
                "swhid": "swh:1:rev:66c7c1cd9673275037140f2abff7b7b11fc9439c",
            },
        },
    }


def test_get_branches_with_one_level_alias(client):
    swhid = "swh:1:snp:0e7f84ede9a254f2cd55649ad5240783f557e65f"
    data, _ = get_branches(client, swhid=swhid, first=10, types=["alias"])
    node = data["snapshot"]["branches"]["nodes"][0]

    assert node == {
        "name": {"text": "target/alias"},  # original name
        "type": "alias",
        "target": {
            "swhid": "swh:1:rev:66c7c1cd9673275037140f2abff7b7b11fc9439c",
            "type": "revision",
            "resolveChain": [{"text": "target/revision"}],
            "node": {
                "__typename": "Revision",
                "swhid": "swh:1:rev:66c7c1cd9673275037140f2abff7b7b11fc9439c",
            },
        },
    }


def test_get_branches_alias_without_a_target(client):
    snapshot = get_snapshots_with_multiple_alias()[0]
    data, errors = get_branches(
        client,
        swhid=str(snapshot.swhid()),
        first=1,
        types=["alias"],
        nameInclude="alias1",
    )
    node = data["snapshot"]["branches"]["nodes"][0]
    assert node == {
        "name": {"text": "target/alias1"},  # original name
        "type": "alias",
        "target": {
            "node": None,
            "type": None,
            "swhid": None,
            "resolveChain": [{"text": "target/alias2"}, {"text": "target/alias3"}],
        },
    }


def test_get_branches_with_multiple_alias_redirects(client):
    snapshot = get_snapshots_with_multiple_alias()[1]
    data, errors = get_branches(
        client,
        swhid=str(snapshot.swhid()),
        first=1,
        types=["alias"],
        nameInclude="alias1",
    )
    node = data["snapshot"]["branches"]["nodes"][0]
    assert node == {
        "name": {"text": "target/alias1"},  # original name
        "type": "alias",
        "target": {
            "type": "release",
            "resolveChain": [{"text": "target/alias2"}, {"text": "target/release"}],
            "swhid": str(get_releases()[0].swhid()),
            "node": {"__typename": "Release", "swhid": str(get_releases()[0].swhid())},
        },
    }


def test_get_branches_with_too_many_alias_redirects(client):
    snapshot = get_snapshots_with_multiple_alias()[2]
    data, errors = get_branches(
        client,
        swhid=str(snapshot.swhid()),
        first=1,
        types=["alias"],
        nameInclude="alias1",
    )
    node = data["snapshot"]["branches"]["nodes"][0]
    assert node == {
        "name": {"text": "target/alias1"},  # original name
        "type": "alias",
        "target": {
            "node": None,
            "type": None,
            "swhid": None,
            "resolveChain": [
                {"text": "target/alias2"},
                {"text": "target/alias3"},
                {"text": "target/alias4"},
                {"text": "target/alias5"},
                {"text": "target/alias6"},
            ],
        },
    }


def test_get_branches_with_infinite_alias_redirects(client):
    snapshot = get_snapshots_with_multiple_alias()[3]
    data, errors = get_branches(
        client,
        swhid=str(snapshot.swhid()),
        first=1,
        types=["alias"],
        nameInclude="alias1",
    )
    node = data["snapshot"]["branches"]["nodes"][0]
    assert node == {
        "name": {"text": "target/alias1"},  # original name
        "type": "alias",
        "target": {
            "node": None,
            "type": None,
            "swhid": None,
            "resolveChain": [
                {"text": "target/alias2"},
                {"text": "target/alias1"},
                {"text": "target/alias2"},
            ],
        },
    }


@pytest.mark.parametrize(
    "filter_type, count, target_type, swhid_pattern",
    [
        ("revision", 1, "Revision", "swh:1:rev"),
        ("release", 1, "Release", "swh:1:rel"),
        ("directory", 1, "Directory", "swh:1:dir"),
        ("content", 0, "Content", "swh:1:cnt"),
        ("snapshot", 1, "Snapshot", "swh:1:snp"),
    ],
)
def test_get_type_filter(client, filter_type, count, target_type, swhid_pattern):
    swhid = "swh:1:snp:0e7f84ede9a254f2cd55649ad5240783f557e65f"
    data, _ = get_branches(client, swhid=swhid, first=10, types=[filter_type])
    assert len(data["snapshot"]["branches"]["nodes"]) == count
    for node in data["snapshot"]["branches"]["nodes"]:
        assert node["target"]["resolveChain"] is None
        assert node["target"]["swhid"].startswith(swhid_pattern)
        assert node["target"]["node"]["__typename"] == target_type


@pytest.mark.parametrize(
    "filter_types, count",
    [
        (["revision", "release"], 2),
        (["revision", "snapshot", "release"], 3),
    ],
)
def test_get_type_filter_multiple(client, filter_types, count):
    swhid = "swh:1:snp:0e7f84ede9a254f2cd55649ad5240783f557e65f"
    data, _ = get_branches(client, swhid=swhid, first=10, types=filter_types)
    assert len(data["snapshot"]["branches"]["nodes"]) == count


@pytest.mark.parametrize("name", ["rel", "rev", "non-exist"])
def test_get_name_include_filter(client, name):
    swhid = "swh:1:snp:0e7f84ede9a254f2cd55649ad5240783f557e65f"
    data, _ = get_branches(client, swhid=swhid, first=10, nameInclude=name)
    for node in data["snapshot"]["branches"]["nodes"]:
        assert name in node["name"]["text"]


@pytest.mark.parametrize("name", ["target", "target/dir"])
def test_get_name_exclude_prefix_filter(client, name):
    swhid = "swh:1:snp:0e7f84ede9a254f2cd55649ad5240783f557e65f"
    data, _ = get_branches(client, swhid=swhid, first=10, excludePrefix=name)
    for node in data["snapshot"]["branches"]["nodes"]:
        assert not node["name"]["text"].startswith(name)


@pytest.mark.parametrize("count", [1, 2])
def test_get_first_arg(client, count):
    swhid = "swh:1:snp:0e7f84ede9a254f2cd55649ad5240783f557e65f"
    data, _ = get_branches(client, swhid=swhid, first=count)
    assert len(data["snapshot"]["branches"]["nodes"]) == count


def test_get_after_arg(client):
    swhid = "swh:1:snp:0e7f84ede9a254f2cd55649ad5240783f557e65f"
    first_data, _ = get_branches(client, swhid=swhid, first=1)
    end_cursor = first_data["snapshot"]["branches"]["pageInfo"]["endCursor"]
    node_name = first_data["snapshot"]["branches"]["nodes"][0]["name"]["text"]
    second_data, _ = get_branches(client, swhid=swhid, first=3, after=end_cursor)
    branches = second_data["snapshot"]["branches"]
    assert len(branches["nodes"]) == 3
    for node in branches["nodes"]:
        assert node["name"]["text"] > node_name
