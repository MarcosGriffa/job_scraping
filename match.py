"""
match.py — Job Matcher basado en keywords (sin llamadas a IA)

enrich.py ya extrajo ai_stack y ai_seniority por oferta.
Este script compara ese stack contra el perfil de Marcos y devuelve el top 10.
Corre en < 5 segundos para cualquier cantidad de ofertas.
"""

import pandas as pd
import fitz
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CV_PATH     = Path("CV_Marcos_Griffa_v2.pdf")
DATA_FILE   = Path("data/computrabajo_enriched.csv")
OUTPUT_FILE = Path("data/top_matches.csv")
TOP_N       = 10

# ── Perfil de Marcos ────────────────────────────────────────────
MARCOS_STACK = {
    "python", "sql", "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "scikit", "sklearn", "machine learning", "ml",
    "n8n", "automatización", "automation", "zapier", "make",
    "git", "github",
    "excel", "power bi", "tableau", "looker",
    "jupyter", "colab",
    "ia", "ai", "llm", "groq", "openai", "langchain", "inteligencia artificial",
    "data", "datos", "analytics", "análisis", "business intelligence", "bi",
    "etl", "pipeline", "data warehouse",
    "api", "rest", "json", "scraping", "web scraping",
    "sqlite", "postgresql", "mysql", "mongodb",
    "fastapi", "flask",
    "ciencia de datos", "data science",
}

IT_KEYWORDS = {
    "developer", "desarrollador", "programador", "software", "data", "datos",
    "analista", "analytics", "python", "sql", "machine learning", "ia", "ai",
    "automatización", "devops", "qa", "testing", "rpa", "etl",
    "bi", "business intelligence", "ciencia de datos", "soporte técnico",
    "infraestructura", "sistemas", "it ", "tech",
}

SENIOR_KEYWORDS = {
    "senior", " sr ", "sr.", "ssr", "semi senior", "semisenior",
    "lead", "líder", "lider", "manager", "architect", "principal",
    "director", "jefe", "gerente", "head of",
}

JR_KEYWORDS = {
    "junior", " jr", "jr.", "trainee", "pasante", "practicante",
    "entry", "sin experiencia", "estudiante", "primera experiencia",
}

NO_IT_WORDS = [
    "civil", "mecánico", "mecanico", "electromecánico", "electrico",
    "soldador", "tornero", "operario", "costurera", "enfermera",
    "médico", "medico", "contador", "abogado", "arquitecto",
    "chef", "cocinero", "mozo", "repositor", "cajero", "vendedor",
    "chofer", "conductor", "seguridad", "limpieza",
]


# ── Helpers ─────────────────────────────────────────────────────
def extract_cv_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()


def pre_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Descarta ofertas claramente fuera de scope sin IA."""
    mask = pd.Series([True] * len(df), index=df.index)
    for idx, row in df.iterrows():
        title = str(row.get("title", "")).lower()
        if any(kw in title for kw in NO_IT_WORDS):
            mask[idx] = False
            continue
        if any(kw in title for kw in SENIOR_KEYWORDS):
            mask[idx] = False
    filtered = df[mask].copy()
    print(f"Pre-filtro: {len(df)} → {len(filtered)} avisos relevantes")
    return filtered


def score_job(row: dict) -> dict | None:
    """
    Scoring por keyword matching contra el perfil de Marcos.
    Devuelve None si el aviso no es IT o es senior.
    """
    title     = str(row.get("title", "")).lower()
    stack     = str(row.get("ai_stack", "")).lower()
    seniority = str(row.get("ai_seniority", "")).lower()
    modality  = str(row.get("modality", "")).lower()
    category  = str(row.get("category", "")).lower()

    # Descarte senior
    if any(kw in title or kw in seniority for kw in SENIOR_KEYWORDS):
        return None

    # Descarte no-IT
    combined = f"{title} {stack} {category}"
    if not any(kw in combined for kw in IT_KEYWORDS):
        return None

    # Tokenizar stack de la oferta
    stack_tokens = {
        t.strip()
        for t in stack.replace(",", " ").replace("/", " ").replace("|", " ").split()
        if len(t.strip()) > 1
    }

    # Calcular skills que matchean
    matched = [
        skill for skill in MARCOS_STACK
        if skill in stack or any(skill in tok or tok in skill for tok in stack_tokens)
    ]

    # Score base: 45-90 según overlap, 40 si es IT pero sin stack definido
    base = 45 + min(len(matched) * 8, 45) if matched else 40

    # Bonuses
    if any(kw in title or kw in seniority for kw in JR_KEYWORDS):
        base = min(base + 5, 100)
    if any(w in modality for w in ("remoto", "remote", "home", "híbrido", "hibrido")):
        base = min(base + 3, 100)
    if "python" in stack:
        base = min(base + 5, 100)
    if any(w in title for w in ("data", "datos", "analista", "analytics")):
        base = min(base + 3, 100)

    # Gap: items del stack de la oferta que Marcos no tiene
    stack_items = [s.strip() for s in stack.split(",") if s.strip()]
    gaps = [s for s in stack_items if not any(m in s.lower() for m in MARCOS_STACK)][:3]

    razon = f"Match en: {', '.join(matched[:3])}" if matched else "Rol IT sin stack específico definido"

    return {
        "score":        base,
        "es_it":        True,
        "match_skills": matched[:5],
        "gap_skills":   gaps,
        "razon":        razon,
    }


# ── Main ────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  JOB MATCHER — Observatorio IT Junior")
    print("=" * 55)

    cv_text = extract_cv_text(CV_PATH)
    print(f"CV leído: {len(cv_text)} caracteres")

    df = pd.read_csv(DATA_FILE, encoding="utf-8")
    print(f"Avisos cargados: {len(df)}\n")

    df_filtered = pre_filter(df)

    print(f"\nCalculando scores para {len(df_filtered)} avisos...")

    results = []
    discarded = 0

    for i, (_, row) in enumerate(df_filtered.iterrows(), 1):
        title  = str(row.get("title", ""))[:45]
        result = score_job(row.to_dict())

        if result is None:
            discarded += 1
            print(f"  [{i}/{len(df_filtered)}] {title}... ✗")
            continue

        score = result["score"]
        print(f"  [{i}/{len(df_filtered)}] {title}... ✓ {score}/100")

        results.append({
            "score":        score,
            "title":        row.get("title", ""),
            "company":      row.get("company", ""),
            "city":         row.get("city", ""),
            "province":     row.get("province", ""),
            "modality":     row.get("modality", ""),
            "ai_stack":     row.get("ai_stack", ""),
            "match_skills": ", ".join(result["match_skills"]),
            "gap_skills":   ", ".join(result["gap_skills"]),
            "razon":        result["razon"],
            "url":          row.get("url", ""),
        })

    print(f"\nDescartados: {discarded} | Relevantes: {len(results)}")

    if not results:
        print("[!] No se encontraron matches relevantes")
        return

    results_df = pd.DataFrame(results).sort_values("score", ascending=False)
    # Eliminar duplicados: mismo título + empresa = mismo aviso scrapeado varias veces
    results_df = results_df.drop_duplicates(subset=["title", "company"], keep="first")
    top10 = results_df.head(TOP_N)
    top10.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"\n{'=' * 55}")
    print(f"TOP {TOP_N} MATCHES")
    print(f"{'=' * 55}")
    for _, r in top10.iterrows():
        print(f"\n  Score {r['score']}/100 — {r['title']}")
        print(f"  {r['company']} | {r['city']} | {r['modality']}")
        print(f"  Match: {r['match_skills']}")

    print(f"\n✓ Guardado en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
