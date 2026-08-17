"""
sources/konzerta.py — Konzerta (HTML scraping, portal general LatAm/Argentina).

Mismo caveat que multitrabajos.py: selectores no verificados en vivo,
listos para ajustar en la primera corrida real usando los prints de
diagnóstico. Konzerta apunta más a perfiles semi-senior/senior — el
pipeline igual filtra por seniority más adelante, así que no hace falta
descartar nada acá.
"""

from __future__ import annotations

import time
import random
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from .base import JobSource, normalize_job

BASE_URL = "https://www.konzerta.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9",
}


def _txt(el) -> str:
    return el.get_text(strip=True) if el else ""


class KonzertaSource(JobSource):
    name = "konzerta"
    is_tech_vertical = False

    def search(self, query: str, max_results: int = 25) -> list[dict]:
        url = f"{BASE_URL}/empleos/busqueda?q={quote(query)}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"    [konzerta] ERROR: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        # AJUSTAR: selector estimado.
        cards = soup.select("article") or soup.select("div[class*=job-card]")

        if not cards:
            print(f"    [konzerta] [WARN] 0 tarjetas para '{query}' — revisar selector")
            return []

        jobs = []
        for card in cards[:max_results]:
            title_el = card.select_one("h2 a") or card.select_one("h3 a") or card.select_one("a")
            if not title_el:
                continue
            title = _txt(title_el)
            href = title_el.get("href", "")
            job_url = href if href.startswith("http") else BASE_URL + href

            company = _txt(card.select_one("[class*=company]"))
            location = _txt(card.select_one("[class*=location]"))
            description = _txt(card.select_one("p"))

            jobs.append(
                normalize_job(
                    source=self.name,
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    url=job_url,
                )
            )

        print(f"    [konzerta] '{query}' → {len(jobs)} ofertas")
        time.sleep(random.uniform(1.5, 3.0))
        return jobs
