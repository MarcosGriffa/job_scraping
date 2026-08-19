"""
storage_backends/json_backend.py — Backend de persistencia temporal, con
archivos JSON locales en data/db/.

Se usa automáticamente cuando NO están configuradas las credenciales de
Supabase en el .env (ver storage.py, que elige el backend). Sirve para
desarrollar sin depender de internet/Supabase, y quedó como red de
contención si algún día hay que correr esto sin base de datos.

Implementa las mismas 5 funciones que storage_backends/supabase_backend.py
(mismos nombres, misma firma, mismo comportamiento) — así storage.py puede
importar cualquiera de los dos sin que el resto del código note la
diferencia:

    save_cv_profile(user_id, filename, cv_text, profile) -> cv_id
    get_cv_profile(user_id, cv_id=None)                   -> dict | None
    save_match_results(user_id, cv_id, results, profile)  -> match_id
    get_match_results(user_id, match_id=None)              -> dict | None
    mark_as_applied(user_id, job_id, applied=True)        -> None
    get_applied_job_ids(user_id)                          -> set[str]

Modelo de datos guardado (simple, tipo "tablas" en JSON):
  data/db/cv_profiles.json   -> { cv_id: {user_id, filename, cv_text, profile, created_at} }
  data/db/match_results.json -> { match_id: {user_id, cv_id, results, created_at} }
  data/db/applied_jobs.json  -> { user_id: { job_id: {applied: bool, applied_at} } }

No hay login todavía, así que user_id por ahora es un id anónimo que genera
el frontend (guardado en localStorage del navegador) — ver web/. Si no
viene ninguno, se usa "default".
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "data" / "db"
CV_PROFILES_FILE = DB_DIR / "cv_profiles.json"
MATCH_RESULTS_FILE = DB_DIR / "match_results.json"
APPLIED_JOBS_FILE = DB_DIR / "applied_jobs.json"
SEEN_JOBS_FILE = DB_DIR / "seen_jobs.json"
USER_SETTINGS_FILE = DB_DIR / "user_settings.json"

DEFAULT_USER_ID = "default"

# Lock simple en memoria para que dos requests no pisen el mismo archivo a
# la vez. Alcanza para el MVP (un solo proceso de FastAPI, poco tráfico).
_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else {}


def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)  # escritura "atómica" — evita dejar el archivo corrupto a medio escribir


# ── Interfaz pública ─────────────────────────────────────────────

def save_cv_profile(user_id: str, filename: str, cv_text: str, profile: dict) -> str:
    """Guarda el perfil clasificado de un CV subido. Devuelve el cv_id nuevo."""
    user_id = user_id or DEFAULT_USER_ID
    with _lock:
        data = _load(CV_PROFILES_FILE)
        cv_id = uuid.uuid4().hex[:12]
        data[cv_id] = {
            "user_id": user_id,
            "filename": filename,
            "cv_text": cv_text,
            "profile": profile,
            "created_at": _now(),
        }
        _save(CV_PROFILES_FILE, data)
    return cv_id


def get_cv_profile(user_id: str, cv_id: str | None = None) -> dict | None:
    """Si no se pasa cv_id, devuelve el CV más reciente de ese usuario."""
    user_id = user_id or DEFAULT_USER_ID
    data = _load(CV_PROFILES_FILE)
    if cv_id:
        entry = data.get(cv_id)
        return {**entry, "cv_id": cv_id} if entry else None

    own = [{**v, "cv_id": k} for k, v in data.items() if v["user_id"] == user_id]
    if not own:
        return None
    return max(own, key=lambda e: e["created_at"])


def save_match_results(user_id: str, cv_id: str, results: list[dict], profile: dict | None = None) -> str:
    """Guarda los resultados de una corrida de matching. Devuelve el match_id nuevo."""
    user_id = user_id or DEFAULT_USER_ID
    with _lock:
        data = _load(MATCH_RESULTS_FILE)
        match_id = uuid.uuid4().hex[:12]
        data[match_id] = {
            "user_id": user_id,
            "cv_id": cv_id,
            "profile": profile,
            "results": results,
            "created_at": _now(),
        }
        _save(MATCH_RESULTS_FILE, data)
    return match_id


def claim_anonymous_data(anon_id: str, real_user_id: str) -> dict:
    """Misma firma/comportamiento que supabase_backend.py — ver ese archivo
    para la explicación completa. Acá simplemente re-escribe el user_id en
    los 3 archivos JSON."""
    if not anon_id or anon_id == real_user_id:
        return {"cv_profiles": 0, "match_results": 0, "applied_jobs": 0}

    resultado = {}
    with _lock:
        data = _load(CV_PROFILES_FILE)
        n = sum(1 for v in data.values() if v.get("user_id") == anon_id)
        for v in data.values():
            if v.get("user_id") == anon_id:
                v["user_id"] = real_user_id
        _save(CV_PROFILES_FILE, data)
        resultado["cv_profiles"] = n

        data = _load(MATCH_RESULTS_FILE)
        n = sum(1 for v in data.values() if v.get("user_id") == anon_id)
        for v in data.values():
            if v.get("user_id") == anon_id:
                v["user_id"] = real_user_id
        _save(MATCH_RESULTS_FILE, data)
        resultado["match_results"] = n

        data = _load(APPLIED_JOBS_FILE)
        anon_entries = data.pop(anon_id, {})
        real_entries = data.setdefault(real_user_id, {})
        for job_id, info in anon_entries.items():
            real_entries.setdefault(job_id, info)  # no pisa si ya existia
        _save(APPLIED_JOBS_FILE, data)
        resultado["applied_jobs"] = len(anon_entries)

    return resultado


def count_recent_runs(user_id: str, hours: int = 24) -> int:
    """Cuántas búsquedas COMPLETAS hizo esta persona en las últimas `hours`.
    Misma firma que en supabase_backend.py — ver api/rate_limit.py."""
    user_id = user_id or DEFAULT_USER_ID
    desde = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    data = _load(MATCH_RESULTS_FILE)
    return sum(
        1
        for v in data.values()
        if v.get("user_id") == user_id and v.get("created_at", "") >= desde
    )


def get_match_results(user_id: str, match_id: str | None = None) -> dict | None:
    """Si no se pasa match_id, devuelve la corrida más reciente de ese usuario,
    con el flag "applied" de cada oferta ya actualizado según get_applied_job_ids
    (por si se marcó como aplicada DESPUÉS de esta corrida — el checkbox tiene
    que reflejar el estado actual, no una foto vieja)."""
    user_id = user_id or DEFAULT_USER_ID
    data = _load(MATCH_RESULTS_FILE)

    if match_id:
        entry = data.get(match_id)
        entry = {**entry, "match_id": match_id} if entry else None
    else:
        own = [{**v, "match_id": k} for k, v in data.items() if v["user_id"] == user_id]
        entry = max(own, key=lambda e: e["created_at"]) if own else None

    if not entry:
        return None

    applied_ids = get_applied_job_ids(user_id)
    for job in entry["results"]:
        job["applied"] = job.get("job_id") in applied_ids

    return entry


def mark_as_applied(user_id: str, job_id: str, applied: bool = True) -> None:
    """Marca (o desmarca, si applied=False) una oferta como aplicada por ese usuario."""
    user_id = user_id or DEFAULT_USER_ID
    with _lock:
        data = _load(APPLIED_JOBS_FILE)
        data.setdefault(user_id, {})
        data[user_id][job_id] = {"applied": applied, "applied_at": _now()}
        _save(APPLIED_JOBS_FILE, data)


def get_applied_job_ids(user_id: str) -> set[str]:
    """IDs de ofertas que este usuario ya marcó como aplicadas."""
    user_id = user_id or DEFAULT_USER_ID
    data = _load(APPLIED_JOBS_FILE)
    user_entries = data.get(user_id, {})
    return {job_id for job_id, info in user_entries.items() if info.get("applied")}


# ── Avisos por mail (19/08/2026) — ver notificaciones_semanales.py ──
# data/db/seen_jobs.json     -> { user_id: { job_id: seen_at } }
# data/db/user_settings.json -> { user_id: {notificaciones_activas, updated_at} }

def get_seen_job_ids(user_id: str) -> set[str]:
    data = _load(SEEN_JOBS_FILE)
    return set(data.get(user_id, {}).keys())


def mark_jobs_seen(user_id: str, job_ids: list[str]) -> None:
    if not job_ids:
        return
    with _lock:
        data = _load(SEEN_JOBS_FILE)
        data.setdefault(user_id, {})
        for jid in job_ids:
            data[user_id].setdefault(jid, _now())  # no pisa la fecha si ya estaba
        _save(SEEN_JOBS_FILE, data)


def get_notification_setting(user_id: str) -> bool:
    data = _load(USER_SETTINGS_FILE)
    return bool(data.get(user_id, {}).get("notificaciones_activas", False))


def set_notification_setting(user_id: str, enabled: bool) -> None:
    with _lock:
        data = _load(USER_SETTINGS_FILE)
        data[user_id] = {"notificaciones_activas": enabled, "updated_at": _now()}
        _save(USER_SETTINGS_FILE, data)


def get_users_with_notifications_enabled() -> list[str]:
    data = _load(USER_SETTINGS_FILE)
    return [uid for uid, v in data.items() if v.get("notificaciones_activas")]
