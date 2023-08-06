# Copyright (C) 2022-2023 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import TYPE_CHECKING, Dict, Optional, Union

from swh.model.model import CoreSWHID
from swh.model.swhids import ObjectType as SwhidObjectType

from .base_node import BaseNode
from .snapshot_branch import SnapshotBranchNode


class BaseTargetNode(BaseNode):

    # 'node' field in this object is resolved in the top level

    @property
    def swhid(self) -> Optional[CoreSWHID]:
        # field exposed in the schema
        # use the target type and hash to construct the SWHID
        mapping = {  # to map models.ObjectId to swhids.ObjectId
            "snapshot": SwhidObjectType.SNAPSHOT,
            "revision": SwhidObjectType.REVISION,
            "release": SwhidObjectType.RELEASE,
            "directory": SwhidObjectType.DIRECTORY,
            "content": SwhidObjectType.CONTENT,
        }
        if self.target_hash and self.type:
            return CoreSWHID(object_type=mapping[self.type], object_id=self.target_hash)
        return None


class TargetNode(BaseTargetNode):
    """
    Intermediate node between an object and its target
    Created for schema clarity and to handle missing target
    nodes in the archive
    """

    if TYPE_CHECKING:  # pragma: no cover
        from .directory_entry import BaseDirectoryEntryNode
        from .release import BaseReleaseNode
        from .revision import BaseRevisionNode

        obj: Union[BaseReleaseNode, BaseDirectoryEntryNode, BaseRevisionNode]

    _can_be_null = True

    def _get_node_data(self) -> Optional[Dict]:
        # No exta data to fetch; everything is available from self.obj
        if not self.obj.target_hash():
            # No information to load the target, consider it as a None target
            return None
        return {
            # field exposed in the schema for some nodes
            "type": self.obj.target_type().value,
            # field NOT exposed in the schema
            # to be used while retrieving the node object
            "target_hash": self.obj.target_hash(),
        }


class BranchTargetNode(BaseTargetNode):
    # Return the final target and the chain

    obj: SnapshotBranchNode

    def _get_node_data(self) -> Dict:
        branch, chain = self.archive.get_branch_target(
            snapshot_id=self.obj.snapshot_id,
            branch_obj=self.obj.branch_obj,
            max_length=5,
        )
        return {
            # field exposed in the schema, return None instead of an empty list
            "resolveChain": chain if chain else None,
            # field exposed in the schema
            "type": branch.target_type.value if branch else None,
            # field NOT exposed in the schema
            # to be used while retrieving the node object
            "target_hash": branch.target if branch else None,
        }
