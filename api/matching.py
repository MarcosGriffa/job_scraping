"""
matching.py — Orquesta el pipeline existente para la API web.

OJO: esto NO reemplaza ni modifica pipeline.py/cv_profile.py/semantic_match.py
— los importa y los usa tal cual, igual que lo haría alguien corriendo
`python pipeline.py` por consola. Lo único que agrega:

  1. Recibe el CV ya guardado en disco (subido por el usuario vía la web)
     en vez de leerlo de sys.argv.
  2. Le pone un job_id estable a cada oferta encontrada.
  3. Excluye las ofertas que el usuario ya marcó como "aplicado" en una
     corrida anterior, ANTES de gastar la etapa 2 (la que usa el modelo
     grande de Groq) — no tiene sentido volver a explicar un match que la
     persona ya aplicó.
  4. Guarda el resultado con storage.save_match_results en vez del
     json/csv que usa pipeline.py por consola.
"""

from __future__ import annotations

from cv_profile import extract_cv_text, classify_cv
from pipeline import collect_jobs, EMBEDDING_TOP_K, EXPLAIN_TOP_N
from semantic_match import rank_and_explain

from . import storage
from .job_utils import make_job_id


def run_full_pipeline(user_id: str, cv_path: str, filename: str) -> dict:
    """Corre CV → clasificación → búsqueda → matching, de punta a punta,
    y devuelve todo lo que necesita el frontend."""

    cv_text = extract_cv_text(cv_path)
    profile = classify_cv(cv_text)
    cv_id = storage.save_cv_profile(user_id, filename, cv_text, profile)

    jobs = collect_jobs(
        profile["search_queries"], profile.get("search_queries_en", []), profile["is_tech"]
    )

    for job in jobs:
        job["job_id"] = make_job_id(job)

    applied_ids = storage.get_applied_job_ids(user_id)
    jobs = [job for job in jobs if job["job_id"] not in applied_ids]

    if jobs:
        results = rank_and_explain(
            cv_text, jobs, embedding_top_k=EMBEDDING_TOP_K, explain_top_n=EXPLAIN_TOP_N
        )
    else:
        results = []

    for r in results:
        r["applied"] = False  # recién generados, ninguno puede estar aplicado todavía

    match_id = storage.save_match_results(user_id, cv_id, results, profile=profile)

    return {
        "cv_id": cv_id,
        "match_id": match_id,
        "profile": profile,
        "results": results,
    }
