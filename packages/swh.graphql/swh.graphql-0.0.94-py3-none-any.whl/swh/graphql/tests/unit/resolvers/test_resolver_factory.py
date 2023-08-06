# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from swh.graphql.resolvers import resolver_factory


class TestFactory:
    def test_get_node_resolver_invalid_type(self):
        with pytest.raises(AttributeError):
            resolver_factory.NodeObjectFactory().create("invalid", None, None)

    def test_get_connection_resolver_invalid_type(self):
        with pytest.raises(AttributeError):
            resolver_factory.ConnectionObjectFactory().create("invalid", None, None)

    def test_get_base_list_resolver_invalid_type(self):
        with pytest.raises(AttributeError):
            resolver_factory.SimpleListFactory().create("invalid", None, None)
