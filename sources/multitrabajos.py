"""
sources/multitrabajos.py — Multitrabajos Argentina (HTML scraping).

Portal general (todos los rubros). No tiene API pública, así que scrapeamos
el HTML de resultados de búsqueda, igual que ya hacías con Computrabajo.

IMPORTANTE: los selectores de abajo son la mejor estimación basada en la
estructura típica de este tipo de portales — NO se probaron contra el sitio
en vivo (mi entorno de desarrollo no tiene salida a internet hacia estos
sitios). En la primera corrida real, revisar los prints de [WARN]/diagnóstico
para ajustar selectores si hace falta — el patrón de diagnóstico es el mismo
que ya usa computrabajo.py.
"""

from __future__ import annotations

import time
import random
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from .base import JobSource, normalize_job

BASE_URL = "https://www.multitrabajos.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9",
}


def _txt(el) -> str:
    return el.get_text(strip=True) if el else ""


class MultitrabajosSource(JobSource):
    name = "multitrabajos"
    is_tech_vertical = False

    def search(self, query: str, max_results: int = 25) -> list[dict]:
        url = f"{BASE_URL}/empleos-busqueda-{quote(query)}.html"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"    [multitrabajos] ERROR: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        # AJUSTAR: selector estimado. Si da 0, revisar con diagnóstico de abajo.
        cards = soup.select("article") or soup.select("div.aviso") or soup.select("li.aviso")

        if not cards:
            print(f"    [multitrabajos] [WARN] 0 tarjetas para '{query}' — revisar selector")
            return []

        jobs = []
        for card in cards[:max_results]:
            title_el = card.select_one("h2 a") or card.select_one("a")
            if not title_el:
                continue
            title = _txt(title_el)
            href = title_el.get("href", "")
            job_url = href if href.startswith("http") else BASE_URL + href

            company = _txt(card.select_one(".empresa") or card.select_one("[class*=company]"))
            location = _txt(card.select_one(".ubicacion") or card.select_one("[class*=location]"))
            description = _txt(card.select_one(".descripcion") or card.select_one("p"))

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

        print(f"    [multitrabajos] '{query}' → {len(jobs)} ofertas")
        time.sleep(random.uniform(1.5, 3.0))
        return jobs
