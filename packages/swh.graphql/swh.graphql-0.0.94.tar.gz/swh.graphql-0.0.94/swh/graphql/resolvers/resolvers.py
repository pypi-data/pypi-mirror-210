# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""
High level resolvers
"""

# Any schema attribute can be resolved by any of the following ways
# and in the following priority order
# - In this module using a decorator (eg: @visit_status.field("snapshot"))
#   Every object (type) is expected to resolve this way as they can accept arguments
#   eg: origin.visits takes arguments to paginate
# - As a property in the Node object (eg: resolvers.visit.BaseVisitNode.id)
#   Every scalar is expected to resolve this way
# - As an attribute/item in the object/dict returned by a backend (eg: Origin.url)

import datetime
from typing import Optional, Union

from ariadne import ObjectType, UnionType
from graphql.type import GraphQLResolveInfo

from swh.graphql import resolvers as rs
from swh.graphql.utils import utils
from swh.model.model import TimestampWithTimezone

from .resolver_factory import (
    ConnectionObjectFactory,
    NodeObjectFactory,
    SimpleListFactory,
)

query: ObjectType = ObjectType("Query")
origin: ObjectType = ObjectType("Origin")
visit: ObjectType = ObjectType("Visit")
visit_status: ObjectType = ObjectType("VisitStatus")
snapshot: ObjectType = ObjectType("Snapshot")
snapshot_branch: ObjectType = ObjectType("Branch")
revision: ObjectType = ObjectType("Revision")
release: ObjectType = ObjectType("Release")
directory: ObjectType = ObjectType("Directory")
directory_entry: ObjectType = ObjectType("DirectoryEntry")
binary_string: ObjectType = ObjectType("BinaryString")
date: ObjectType = ObjectType("Date")
branch_target: ObjectType = ObjectType("BranchTarget")
release_target: ObjectType = ObjectType("ReleaseTarget")
directory_entry_target: ObjectType = ObjectType("DirectoryEntryTarget")
origin_search_result: ObjectType = ObjectType("OriginSearchResult")

branch_target_node: UnionType = UnionType("BranchTargetNode")
release_target_node: UnionType = UnionType("ReleaseTargetNode")
directory_entry_target_node: UnionType = UnionType("DirectoryEntryTargetNode")
resolve_swhid_result: UnionType = UnionType("ResolveSWHIDResult")


# Node resolvers
# A node resolver will return either an instance of a BaseNode subclass or None


@query.field("origin")
def origin_resolver(obj: None, info: GraphQLResolveInfo, **kw) -> rs.origin.OriginNode:
    return NodeObjectFactory.create("origin", obj, info, **kw)


@origin.field("latestVisit")
def latest_visit_resolver(
    obj: rs.origin.BaseOriginNode, info: GraphQLResolveInfo, **kw
) -> Optional[rs.visit.LatestVisitNode]:
    return NodeObjectFactory.create("latest-visit", obj, info, **kw)


@origin.field("latestSnapshot")
def latest_snapshot_resolver(
    obj: rs.origin.BaseOriginNode, info: GraphQLResolveInfo, **kw
) -> Optional[rs.snapshot.LatestSnapshotNode]:
    return NodeObjectFactory.create("latest-snapshot", obj, info, **kw)


@query.field("visit")
def visit_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.visit.OriginVisitNode:
    return NodeObjectFactory.create("visit", obj, info, **kw)


@visit.field("latestStatus")
def latest_visit_status_resolver(
    obj: rs.visit.BaseVisitNode, info: GraphQLResolveInfo, **kw
) -> Optional[rs.visit_status.LatestVisitStatusNode]:
    return NodeObjectFactory.create("latest-status", obj, info, **kw)


@query.field("snapshot")
def snapshot_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.snapshot.SnapshotNode:
    return NodeObjectFactory.create("snapshot", obj, info, **kw)


@visit_status.field("snapshot")
def visit_snapshot_resolver(
    obj: rs.visit_status.BaseVisitStatusNode, info: GraphQLResolveInfo, **kw
) -> Optional[rs.snapshot.VisitSnapshotNode]:
    return NodeObjectFactory.create("visit-snapshot", obj, info, **kw)


@query.field("revision")
def revision_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.revision.RevisionNode:
    return NodeObjectFactory.create("revision", obj, info, **kw)


@revision.field("directory")
def revision_directory_resolver(
    obj: rs.revision.BaseRevisionNode, info: GraphQLResolveInfo, **kw
) -> Optional[rs.directory.RevisionDirectoryNode]:
    return NodeObjectFactory.create("revision-directory", obj, info, **kw)


@query.field("release")
def release_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.release.ReleaseNode:
    return NodeObjectFactory.create("release", obj, info, **kw)


@query.field("directory")
def directory_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.directory.DirectoryNode:
    return NodeObjectFactory.create("directory", obj, info, **kw)


@query.field("directoryEntry")
def directory_entry_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.directory_entry.DirectoryEntryNode:
    return NodeObjectFactory.create("directory-entry", obj, info, **kw)


@directory_entry.field("target")
@release.field("target")
def generic_target_resolver(
    obj: Union[rs.release.BaseReleaseNode, rs.directory_entry.BaseDirectoryEntryNode],
    info: GraphQLResolveInfo,
    **kw,
) -> rs.target.TargetNode:
    return NodeObjectFactory.create("generic-target", obj, info, **kw)


@snapshot_branch.field("target")
def snapshot_branch_target_resolver(
    obj: rs.snapshot_branch.SnapshotBranchNode, info: GraphQLResolveInfo, **kw
) -> rs.target.BranchTargetNode:
    # Snapshot branch target is a special case
    return NodeObjectFactory.create("branch-target", obj, info, **kw)


@directory_entry_target.field("node")
@release_target.field("node")
@branch_target.field("node")
def generic_target_node_resolver(
    obj: rs.target.TargetNode, info: GraphQLResolveInfo, **kw
) -> Optional[
    Union[
        rs.revision.BaseRevisionNode,
        rs.release.BaseReleaseNode,
        rs.directory.BaseDirectoryNode,
        rs.content.BaseContentNode,
        rs.snapshot.BaseSnapshotNode,
    ]
]:
    if not obj or not obj.type:
        # Target can be None for a branch, return None in that case
        return None
    return NodeObjectFactory.create(f"target-{obj.type}", obj, info, **kw)


@query.field("contentByHashes")
def content_by_hashes_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.content.ContentbyHashesNode:
    return NodeObjectFactory.create("content-by-hashes", obj, info, **kw)


@origin_search_result.field("node")
def origin_search_node_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.origin.TargetOriginNode:
    return NodeObjectFactory.create("target-origin", obj, info, **kw)


# Connection resolvers
# A connection resolver should return an instance of BaseConnection


@query.field("origins")
def origins_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.origin.OriginConnection:
    return ConnectionObjectFactory.create("origins", obj, info, **kw)


@origin.field("visits")
def visits_resolver(
    obj: rs.origin.BaseOriginNode, info: GraphQLResolveInfo, **kw
) -> rs.visit.OriginVisitConnection:
    return ConnectionObjectFactory.create("origin-visits", obj, info, **kw)


@origin.field("snapshots")
def origin_snapshots_resolver(
    obj: rs.origin.BaseOriginNode, info: GraphQLResolveInfo, **kw
) -> rs.snapshot.OriginSnapshotConnection:
    return ConnectionObjectFactory.create("origin-snapshots", obj, info, **kw)


@visit.field("statuses")
def visitstatus_resolver(
    obj: rs.visit.BaseVisitNode, info: GraphQLResolveInfo, **kw
) -> rs.visit_status.VisitStatusConnection:
    return ConnectionObjectFactory.create("visit-status", obj, info, **kw)


@snapshot.field("branches")
def snapshot_branches_resolver(
    obj: rs.snapshot.BaseSnapshotNode, info: GraphQLResolveInfo, **kw
) -> rs.snapshot_branch.SnapshotBranchConnection:
    return ConnectionObjectFactory.create("snapshot-branches", obj, info, **kw)


@revision.field("parents")
def revision_parents_resolver(
    obj: rs.revision.BaseRevisionNode, info: GraphQLResolveInfo, **kw
) -> rs.revision.ParentRevisionConnection:
    return ConnectionObjectFactory.create("revision-parents", obj, info, **kw)


@revision.field("revisionLog")
def revision_log_resolver(
    obj: rs.revision.BaseRevisionNode, info: GraphQLResolveInfo, **kw
) -> rs.revision.LogRevisionConnection:
    return ConnectionObjectFactory.create("revision-log", obj, info, **kw)


@directory.field("entries")
def directory_entries_resolver(
    obj: rs.directory.BaseDirectoryNode, info: GraphQLResolveInfo, **kw
) -> rs.directory_entry.DirectoryEntryConnection:
    return ConnectionObjectFactory.create("directory-entries", obj, info, **kw)


@query.field("originSearch")
def origin_search_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.search.OriginSearchConnection:
    return ConnectionObjectFactory.create("origin-search", obj, info, **kw)


# Simple list resolvers (lists without paginations)


@query.field("contentsBySWHID")
def contnets_by_swhid_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.content.ContentSwhidList:
    return SimpleListFactory.create("contents-swhid", obj, info, **kw)


@query.field("contentsByHashes")
def contnets_by_hashes_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.content.ContentHashList:
    return SimpleListFactory.create("contents-hashes", obj, info, **kw)


@query.field("resolveSWHID")
def resolve_swhid_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.swhid.ResolveSWHIDList:
    return SimpleListFactory.create("resolve-swhid", obj, info, **kw)


@revision.field("author")
def revision_author_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.revision.RevisionNode:
    return SimpleListFactory.create("revision-author", obj, info, **kw)


@revision.field("committer")
def revision_committer_resolver(
    obj: None, info: GraphQLResolveInfo, **kw
) -> rs.revision.RevisionNode:
    return SimpleListFactory.create("revision-committer", obj, info, **kw)


@release.field("author")
def release_author_resolver(
    obj: rs.release.BaseReleaseNode, info: GraphQLResolveInfo, **kw
) -> rs.revision.RevisionNode:
    return SimpleListFactory.create("release-author", obj, info, **kw)


# Other resolvers


@release_target_node.type_resolver
@directory_entry_target_node.type_resolver
@branch_target_node.type_resolver
@resolve_swhid_result.type_resolver
def union_resolver(
    obj: Union[
        rs.revision.BaseRevisionNode,
        rs.release.BaseReleaseNode,
        rs.directory.BaseDirectoryNode,
        rs.content.BaseContentNode,
        rs.snapshot.BaseSnapshotNode,
    ],
    *_,
) -> str:
    """
    Generic resolver for all the union types
    """
    return obj.is_type_of()


# BinaryString resolvers


@binary_string.field("text")
def binary_string_text_resolver(obj: bytes, *args, **kw) -> str:
    return obj.decode(utils.ENCODING, "replace")


@binary_string.field("base64")
def binary_string_base64_resolver(obj: bytes, *args, **kw) -> str:
    return utils.get_b64_string(obj)


# Date object resolver


@date.field("date")
def date_date_resolver(
    obj: TimestampWithTimezone, *args: GraphQLResolveInfo, **kw
) -> datetime.datetime:
    # This will be serialised as a DateTime Scalar
    return obj.to_datetime()


@date.field("offset")
def date_offset_resolver(
    obj: TimestampWithTimezone, *args: GraphQLResolveInfo, **kw
) -> bytes:
    # This will be serialised as a Binary string
    return obj.offset_bytes
