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


def claim_anonymous_data(anon_id: str, real_user_id: str) -> dict:
    """Fase 3 — al crear una cuenta, re-etiqueta lo que ese navegador tenía
    guardado bajo su id anónimo, para que pase a ser del usuario real.

    Se llama UNA sola vez, en el alta de cuenta (nunca en un login), y es
    idempotente a propósito: si se llama de nuevo (doble click, reintento
    de red), la segunda vez no encuentra filas con ese anon_id y no hace
    nada — no hay forma de que "pise" datos por error.

    anon_id="" (sin cookie previa) es válido y no hace nada."""
    if not anon_id or anon_id == real_user_id:
        return {"cv_profiles": 0, "match_results": 0, "applied_jobs": 0}

    c = _get_client()
    resultado = {}
    for tabla in ("cv_profiles", "match_results", "applied_jobs"):
        try:
            r = c.table(tabla).update({"user_id": real_user_id}).eq("user_id", anon_id).execute()
            resultado[tabla] = len(r.data)
        except Exception as e:
            # applied_jobs tiene clave primaria (user_id, job_id): en el caso
            # remoto de que la cuenta real ya tuviera una fila para el mismo
            # job_id, el UPDATE choca contra esa clave. No dejamos que eso
            # tumbe la migración de las otras tablas — se loguea y se sigue.
            print(f"[claim_anonymous_data] no se pudo migrar '{tabla}': {e}")
            resultado[tabla] = 0
    return resultado


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


# ── Avisos por mail (19/08/2026) — ver notificaciones_semanales.py ──

def get_seen_job_ids(user_id: str) -> set[str]:
    """Ofertas que este usuario ya vio, por cualquier vía (búsqueda manual
    o chequeo automático). Se usa para no repetir un aviso por mail."""
    rows = _get_client().table("seen_jobs").select("job_id").eq("user_id", user_id).execute().data
    return {row["job_id"] for row in rows}


def mark_jobs_seen(user_id: str, job_ids: list[str]) -> None:
    """Registra estas ofertas como ya vistas por este usuario. Idempotente:
    si alguna ya estaba (mismo user_id + job_id), no la duplica ni falla."""
    if not job_ids:
        return
    # dict.fromkeys en vez de set(): dedupea preservando el primer orden, y
    # sobre todo evita el error real de Postgres "ON CONFLICT DO UPDATE
    # command cannot affect row a second time" cuando el mismo job_id
    # aparece dos veces en la lista de entrada (pasa de verdad: una oferta
    # puede repetirse entre dos corridas de búsqueda distintas del mismo
    # usuario que se procesan juntas, como en el backfill manual o si
    # alguna vez se llama con resultados de varias corridas a la vez).
    ids_unicos = list(dict.fromkeys(job_ids))
    filas = [{"user_id": user_id, "job_id": jid} for jid in ids_unicos]
    _get_client().table("seen_jobs").upsert(filas, on_conflict="user_id,job_id").execute()


def get_notification_setting(user_id: str) -> bool:
    """Apagado por defecto (opt-in) — si no hay fila todavía, es que nunca
    lo prendió."""
    rows = (
        _get_client()
        .table("user_settings")
        .select("notificaciones_activas")
        .eq("user_id", user_id)
        .execute()
        .data
    )
    return bool(rows[0]["notificaciones_activas"]) if rows else False


def set_notification_setting(user_id: str, enabled: bool) -> None:
    _get_client().table("user_settings").upsert(
        {"user_id": user_id, "notificaciones_activas": enabled, "updated_at": _now()},
        on_conflict="user_id",
    ).execute()


def get_users_with_notifications_enabled() -> list[str]:
    """Para notificaciones_semanales.py: a quién chequear esta semana."""
    rows = (
        _get_client()
        .table("user_settings")
        .select("user_id")
        .eq("notificaciones_activas", True)
        .execute()
        .data
    )
    return [row["user_id"] for row in rows]
