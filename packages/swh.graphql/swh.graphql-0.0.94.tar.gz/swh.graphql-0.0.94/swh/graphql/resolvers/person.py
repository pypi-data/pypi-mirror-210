# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import List, Optional

from swh.model.model import Person as StoragePerson

from .base_connection import BaseList
from .base_node import BaseNode
from .release import BaseReleaseNode
from .revision import BaseRevisionNode


class Person(BaseNode):
    pass


def get_person_list(person: Optional[StoragePerson]) -> List[StoragePerson]:
    return [person] if person else []


class RevisionAuthorList(BaseList):
    """
    List of revision authors
    """

    obj: BaseRevisionNode

    _node_class = Person

    def _get_results(self) -> List[StoragePerson]:
        """
        Author is a single object in the current data model,
        return it as a list to support future evolutions

        No backend fetching required as the data exists in
        the parent object (revision)
        """

        return get_person_list(self.obj.author)


class RevisionCommitterList(BaseList):
    obj: BaseRevisionNode

    _node_class = Person

    def _get_results(self) -> List[StoragePerson]:
        """
        Committer is a single object in the current data model,
        return it as a list to support future evolutions

        No backend fetching required as the data exists in
        the parent object (revision)
        """

        return get_person_list(self.obj.committer)


class ReleaseAuthorList(BaseList):
    obj: BaseReleaseNode

    _node_class = Person

    def _get_results(self) -> List[StoragePerson]:
        """
        Author is a single object in the current data model,
        return it as a list to support future evolutions

        No backend fetching required as the data exists in
        the parent object (release)
        """

        return get_person_list(self.obj.author)
