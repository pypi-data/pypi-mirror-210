# Copyright (C) 2023 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os

from starlette.templating import Jinja2Templates


async def explorer_page(request):
    from swh.graphql.server import graphql_cfg

    auth = graphql_cfg.get("auth")
    if auth and "public_server" not in auth:
        # ensure to not break already deployed service
        auth["public_server"] = auth["server"]

    templates = Jinja2Templates(directory=os.path.dirname(__file__))
    return templates.TemplateResponse(
        "explorer.html", {"request": request, "auth": auth}
    )
