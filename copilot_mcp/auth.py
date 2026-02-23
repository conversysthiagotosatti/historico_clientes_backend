from __future__ import annotations

from dataclasses import dataclass
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

@dataclass(frozen=True)
class Identity:
    user: User
    raw_token: str

def resolve_identity_from_headers(headers: dict) -> Identity:
    """
    headers: dict com 'authorization' (case-insensitive).
    """
    auth = JWTAuthentication()

    # SimpleJWT espera algo no formato: "Bearer <token>"
    raw = headers.get("authorization") or headers.get("Authorization")
    if not raw:
        raise PermissionError("Authorization header ausente (Bearer token).")

    parts = raw.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise PermissionError("Authorization inválido. Use: Bearer <token>")

    token = parts[1]

    try:
        validated = auth.get_validated_token(token)
        user = auth.get_user(validated)
    except (InvalidToken, TokenError) as e:
        raise PermissionError("Token JWT inválido ou expirado.") from e

    return Identity(user=user, raw_token=token)