"""
Scraper de Computrabajo Argentina — IT Junior
Extrae avisos de múltiples búsquedas y guarda CSV.
"""
import csv
import time
import random
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# ── Configuración ──────────────────────────────────────────────
BASE_URL = "https://ar.computrabajo.com"

SEARCH_PATHS = [
    "/trabajo-de-analista-de-datos-junior",
    "/trabajo-de-desarrollador-junior",
    "/trabajo-de-programador-junior",
    "/trabajo-de-soporte-tecnico-junior",
    "/trabajo-de-qa-junior",
    "/trabajo-de-python-junior",
    "/trabajo-de-sql-junior",
    "/trabajo-de-trainee-it",
    "/trabajo-de-data-analyst-junior",
    "/trabajo-de-automatizacion",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9",
}

MIN_DELAY    = 2.0
MAX_DELAY    = 4.0
MAX_PAGES    = 5
OUTPUT_FILE  = Path("data/computrabajo_raw.csv")


# ── Helpers ────────────────────────────────────────────────────
def wait():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def get_soup(url: str):
    """Descarga una URL y devuelve BeautifulSoup. None si falla."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException as e:
        print(f"    [ERROR] {url} → {e}")
        return None


def txt(el) -> str:
    """Texto limpio de un elemento BS4. '' si es None."""
    return el.get_text(strip=True) if el else ""


# ── Parseo de una tarjeta ──────────────────────────────────────
def parse_card(card, category: str) -> dict | None:
    """
    Extrae los campos de una tarjeta <article>.
    Devuelve None si no puede sacar título + URL.
    """

    # ── Título y URL ──
    # Probamos varios selectores porque Computrabajo a veces varía
    title_el = (
        card.select_one("h2 a") or
        card.select_one("a.js-o-link") or
        card.select_one("a[href*='oferta']")
    )
    if not title_el:
        return None

    title = txt(title_el)
    href  = title_el.get("href", "")
    url   = BASE_URL + href if href.startswith("/") else href

    # ── Empresa ──
    company_el = (
        card.select_one("a.fc_base.t_ellipsis") or
        card.select_one("p.fc_base a") or
        card.select_one("span.fc_base")
    )
    company = txt(company_el)

    # ── Ubicación ──
    location = ""
    for p in card.select("p.fs16.fc_base.mt5"):
        if "dFlex" not in p.get("class", []):
            span = p.select_one("span.mr10")
            location = txt(span) if span else txt(p)
            break

# ── Fecha ── (selector corregido)
    date_el = card.select_one("p.fs13.fc_aux.mt15")
    date = txt(date_el)

    # ── Modalidad (Remoto / Híbrido / Presencial) ──
    modality = ""
    for tag in card.select("span, p"):
        t = txt(tag).lower()
        if t in ("remoto", "híbrido", "hibrido", "presencial"):
            modality = t
            break

    # ── Salario (aparece pocas veces) ──
    salary = ""
    for el in card.select("span, p"):
        t = txt(el)
        if "$" in t and "mensual" in t.lower():
            salary = t
            break

    return {
        "category":      category,
        "title":         title,
        "company":       company,
        "location":      location,
        "modality":      modality,
        "salary":        salary,
        "date_posted":   date,
        "url":           url,
        "scraped_at":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


# ── Scraping de una página de resultados ──────────────────────
def scrape_page(path: str, page: int) -> list[dict]:
    url = BASE_URL + path if page == 1 else f"{BASE_URL}{path}?p={page}"
    print(f"    p{page} → {url}")

    soup = get_soup(url)
    if not soup:
        return []

    # Selector principal que vimos en tus DevTools: article.box_offer
    cards = soup.select("article.box_offer")

    # ── Debug: si no encuentra nada, mostramos info para arreglar ──
    if not cards:
        print(f"    [WARN] 0 tarjetas con 'article.box_offer'")
        # Contamos articles en general para diagnosticar
        all_articles = soup.select("article")
        print(f"           <article> en la página: {len(all_articles)}")
        if all_articles:
            # Mostramos las clases del primer article para ajustar
            print(f"           Clases del 1er article: {all_articles[0].get('class')}")
        return []

    category = path.replace("/trabajo-de-", "").replace("-", " ").strip()
    results  = []

    for card in cards:
        job = parse_card(card, category)
        if job:
            results.append(job)

    print(f"           ✓ {len(results)} avisos")
    return results


# ── Loop principal ─────────────────────────────────────────────
def scrape_all() -> list[dict]:
    all_jobs = []

    for i, path in enumerate(SEARCH_PATHS, 1):
        print(f"\n[{i}/{len(SEARCH_PATHS)}] {path}")

        for page in range(1, MAX_PAGES + 1):
            jobs = scrape_page(path, page)

            if not jobs:
                break  # Sin resultados → no hay más páginas

            all_jobs.extend(jobs)
            wait()

    return all_jobs


# ── Deduplicación ─────────────────────────────────────────────
def deduplicate(jobs: list[dict]) -> list[dict]:
    """Un mismo aviso puede aparecer en varias búsquedas. Lo limpiamos por URL."""
    seen, unique = set(), []
    for job in jobs:
        url = job["url"]
        if url not in seen:
            seen.add(url)
            unique.append(job)
    return unique


# ── Guardar CSV ───────────────────────────────────────────────
def save_csv(jobs: list[dict]):
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
        writer.writeheader()
        writer.writerows(jobs)
    print(f"\n✓ Guardado: {OUTPUT_FILE.resolve()}")
    print(f"  Filas totales: {len(jobs)}")


# ── Entry point ───────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  SCRAPER COMPUTRABAJO — IT JUNIOR ARGENTINA")
    print("=" * 55)

    jobs        = scrape_all()
    unique_jobs = deduplicate(jobs)

    print(f"\nTotal scrapeados:  {len(jobs)}")
    print(f"Únicos (sin dupl): {len(unique_jobs)}")

    if unique_jobs:
        save_csv(unique_jobs)
    else:
        print("\n[!] No se scrapeó nada. Revisá los WARN de arriba.")


if __name__ == "__main__":
    main()