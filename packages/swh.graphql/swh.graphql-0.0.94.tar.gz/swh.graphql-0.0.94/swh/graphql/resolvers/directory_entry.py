# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import List

from swh.graphql.utils import utils
from swh.model.model import DirectoryEntry, ObjectType, Sha1Git

from .base_connection import BaseConnection, ConnectionData
from .base_node import BaseNode


class BaseDirectoryEntryNode(BaseNode):
    def target_hash(self) -> Sha1Git:
        assert self._node is not None
        return self._node.target

    def target_type(self) -> ObjectType:
        mapping = {
            "file": ObjectType.CONTENT,
            "dir": ObjectType.DIRECTORY,
            "rev": ObjectType.REVISION,
        }
        assert self._node is not None
        return mapping[self._node.type]


class DirectoryEntryNode(BaseDirectoryEntryNode):
    """
    Node resolver for a directory entry requested with a
    directory SWHID and a relative path
    """

    def _get_node_data(self):
        # STORAGE-TODO, archive is returning a dict
        # return DirectoryEntry object instead
        return self.archive.get_directory_entry_by_path(
            directory_id=self.kwargs.get("directorySWHID").object_id,
            path=self.kwargs.get("path"),
        )


class DirectoryEntryConnection(BaseConnection):
    """
    Connection resolver for entries in a directory
    """

    from .directory import BaseDirectoryNode

    obj: BaseDirectoryNode

    _node_class = BaseDirectoryEntryNode

    def _get_connection_data(self) -> ConnectionData:
        # FIXME, using dummy(local) pagination, move pagination to backend
        # STORAGE-TODO
        entries: List[DirectoryEntry] = self.archive.get_directory_entries(
            self.obj.swhid.object_id
        ).results
        name_include = self.kwargs.get("nameInclude")
        if name_include is not None:
            # STORAGE-TODO, move this filter to swh-storage
            entries = [
                x
                for x in entries
                if name_include.casefold() in x.name.decode().casefold()
            ]
        return utils.get_local_paginated_data(
            entries, self._get_first_arg(), self._get_after_arg()
        )
