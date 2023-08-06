from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import hashlib
import os
import base64
import struct

def hash_password(password, rounds=10000):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, rounds)
    return base64.b64encode(struct.pack('>I', rounds) + salt + dk).decode()

def verify_password(hashed_password, clear_password):
    """
    :param hashed_password: password hash (e.g. from database)
    :param clear_password: password in clear text (e.g. from user input)
    :return: True if password matches, False otherwise
    """
    decoded = base64.b64decode(hashed_password)
    rounds = struct.unpack('>I', decoded[:4])[0]
    salt = decoded[4:20]
    dk = decoded[20:]
    return dk == hashlib.pbkdf2_hmac('sha256', clear_password.encode(), salt, rounds)
