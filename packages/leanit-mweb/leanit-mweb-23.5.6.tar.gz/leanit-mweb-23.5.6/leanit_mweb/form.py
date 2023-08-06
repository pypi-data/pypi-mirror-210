from __future__ import annotations
import logging
from urllib.parse import parse_qsl

from multidict import MultiDict
from wtforms import Form as WtformsForm
logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

class Form(WtformsForm):

    @classmethod
    def from_request_data(cls, data: bytes) -> "cls":
        doc = MultiDict(parse_qsl(data.decode()))
        form = cls(doc)
        return form
