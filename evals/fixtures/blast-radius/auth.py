from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    user_id: str
    active: bool
    revoked_at: Optional[str] = None


def handle_api_request(user: User, resource: str) -> dict:
    if not user.active or user.revoked_at is not None:
        raise PermissionError('revoked')
    return {'resource': resource, 'owner': user.user_id}
