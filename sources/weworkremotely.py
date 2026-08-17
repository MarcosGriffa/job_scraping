"""
sources/weworkremotely.py — We Work Remotely (RSS oficial, sin key).

WWR publica feeds RSS por categoría. Usamos el feed combinado de todos
los remote jobs y filtramos localmente por la query, porque WWR no
ofrece búsqueda por texto vía RSS.
"""

from __future__ import annotations

import feedparser

from .base import JobSource, normalize_job

RSS_URL = "https://weworkremotely.com/remote-jobs.rss"


class WeWorkRemotelySource(JobSource):
    name = "weworkremotely"
    is_tech_vertical = True

    def search(self, query: str, max_results: int = 25) -> list[dict]:
        try:
            feed = feedparser.parse(RSS_URL)
        except Exception as e:
            print(f"    [weworkremotely] ERROR: {e}")
            return []

        query_lower = query.lower()
        jobs = []
        for entry in feed.entries:
            title = entry.get("title", "")  # suele venir como "Empresa: Puesto"
            summary = entry.get("summary", "")
            haystack = f"{title} {summary}".lower()
            if query_lower and query_lower not in haystack:
                continue

            company, _, role = title.partition(":")
            jobs.append(
                normalize_job(
                    source=self.name,
                    title=role.strip() or title,
                    company=company.strip() if role else "",
                    location="Remoto",
                    modality="remoto",
                    description=summary,
                    url=entry.get("link", ""),
                    posted_at=entry.get("published", ""),
                )
            )
            if len(jobs) >= max_results:
                break

        print(f"    [weworkremotely] '{query}' → {len(jobs)} ofertas")
        return jobs
