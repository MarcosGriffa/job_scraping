"""
auth.py — Verifica la sesión real de Supabase Auth (Fase 3).

Hasta ahora, el user_id era un texto que mandaba el navegador (cookie
anónima) y el motor le creía ciegamente — cualquiera podía mandar el
user_id de otra persona y leer/escribir sus datos. Con cuentas reales eso
deja de ser tolerable.

Cómo se arregla: Supabase Auth firma un token (JWT) cuando alguien inicia
sesión. Acá lo verificamos con la llave PÚBLICA del proyecto (JWKS, que
Supabase expone en /auth/v1/.well-known/jwks.json) — no hace falta ningún
secreto nuevo en el .env/Render. Si la firma es válida, el "sub" (subject)
del token ES el user_id real, verificado por Supabase — ya no confiamos en
nada que mande el cliente.

Los endpoints de matching (ver main.py) usan get_verified_user_id() como
dependencia de FastAPI: sin token válido, no hay respuesta — no existe un
"modo anónimo" para matchear, por decisión de producto (Fase 3: cuenta
obligatoria para usar el servicio, la landing sigue libre).
"""

from __future__ import annotations

import os

import jwt
from dotenv import load_dotenv
from fastapi import Header, HTTPException
from jwt import PyJWKClient

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

_jwk_client: PyJWKClient | None = None


def _get_jwk_client() -> PyJWKClient:
    global _jwk_client
    if _jwk_client is None:
        if not SUPABASE_URL:
            raise RuntimeError("Falta SUPABASE_URL en el .env — no se puede verificar sesiones.")
        # cache_keys: evita pedirle a Supabase la llave pública en cada
        # request; solo la re-pide si aparece un "kid" que no tiene cacheado.
        _jwk_client = PyJWKClient(JWKS_URL, cache_keys=True)
    return _jwk_client


def verify_token(token: str) -> str:
    """Valida el JWT y devuelve el user_id (claim "sub"). Tira HTTPException
    401 si el token es inválido, está vencido, o no vino."""
    try:
        signing_key = _get_jwk_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",  # Supabase pone esto en todos los tokens de usuarios logueados
        )
    except Exception as e:
        raise HTTPException(401, f"Sesión inválida o vencida: {e}")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Token sin usuario (claim 'sub' ausente).")
    return user_id


def get_verified_user_id(authorization: str | None = Header(default=None)) -> str:
    """Dependencia de FastAPI: exige "Authorization: Bearer <token>" y
    devuelve el user_id ya verificado. Usarla en cualquier endpoint que
    toque datos de un usuario — nunca confiar en un user_id que mande el
    cliente por otro lado (form, query param, body)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Falta iniciar sesión para usar esta función.")
    token = authorization.removeprefix("Bearer ").strip()
    return verify_token(token)
