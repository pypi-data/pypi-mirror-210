# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

# import pkg_resources
import os
from pathlib import Path

from ariadne import gql, load_schema_from_path, make_executable_schema
from ariadne.validation import cost_validator

from .resolvers import resolvers, scalars

type_defs = gql(
    # pkg_resources.resource_string("swh.graphql", "schema/schema.graphql").decode()
    load_schema_from_path(
        os.path.join(Path(__file__).parent.resolve(), "schema", "schema.graphql")
    )
)

schema = make_executable_schema(
    type_defs,
    resolvers.query,
    resolvers.origin,
    resolvers.visit,
    resolvers.visit_status,
    resolvers.snapshot,
    resolvers.snapshot_branch,
    resolvers.revision,
    resolvers.release,
    resolvers.directory,
    resolvers.directory_entry,
    resolvers.branch_target,
    resolvers.branch_target_node,
    resolvers.release_target,
    resolvers.release_target_node,
    resolvers.directory_entry_target,
    resolvers.directory_entry_target_node,
    resolvers.resolve_swhid_result,
    resolvers.origin_search_result,
    resolvers.binary_string,
    resolvers.date,
    scalars.id_scalar,
    scalars.datetime_scalar,
    scalars.swhid_scalar,
)


def validation_rules(context, document, data):
    from .server import graphql_cfg

    if context["request"].user.is_authenticated:
        max_query_cost = graphql_cfg["max_query_cost"]["user"]
    else:
        max_query_cost = graphql_cfg["max_query_cost"]["anonymous"]

    if max_query_cost:
        return [
            cost_validator(maximum_cost=max_query_cost, variables=data.get("variables"))
        ]
    # no limit is applied when max_query_cost is set to 0 or None
    return None
