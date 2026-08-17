"""
tailor.py — Genera el CV adaptado a UNA oferta puntual, bajo demanda.

Diferencia clave con correr `python cv_tailor.py` por consola: ese script
vuelve a scrapear todos los portales desde cero para conseguir las ofertas
(lento, minutos). Acá no hace falta: las ofertas y el texto del CV ya están
guardados en Supabase de la corrida de matching. Entonces adaptar una
oferta es solo:

    texto del CV (guardado) + 1 llamada al modelo chico + armar el .docx

o sea unos segundos, no minutos. Por eso alcanza con un botón que genera
en el momento, sin pre-generar los 10 CVs que quizás nadie mire.

Caché: el .docx se guarda en disco identificado por CV de origen + oferta
(data/cvs_adaptados/web/<cv_id>/<job_id>.docx). Si la persona vuelve a
apretar el botón, se le devuelve el archivo ya hecho sin gastar IA de
nuevo. Si sube un CV nuevo, cambia el cv_id y por lo tanto se regenera
solo — nunca queda pegado a una versión vieja del CV.
"""

from __future__ import annotations

from pathlib import Path

from cv_tailor import (
    _safe_filename,
    adapt_for_job,
    build_render_data,
    parse_cv,
    render_cv_docx,
)
from sources.computrabajo import fetch_full_description

from . import storage

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cvs_adaptados" / "web"


class TailorError(Exception):
    """Error esperable y explicable al usuario (no un bug)."""


def _find_job(user_id: str, job_id: str) -> tuple[dict, str]:
    """Busca la oferta dentro de la última corrida de matching de esta
    persona. Devuelve (oferta, cv_id)."""
    entry = storage.get_match_results(user_id)
    if not entry:
        raise TailorError(
            "No encontramos tus resultados. Volvé a subir tu CV para generar el ranking."
        )

    for job in entry.get("results", []):
        if job.get("job_id") == job_id:
            return job, entry.get("cv_id", "")

    raise TailorError(
        "Esa oferta ya no está en tus resultados. Actualizá la página y probá de nuevo."
    )


def _download_name(job: dict) -> str:
    """Nombre del archivo que ve el usuario al descargarlo."""
    title = _safe_filename(job.get("title", "")) or "oferta"
    company = _safe_filename(job.get("company", ""))
    name = f"CV_{title}"
    if company:
        name += f"_{company}"
    return f"{name}.docx"


def generate_tailored_cv(user_id: str, job_id: str) -> tuple[Path, str, bool]:
    """Genera (o recupera de caché) el CV adaptado a una oferta.

    Devuelve (ruta_del_archivo, nombre_para_descargar, vino_de_cache).
    """
    job, cv_id = _find_job(user_id, job_id)

    cached_path = CACHE_DIR / cv_id / f"{job_id}.docx"
    if cached_path.exists():
        return cached_path, _download_name(job), True

    cv_entry = storage.get_cv_profile(user_id, cv_id or None)
    if not cv_entry or not cv_entry.get("cv_text"):
        raise TailorError(
            "No encontramos el texto de tu CV guardado. Volvé a subirlo y probá de nuevo."
        )

    cv_text = cv_entry["cv_text"]
    header_lines, sections = parse_cv(cv_text)
    if not sections:
        raise TailorError(
            "No pudimos reconocer las secciones de tu CV (Perfil, Experiencia, etc.), "
            "así que no podemos adaptarlo. Probá con un CV con títulos de sección más claros."
        )

    # Los avisos de Computrabajo vienen sin descripción en el listado; traerla
    # mejora bastante la adaptación. Si falla, seguimos con lo que haya.
    if not job.get("description") and job.get("source") == "computrabajo" and job.get("url"):
        try:
            job = {**job, "description": fetch_full_description(job["url"])}
        except Exception:
            pass

    adapted = adapt_for_job(cv_text, sections, job)
    cv_data = build_render_data(header_lines, sections, adapted)
    render_cv_docx(cv_data, cached_path)  # crea las carpetas solo

    return cached_path, _download_name(job), False
