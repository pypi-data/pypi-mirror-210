from __future__ import annotations
import logging
from unittest import TestCase

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

class Test(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

