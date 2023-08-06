# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import List, Optional, Union

from swh.graphql.errors import DataError, InvalidInputError
from swh.model import hashutil
from swh.model.model import Content
from swh.storage.interface import HashDict, TotalHashDict

from .base_connection import BaseList
from .base_node import BaseSWHNode
from .target import BranchTargetNode, TargetNode


def read_and_validate_content_hashes(hashes):
    try:
        return {
            hash_type: hashutil.hash_to_bytes(hash_value)
            for (hash_type, hash_value) in hashes
        }
    except ValueError as e:
        # raise an input error in case of an invalid hash
        raise InvalidInputError("Invalid content hash", e)


class BaseContentNode(BaseSWHNode):
    """
    Base resolver for all the content nodes
    """

    @property
    def hashes(self):
        # FIXME, use a Node instead
        return {k: v.hex() for (k, v) in self._node.hashes().items()}

    @property
    def id(self):
        return self._node.sha1_git

    @property
    def data(self):
        # FIXME, return a Node object
        # FIXME, add more ways to retrieve data like binary string
        archive_url = "https://archive.softwareheritage.org/api/1/"
        content_sha1 = self._node.hashes()["sha1"]
        return {
            "url": f"{archive_url}content/sha1:{content_sha1.hex()}/raw/",
        }

    @property
    def mimeType(self):
        # FIXME, fetch data from the indexers
        return None

    @property
    def language(self):
        # FIXME, fetch data from the indexers
        return None

    @property
    def license(self):
        # FIXME, fetch data from the indexers
        return None

    def is_type_of(self):
        # is_type_of is required only when resolving a UNION type
        # This is for ariadne to return the right type
        return "Content"


class ContentbyHashesNode(BaseContentNode):
    """
    Node resolver for a content requested with all of its hashes
    A single content object will be returned
    """

    def _get_node_data(self) -> Optional[Content]:
        hashes: TotalHashDict = read_and_validate_content_hashes(self.kwargs.items())
        contents = self.archive.get_contents(hashes=hashes)
        if len(contents) > 1:
            # This situation is not expected to happen IRL
            raise DataError("Content hash conflict for the set ", hashes)
        return contents[0] if contents else None


class TargetContentNode(BaseContentNode):
    """
    Node resolver for a content requested as a target
    """

    _can_be_null = True
    obj: Union[
        TargetNode,
        BranchTargetNode,
    ]

    def _get_node_data(self) -> Optional[Content]:
        # FIXME, this is not considering hash collisions
        # and could return a wrong object in very rare situations
        contents = self.archive.get_contents(hashes={"sha1_git": self.obj.target_hash})
        # always returning the first content from the storage
        return contents[0] if contents else None


class ContentSwhidList(BaseList):
    """
    Return a non paginated list of contents for the given SWHID
    This will return a single item in most of the cases
    """

    _node_class = BaseContentNode

    def _get_results(self) -> List[Content]:
        hashes = {"sha1_git": self.kwargs.get("swhid").object_id}
        return self.archive.get_contents(hashes=hashes)


class ContentHashList(BaseList):
    """
    Return a non paginated list of contents for the given hashes
    This will return a single item in most of the cases
    """

    _node_class = BaseContentNode

    def _get_results(self) -> List[Content]:
        hashes: HashDict = read_and_validate_content_hashes(self.kwargs.items())
        if not hashes:
            raise InvalidInputError("At least one of the four hashes must be provided")
        return self.archive.get_contents(hashes=hashes)
