# Copyright (C) 2022-2023 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from starlette.middleware.base import BaseHTTPMiddleware

from swh.core import statsd


class LogMiddleware(BaseHTTPMiddleware):
    # Starlette/ASGI middleware for logging request information

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statsd = statsd.Statsd(namespace="swh_graphql")

    async def dispatch(self, request, call_next):
        if request.method == "POST":
            # This is a query request
            self.statsd.increment("query_total")
            # FIXME, add a metric for total query cost
            # FIXME, start a sentry transaction here
        with self.statsd.timed("query_seconds"):
            # total exec time metric (for both POST and GET)
            response = await call_next(request)
        return response
