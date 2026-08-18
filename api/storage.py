"""
storage.py — Punto único de entrada a la persistencia.

Elige automáticamente el backend real, según lo que haya en el .env:

  - Si están SUPABASE_URL y SUPABASE_SECRET_KEY -> usa Supabase de verdad
    (storage_backends/supabase_backend.py). Requiere haber corrido
    supabase/schema.sql una vez en el proyecto de Supabase.
  - Si no están -> usa el backend temporal de archivos JSON en data/db/
    (storage_backends/json_backend.py), para poder seguir desarrollando
    sin depender de Supabase.

matching.py y main.py SOLO importan `storage` y llaman a estas funciones —
no les importa (ni deberían enterarse) cuál de los dos backends está activo:

    save_cv_profile(user_id, filename, cv_text, profile) -> cv_id
    get_cv_profile(user_id, cv_id=None)                   -> dict | None
    save_match_results(user_id, cv_id, results, profile)  -> match_id
    count_recent_runs(user_id, hours)                     -> int
    get_match_results(user_id, match_id=None)              -> dict | None
    mark_as_applied(user_id, job_id, applied=True)        -> None
    get_applied_job_ids(user_id)                          -> set[str]
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SECRET_KEY"):
    from .storage_backends.supabase_backend import (  # noqa: F401
        DEFAULT_USER_ID,
        claim_anonymous_data,
        count_recent_runs,
        get_applied_job_ids,
        get_cv_profile,
        get_match_results,
        mark_as_applied,
        save_cv_profile,
        save_match_results,
    )

    BACKEND = "supabase"
else:
    from .storage_backends.json_backend import (  # noqa: F401
        DEFAULT_USER_ID,
        claim_anonymous_data,
        count_recent_runs,
        get_applied_job_ids,
        get_cv_profile,
        get_match_results,
        mark_as_applied,
        save_cv_profile,
        save_match_results,
    )

    BACKEND = "json"

print(f"[storage] backend de persistencia activo: {BACKEND}")
