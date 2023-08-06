from __future__ import annotations
import logging
import os
from pprint import pprint
from urllib.parse import parse_qs

from starlette.responses import Response
from starlette.staticfiles import StaticFiles as StarletteStaticFiles, PathLike
from starlette.types import Scope

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

class StaticFiles(StarletteStaticFiles):
    def file_response(
            self,
            full_path: PathLike,
            stat_result: os.stat_result,
            scope: Scope,
            *args,
            **kwargs,
    ) -> Response:
        response = super().file_response(full_path, stat_result, scope, *args, **kwargs)

        if query_string := scope.get("query_string"):
            query = parse_qs(query_string)
            if b"v" in query:
                response.headers["Cache-Control"] = "public, max-age=31536000"
        # pprint(args)
        # pprint(kwargs)
        # response.headers["Cache-Control"] = "public, max-age=31536000"
        return response
