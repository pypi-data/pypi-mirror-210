# Copyright (C) 2022-2023 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import List, Optional

from .base_connection import BaseList
from .content import BaseContentNode
from .directory import BaseDirectoryNode
from .release import BaseReleaseNode
from .revision import BaseRevisionNode
from .snapshot import BaseSnapshotNode


class ResolveSWHIDList(BaseList):
    def _get_results(self) -> Optional[List]:
        swhid = self.kwargs.get("swhid")
        object_type = swhid.object_type
        object_id = swhid.object_id
        nodes = None
        if object_type.name == "REVISION":
            self._node_class = BaseRevisionNode
            nodes = self.archive.get_revisions([object_id])
        elif object_type.name == "RELEASE":
            self._node_class = BaseReleaseNode
            nodes = self.archive.get_releases([object_id])
        elif object_type.name == "SNAPSHOT":
            self._node_class = BaseSnapshotNode
            # get_snapshot will return a single object
            nodes = [self.archive.get_snapshot(object_id, verify=True)]
        elif object_type.name == "DIRECTORY":
            self._node_class = BaseDirectoryNode
            # get_directory will return a single object
            nodes = [self.archive.get_directory(object_id, verify=True)]
        elif object_type.name == "CONTENT":
            self._node_class = BaseContentNode
            nodes = self.archive.get_contents(hashes={"sha1_git": object_id})
        if not nodes or nodes[0] is None:
            nodes = None
        return nodes
