"""
sources/jobicy.py — Jobicy (API JSON pública, sin key, documentada en jobicy.com/api).

Fuente vertical tech (aunque Jobicy tiene también categorías no-tech,
la dejamos en la capa tech por ahora ya que su fuerte es remoto/digital).
"""

from __future__ import annotations

import requests

from .base import JobSource, normalize_job

API_URL = "https://jobicy.com/api/v2/remote-jobs"


class JobicySource(JobSource):
    name = "jobicy"
    is_tech_vertical = True

    def search(self, query: str, max_results: int = 25) -> list[dict]:
        try:
            resp = requests.get(
                API_URL,
                params={"count": max_results, "tag": query},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"    [jobicy] ERROR: {e}")
            return []

        raw_jobs = data.get("jobs", []) if isinstance(data, dict) else []
        jobs = []
        for item in raw_jobs:
            jobs.append(
                normalize_job(
                    source=self.name,
                    title=item.get("jobTitle", ""),
                    company=item.get("companyName", ""),
                    location=item.get("jobGeo", "") or "Remoto",
                    modality="remoto",
                    description=item.get("jobExcerpt", "") or item.get("jobDescription", ""),
                    url=item.get("url", ""),
                    posted_at=item.get("pubDate", ""),
                )
            )
            if len(jobs) >= max_results:
                break

        print(f"    [jobicy] '{query}' → {len(jobs)} ofertas")
        return jobs
