"""
sources/remoteok.py — RemoteOK (API JSON pública, sin API key).

Fuente vertical tech: se usa solo cuando el CV es de área IT.
Docs no oficiales pero estables desde hace años: GET https://remoteok.com/api
Devuelve un array JSON; el primer elemento es un aviso legal (no es una oferta),
el resto son ofertas.

NOTA: si el formato de respuesta cambia, este adaptador debería fallar
"silencioso" (devuelve []) y loguear el error — nunca tumba el pipeline.
"""

from __future__ import annotations

import requests

from .base import JobSource, normalize_job

API_URL = "https://remoteok.com/api"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


class RemoteOKSource(JobSource):
    name = "remoteok"
    is_tech_vertical = True

    def search(self, query: str, max_results: int = 25) -> list[dict]:
        try:
            resp = requests.get(API_URL, headers=HEADERS, params={"tags": query}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"    [remoteok] ERROR: {e}")
            return []

        jobs = []
        query_lower = query.lower()
        for item in data:
            # El primer elemento del array es metadata, no una oferta.
            if not isinstance(item, dict) or "position" not in item:
                continue

            title = item.get("position", "")
            tags = " ".join(item.get("tags", []) or [])
            description = item.get("description", "") or ""

            # RemoteOK no siempre filtra bien por "tags" en la query string,
            # así que reforzamos el filtro acá comparando contra título/tags.
            haystack = f"{title} {tags}".lower()
            if query_lower and query_lower not in haystack:
                continue

            jobs.append(
                normalize_job(
                    source=self.name,
                    title=title,
                    company=item.get("company", ""),
                    location=item.get("location", "") or "Remoto",
                    modality="remoto",
                    description=description,
                    url=item.get("url") or item.get("apply_url", ""),
                    posted_at=item.get("date", ""),
                )
            )
            if len(jobs) >= max_results:
                break

        print(f"    [remoteok] '{query}' → {len(jobs)} ofertas")
        return jobs
