from __future__ import annotations
import logging

logger = logging.getLogger(__name__)
import logging
from datetime import timedelta, datetime

import leanit_mweb

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette import status

from typing import TYPE_CHECKING, Annotated, Dict

if TYPE_CHECKING:
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

def get_password_hash(password):
    return leanit_mweb.pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return leanit_mweb.pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    """
    Authenticate user, return user if authenticated, False otherwise
    :param username:
    :param password:
    :return:
    """
    users = leanit_mweb.auth_user_model.filter(name=username)
    if not users:
        print("No user found")
        return False
    user = users[0]
    if not user:
        return False
    if not leanit_mweb.pwd_context.verify(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, leanit_mweb.secret_key, algorithm=leanit_mweb.algorithm)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(leanit_mweb.oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, leanit_mweb.secret_key, algorithms=[leanit_mweb.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = leanit_mweb.auth_user_model.get(id=user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[Dict, Depends(get_current_user)]
) -> Dict[str, str]:
    return current_user.to_dict()
