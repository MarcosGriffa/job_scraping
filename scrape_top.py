"""
scrape_top.py — Scrapea la descripción completa de los top matches
para poder validar si realmente matchean antes de generar CVs.
"""

import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path

MATCHES_FILE = Path("data/top_matches.csv")
OUTPUT_FILE  = Path("data/top_matches_full.csv")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_description(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        # Selectores típicos de Computrabajo
        desc = (
            soup.select_one("p.mbB") or
            soup.select_one("div.fs16") or
            soup.select_one("section.box_resume") or
            soup.select_one("div.offer_description")
        )
        if desc:
            return desc.get_text(separator=" ", strip=True)[:2000]

        # Fallback: agarrar todos los párrafos
        paragraphs = soup.find_all("p")
        if paragraphs:
            text = " ".join(p.get_text(strip=True) for p in paragraphs[:5])
            return text[:2000]

        return "Descripción no disponible"
    except Exception as e:
        return f"Error: {e}"


def main():
    df = pd.read_csv(MATCHES_FILE, encoding="utf-8")
    print(f"Scrapeando descripciones de {len(df)} puestos...\n")

    descriptions = []
    for i, row in df.iterrows():
        title = str(row["title"])[:50]
        print(f"[{i+1}/{len(df)}] {title}")
        desc = scrape_description(row["url"])
        descriptions.append(desc)
        print(f"  → {len(desc)} caracteres")
        time.sleep(2)

    df["description"] = descriptions
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n✓ Guardado en {OUTPUT_FILE}")

    # Mostrar cada uno
    print("\n" + "=" * 60)
    print("REVISIÓN DE LOS 10 PUESTOS")
    print("=" * 60)
    for i, row in df.iterrows():
        print(f"\n{'─' * 60}")
        print(f"#{i} — {row['title']}")
        print(f"Empresa: {row['company']}")
        print(f"Ubicación: {row['city']}, {row['province']}")
        print(f"Modalidad: {row['modality']}")
        print(f"Score IA: {row['score']}")
        print(f"\nDescripción:")
        print(descriptions[i][:800])
        print()


if __name__ == "__main__":
    main()