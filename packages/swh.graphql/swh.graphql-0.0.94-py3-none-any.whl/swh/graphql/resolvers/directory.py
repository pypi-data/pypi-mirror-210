# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import TYPE_CHECKING, Optional, Union

from swh.graphql.errors import NullableObjectError
from swh.model.model import Directory

from .base_node import BaseSWHNode
from .revision import BaseRevisionNode


class BaseDirectoryNode(BaseSWHNode):
    """
    Base resolver for all the directory nodes
    """

    def is_type_of(self):
        return "Directory"


class DirectoryNode(BaseDirectoryNode):
    """
    Node resolver for a directory requested directly with its SWHID
    """

    def _get_node_data(self):
        swhid = self.kwargs.get("swhid")
        return self.archive.get_directory(directory_id=swhid.object_id, verify=True)


class RevisionDirectoryNode(BaseDirectoryNode):
    """
    Node resolver for a directory requested from a revision
    """

    # Revision directory is not using the target indirection,
    # hence this implementation (not using TargetDirectoryNode)

    _can_be_null = True
    obj: BaseRevisionNode

    def _get_node_data(self) -> Directory:
        # self.obj.directory_hash is the requested directory Id
        directory_id = self.obj.directory_hash()
        if directory_id is None:
            raise NullableObjectError()
        directory = self.archive.get_directory(directory_id=directory_id, verify=False)
        assert directory is not None
        return directory


class TargetDirectoryNode(BaseDirectoryNode):
    """
    Node resolver for a directory requested as a target
    """

    if TYPE_CHECKING:  # pragma: no cover
        from .target import BranchTargetNode, TargetNode

        obj: Union[
            BranchTargetNode,
            TargetNode,
        ]
    _can_be_null = True

    def _get_node_data(self) -> Optional[Directory]:
        # existing directory in the archive, hence verify is False
        return self.archive.get_directory(
            directory_id=self.obj.target_hash, verify=False
        )
