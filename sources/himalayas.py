"""
sources/himalayas.py — Himalayas (API JSON pública, sin key).

Fuente vertical tech. El endpoint público NO soporta búsqueda por texto
libre server-side (los parámetros "search"/"q"/"category" se ignoran y
siempre devuelve los avisos más recientes) ni un "limit" mayor a 20 por
página — así que paginamos con "offset" para juntar un lote razonable de
avisos recientes y filtramos localmente por la query, igual que ya hacía
esta fuente antes.
"""

from __future__ import annotations

from datetime import datetime, timezone

import requests

from .base import JobSource, normalize_job

API_URL = "https://himalayas.app/jobs/api"  # el endpoint viejo (/api/jobs) da 404 desde ago/2026
PAGE_SIZE = 20  # la API ignora valores de "limit" mayores a este
PAGES_TO_FETCH = 10  # junta hasta 200 avisos recientes antes de filtrar

_cache: list[dict] | None = None  # el pipeline llama a search() una vez por query del mismo CV


def _fetch_recent_jobs() -> list[dict]:
    """Trae los avisos más recientes paginando con offset (ver nota arriba
    sobre por qué no se puede pedir por palabra clave directamente).
    Cachea el resultado para no repetir las 10 páginas por cada query."""
    global _cache
    if _cache is not None:
        return _cache

    all_jobs = []
    for page in range(PAGES_TO_FETCH):
        try:
            resp = requests.get(
                API_URL, params={"limit": PAGE_SIZE, "offset": page * PAGE_SIZE}, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"    [himalayas] ERROR p{page}: {e}")
            break

        raw_jobs = data.get("jobs", data) if isinstance(data, dict) else data
        if not isinstance(raw_jobs, list) or not raw_jobs:
            break
        all_jobs.extend(raw_jobs)

    _cache = all_jobs
    return all_jobs


class HimalayasSource(JobSource):
    name = "himalayas"
    is_tech_vertical = True

    def search(self, query: str, max_results: int = 25) -> list[dict]:
        raw_jobs = _fetch_recent_jobs()
        if not raw_jobs:
            return []

        query_lower = query.lower()
        jobs = []
        for item in raw_jobs:
            title = item.get("title", "")
            description = item.get("description", "") or item.get("excerpt", "")
            haystack = f"{title} {description}".lower()
            if query_lower and query_lower not in haystack:
                continue

            # Bug de datos del lado de Himalayas (confirmado 10/08/2026, ~50%
            # de los avisos): "companyName" a veces viene literalmente con el
            # placeholder "name" en vez del nombre real. En esos casos usamos
            # "companySlug" (ej. "blend360" → "Blend360") como mejor esfuerzo.
            company = item.get("companyName") or ""
            if not company or company.strip().lower() == "name":
                slug = item.get("companySlug") or ""
                company = slug.replace("-", " ").title()

            # pubDate viene como epoch (segundos), no como texto — lo convertimos
            pub_date = item.get("pubDate")
            posted_at = ""
            if isinstance(pub_date, (int, float)):
                posted_at = datetime.fromtimestamp(pub_date, tz=timezone.utc).strftime("%Y-%m-%d")
            elif isinstance(pub_date, str):
                posted_at = pub_date

            jobs.append(
                normalize_job(
                    source=self.name,
                    title=title,
                    company=company,
                    location="Remoto",
                    modality="remoto",
                    description=description,
                    url=item.get("applicationLink", "") or item.get("guid", ""),
                    posted_at=posted_at,
                )
            )
            if len(jobs) >= max_results:
                break

        print(f"    [himalayas] '{query}' → {len(jobs)} ofertas")
        return jobs
