from datetime import datetime, timedelta
from typing import Optional

import jwt
from django.conf import settings

from .user import ModuleUser


def jwt_to_module_user(token: str) -> Optional[ModuleUser]:
    key = settings.INTERCONNECT_JWT_ENCODE_KEY
    if not key:
        return None

    try:
        payload = jwt.decode(token, key, algorithms="HS256")
        if payload["valid"] < datetime.now().timestamp():
            return None
        return ModuleUser(
            module_name=payload["module"],
        )
    except Exception:  # pylint: disable=broad-except
        return None


def generate_jwt(ttl: Optional[timedelta] = None) -> str:
    key = settings.INTERCONNECT_JWT_ENCODE_KEY
    if not key:
        return None

    ttl = ttl or timedelta(minutes=5)
    valid_until = (datetime.now() + ttl).timestamp()

    return jwt.encode(
        {
            "module": settings.INTERCONNECT_MODULE_NAME,
            "valid": valid_until,
        },
        key,
        algorithm="HS256",
    )
