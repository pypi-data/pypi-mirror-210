# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import List, Optional, Tuple

from swh.graphql.errors import DataError
from swh.graphql.utils import utils
from swh.model.model import CoreSWHID, SnapshotBranch
from swh.storage.interface import PagedResult

from .base_connection import BaseConnection, ConnectionData
from .base_node import BaseNode


class SnapshotBranchNode(BaseNode):

    obj: "SnapshotBranchConnection"

    def _get_node_from_data(self, node_data: Tuple[bytes, Optional[SnapshotBranch]]):
        # node_data is a tuple as returned by _get_connection_data in SnapshotBranchConnection
        # overriding to support this special data structure
        branch_name, branch_obj = node_data
        updated_node_data = {
            # Name of the branch, exposed in the schema
            "name": branch_name,
            # Type of the branch, exposed in the schema
            "type": branch_obj.target_type.value if branch_obj else None,
            # not exposed in the schema, to be used by the target object
            "snapshot_id": self._get_snapshot_swhid().object_id,
            # not exposed in the schema, to be used by the target object
            "branch_obj": branch_obj,
        }
        return super()._get_node_from_data(updated_node_data)

    def _get_snapshot_swhid(self) -> CoreSWHID:
        from .snapshot import BaseSnapshotNode

        # As of now parent of SnapshotBranch will always be a SnapshotBranchConnection
        # and self.obj.obj will always be a BaseSnapshot object
        # override this method for SnapshotBranch nodes reachable by some other path
        if not isinstance(self.obj.obj, BaseSnapshotNode):
            # This is not expected to happen with the existing endpoints
            raise DataError(
                "SnapshotBranch is accessed outside a SnapshotBranchConnection context"
            )
        return self.obj.obj.swhid


class SnapshotBranchConnection(BaseConnection):
    """
    Connection resolver for the branches in a snapshot
    """

    from .snapshot import BaseSnapshotNode

    obj: BaseSnapshotNode

    _node_class = SnapshotBranchNode

    def _get_connection_data(self) -> ConnectionData:
        branches = self.archive.get_snapshot_branches(
            snapshot=self.obj.swhid.object_id,
            after=self._get_after_arg(),
            first=self._get_first_arg(),
            target_types=self.kwargs.get("types"),
            name_include=self._get_name_include_arg(),
            name_exclude_prefix=self._get_name_exclude_prefix_arg(),
        )
        end_cursor: Optional[bytes] = branches.get("next_branch") if branches else None
        # FIXME, this pagination is not consistent with other connections
        # FIX in swh-storage to return PagedResult
        # STORAGE-TODO

        # each result item will be converted to a dict in _get_node_from_data
        # method in the node class
        results: List[Tuple[bytes, Optional[SnapshotBranch]]] = (
            list(branches["branches"].items()) if branches else []
        )
        return ConnectionData(
            paged_result=PagedResult(
                results=results,
                next_page_token=end_cursor.decode() if end_cursor else None,
            )
        )

    def _get_after_arg(self):
        # after argument must be an empty string by default
        after = super()._get_after_arg()
        return after.encode() if after else b""

    def _get_name_include_arg(self):
        name_include = self.kwargs.get("nameInclude", None)
        return name_include.encode() if name_include else None

    def _get_name_exclude_prefix_arg(self):
        name_exclude_prefix = self.kwargs.get("nameExcludePrefix", None)
        return name_exclude_prefix.encode() if name_exclude_prefix else None

    def _get_index_cursor(self, index: int, node: SnapshotBranchNode):
        # Snapshot branch is using a different cursor, hence the override
        return utils.get_encoded_cursor(node.name)
