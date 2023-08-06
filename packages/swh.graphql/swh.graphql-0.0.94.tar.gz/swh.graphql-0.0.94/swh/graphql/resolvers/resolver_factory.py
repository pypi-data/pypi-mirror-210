# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import logging
from typing import ClassVar, Dict, Type

from swh.core import statsd
from swh.graphql.errors import NullableObjectError

from .base_connection import BaseConnection, BaseList
from .base_node import BaseNode
from .content import (
    ContentbyHashesNode,
    ContentHashList,
    ContentSwhidList,
    TargetContentNode,
)
from .directory import DirectoryNode, RevisionDirectoryNode, TargetDirectoryNode
from .directory_entry import DirectoryEntryConnection, DirectoryEntryNode
from .origin import OriginConnection, OriginNode, TargetOriginNode
from .person import ReleaseAuthorList, RevisionAuthorList, RevisionCommitterList
from .release import ReleaseNode, TargetReleaseNode
from .revision import (
    LogRevisionConnection,
    ParentRevisionConnection,
    RevisionNode,
    TargetRevisionNode,
)
from .search import OriginSearchConnection
from .snapshot import (
    LatestSnapshotNode,
    OriginSnapshotConnection,
    SnapshotNode,
    TargetSnapshotNode,
    VisitSnapshotNode,
)
from .snapshot_branch import SnapshotBranchConnection
from .swhid import ResolveSWHIDList
from .target import BranchTargetNode, TargetNode
from .visit import LatestVisitNode, OriginVisitConnection, OriginVisitNode
from .visit_status import LatestVisitStatusNode, VisitStatusConnection

this_statsd = statsd.Statsd(namespace="swh_graphql")
logger = logging.getLogger(__name__)


class NodeObjectFactory:
    mapping: ClassVar[Dict[str, Type[BaseNode]]] = {
        "origin": OriginNode,
        "visit": OriginVisitNode,
        "latest-visit": LatestVisitNode,
        "latest-status": LatestVisitStatusNode,
        "latest-snapshot": LatestSnapshotNode,
        "visit-snapshot": VisitSnapshotNode,
        "snapshot": SnapshotNode,
        "revision": RevisionNode,
        "revision-directory": RevisionDirectoryNode,
        "release": ReleaseNode,
        "directory": DirectoryNode,
        "directory-entry": DirectoryEntryNode,
        "content-by-hashes": ContentbyHashesNode,
        "generic-target": TargetNode,
        "branch-target": BranchTargetNode,
        "target-origin": TargetOriginNode,
        "target-snapshot": TargetSnapshotNode,
        "target-revision": TargetRevisionNode,
        "target-release": TargetReleaseNode,
        "target-directory": TargetDirectoryNode,
        "target-content": TargetContentNode,
    }

    @classmethod
    def create(cls, node_type: str, obj, info, *args, **kw):
        # FIXME, add to the sentry transaction
        resolver = cls.mapping.get(node_type)
        if not resolver:
            raise AttributeError(f"Invalid node type: {node_type}")
        with this_statsd.timed("node_query_seconds", tags={"node": node_type}):
            try:
                node_obj = resolver(obj, info, *args, **kw)
            except NullableObjectError:
                # Return None instead of the object
                # FIXME, add to the sentry transaction
                logger.warning("Null %s object", node_type)
                node_obj = None
        return node_obj


class ConnectionObjectFactory:
    mapping: ClassVar[Dict[str, Type[BaseConnection]]] = {
        "origins": OriginConnection,
        "origin-visits": OriginVisitConnection,
        "origin-snapshots": OriginSnapshotConnection,
        "visit-status": VisitStatusConnection,
        "snapshot-branches": SnapshotBranchConnection,
        "revision-parents": ParentRevisionConnection,
        "revision-log": LogRevisionConnection,
        "directory-entries": DirectoryEntryConnection,
        "origin-search": OriginSearchConnection,
    }

    @classmethod
    def create(cls, connection_type: str, obj, info, *args, **kw):
        # FIXME, add to the sentry transaction
        resolver = cls.mapping.get(connection_type)
        if not resolver:
            raise AttributeError(f"Invalid connection type: {connection_type}")
        with this_statsd.timed(
            "connection_query_seconds", tags={"connection": connection_type}
        ):
            return resolver(obj, info, *args, **kw)


class SimpleListFactory:
    mapping: ClassVar[Dict[str, Type[BaseList]]] = {
        "resolve-swhid": ResolveSWHIDList,
        "revision-author": RevisionAuthorList,
        "revision-committer": RevisionCommitterList,
        "release-author": ReleaseAuthorList,
        "contents-swhid": ContentSwhidList,
        "contents-hashes": ContentHashList,
    }

    @classmethod
    def create(cls, list_type: str, obj, info, *args, **kw):
        # FIXME, add to the sentry transaction
        resolver = cls.mapping.get(list_type)
        if not resolver:
            raise AttributeError(f"Invalid list type: {list_type}")
        with this_statsd.timed("list_query_seconds", tags={"list": list_type}):
            # invoke the get_results method to return the list
            return resolver(obj, info, *args, **kw).get_results()
