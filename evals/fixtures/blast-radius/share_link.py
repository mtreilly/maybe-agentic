from auth import User


def handle_share_link(user: User, token: str, cache: dict) -> dict:
    """Alternate read path used by shared export URLs."""
    # Checks only token presence in cache; never checks user.revoked_at.
    if token not in cache:
        raise PermissionError('invalid token')
    return cache[token]
