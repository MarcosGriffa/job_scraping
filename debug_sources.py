"""
debug_sources.py — Script de diagnóstico, un solo uso.

Corré esto y pegame TODO lo que imprime en consola. Con eso arreglo los
selectores de Multitrabajos/Konzerta y el endpoint de Himalayas sin
necesitar acceso a tu compu.

Uso:
    python debug_sources.py
"""

import requests
from bs4 import BeautifulSoup
from collections import Counter

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9",
}


def diagnose_html(name: str, url: str):
    print(f"\n{'=' * 60}\n{name} -> {url}\n{'=' * 60}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"URL final (tras redirects): {resp.url}")
    except Exception as e:
        print(f"ERROR de conexion: {e}")
        return

    if resp.status_code != 200:
        print(f"Primeros 500 caracteres del body:\n{resp.text[:500]}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    print(f"<title>: {soup.title.string if soup.title else '(sin title)'}")

    articles = soup.select("article")
    print(f"Cantidad de <article>: {len(articles)}")

    class_counter = Counter()
    for tag in soup.select("div[class], li[class], article[class]"):
        classes = tag.get("class", [])
        for c in classes:
            class_counter[c] += 1

    print("\nTop 15 clases mas repetidas (candidatas a ser la tarjeta de oferta):")
    for cls, count in class_counter.most_common(15):
        print(f"  {count:4d}x  class=\"{cls}\"")

    if articles:
        print(f"\nClases del primer <article>: {articles[0].get('class')}")
        print(f"Primer <article> (recortado a 800 chars):\n{str(articles[0])[:800]}")


def diagnose_json(name: str, urls: list):
    print(f"\n{'=' * 60}\n{name} - probando endpoints candidatos\n{'=' * 60}")
    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            print(f"\n{url}\n  Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"  Primeros 400 chars: {resp.text[:400]}")
        except Exception as e:
            print(f"\n{url}\n  ERROR: {e}")


if __name__ == "__main__":
    diagnose_html("MULTITRABAJOS", "https://www.multitrabajos.com/empleos-busqueda-analista-de-datos.html")
    diagnose_html("KONZERTA", "https://www.konzerta.com/empleos/busqueda?q=analista+de+datos")

    diagnose_json("HIMALAYAS", [
        "https://himalayas.app/api/jobs",
        "https://himalayas.app/jobs/api",
        "https://himalayas.app/api/v1/jobs",
        "https://himalayas.app/api/jobs?limit=5",
    ])

    print("\n\n>>> Copia TODO lo de arriba y pegamelo <<<")
