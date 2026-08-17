"""
storage_backends/supabase_backend.py — Backend de persistencia real, con
Supabase (Postgres detrás de una API REST).

Se usa automáticamente en cuanto SUPABASE_URL y SUPABASE_SECRET_KEY están
en el .env (ver storage.py, que elige el backend). Las tablas las tiene
que crear una vez Marcos, pegando supabase/schema.sql en el SQL Editor del
dashboard de Supabase — este módulo asume que ya existen.

Usa SUPABASE_SECRET_KEY (no la publishable) porque corre 100% server-side:
esa key tiene permiso total y salta Row Level Security, así que NUNCA debe
llegar al navegador — no se manda al frontend en ninguna respuesta ni se
loguea. Ver .env.example.

Implementa las mismas 6 funciones que storage_backends/json_backend.py
(mismos nombres, misma firma, mismo comportamiento) — storage.py importa
una u otra sin que el resto del código note la diferencia.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from supabase import Client, create_client

DEFAULT_USER_ID = "default"

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SECRET_KEY")
        if not url or not key:
            raise RuntimeError(
                "Falta SUPABASE_URL y/o SUPABASE_SECRET_KEY en el .env — "
                "ver .env.example."
            )
        _client = create_client(url, key)
    return _client


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Interfaz pública (igual a json_backend.py) ───────────────────

def save_cv_profile(user_id: str, filename: str, cv_text: str, profile: dict) -> str:
    user_id = user_id or DEFAULT_USER_ID
    resp = (
        _get_client()
        .table("cv_profiles")
        .insert({"user_id": user_id, "filename": filename, "cv_text": cv_text, "profile": profile})
        .execute()
    )
    return resp.data[0]["id"]


def get_cv_profile(user_id: str, cv_id: str | None = None) -> dict | None:
    user_id = user_id or DEFAULT_USER_ID
    query = _get_client().table("cv_profiles").select("*")
    if cv_id:
        query = query.eq("id", cv_id)
    else:
        query = query.eq("user_id", user_id).order("created_at", desc=True).limit(1)

    rows = query.execute().data
    if not rows:
        return None
    row = rows[0]
    return {**row, "cv_id": row["id"]}


def save_match_results(user_id: str, cv_id: str, results: list[dict], profile: dict | None = None) -> str:
    user_id = user_id or DEFAULT_USER_ID
    resp = (
        _get_client()
        .table("match_results")
        .insert({"user_id": user_id, "cv_id": cv_id, "profile": profile, "results": results})
        .execute()
    )
    return resp.data[0]["id"]


def count_recent_runs(user_id: str, hours: int = 24) -> int:
    """Cuántas búsquedas COMPLETAS hizo esta persona en las últimas `hours`.

    Se cuenta sobre match_results (que ya existe) en vez de una tabla nueva:
    así el límite sobrevive a los reinicios del servidor, que en los
    hostings gratuitos borran el disco. Ver api/rate_limit.py."""
    user_id = user_id or DEFAULT_USER_ID
    desde = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = (
        _get_client()
        .table("match_results")
        .select("id")
        .eq("user_id", user_id)
        .gte("created_at", desde)
        .execute()
        .data
    )
    return len(rows)


def get_match_results(user_id: str, match_id: str | None = None) -> dict | None:
    """Igual que en json_backend.py: si no se pasa match_id, trae la corrida
    más reciente y le actualiza el flag "applied" a cada oferta con el
    estado ACTUAL (por si se marcó como aplicada después de esa corrida)."""
    user_id = user_id or DEFAULT_USER_ID
    query = _get_client().table("match_results").select("*")
    if match_id:
        query = query.eq("id", match_id)
    else:
        query = query.eq("user_id", user_id).order("created_at", desc=True).limit(1)

    rows = query.execute().data
    if not rows:
        return None
    entry = rows[0]
    entry = {**entry, "match_id": entry["id"]}

    applied_ids = get_applied_job_ids(user_id)
    for job in entry["results"]:
        job["applied"] = job.get("job_id") in applied_ids

    return entry


def mark_as_applied(user_id: str, job_id: str, applied: bool = True) -> None:
    user_id = user_id or DEFAULT_USER_ID
    _get_client().table("applied_jobs").upsert(
        {"user_id": user_id, "job_id": job_id, "applied": applied, "applied_at": _now()},
        on_conflict="user_id,job_id",
    ).execute()


def get_applied_job_ids(user_id: str) -> set[str]:
    user_id = user_id or DEFAULT_USER_ID
    rows = (
        _get_client()
        .table("applied_jobs")
        .select("job_id")
        .eq("user_id", user_id)
        .eq("applied", True)
        .execute()
        .data
    )
    return {row["job_id"] for row in rows}
