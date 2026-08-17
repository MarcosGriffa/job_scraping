"""
Paso A: Limpieza del CSV crudo de Computrabajo.

Qué hace:
- Elimina filas sin título o sin URL
- Normaliza fechas ("Hace 3 días" → fecha real)
- Normaliza ubicación (extrae provincia y zona)
- Normaliza modalidad (remoto/híbrido/presencial/no especificado)
- Elimina duplicados por URL
- Filtra avisos claramente fuera de scope (ventas, atención al cliente puro, etc.)
- Guarda data/computrabajo_clean.csv
"""

import re
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


# ── Paths ──────────────────────────────────────────────────────
INPUT_FILE  = Path("data/computrabajo_raw.csv")
OUTPUT_FILE = Path("data/computrabajo_clean.csv")


# ── Normalización de fechas ────────────────────────────────────
def parse_date(date_str: str) -> str:
    """
    Convierte textos relativos a fechas reales.
    "Hace 3 días"   → "2026-05-11"
    "Hace 1 semana" → "2026-05-07"
    "Hace 2 meses"  → "2026-03-14"
    Hoy como base.
    """
    if not date_str or not isinstance(date_str, str):
        return ""

    today = datetime.today()
    s = date_str.lower().strip()

    try:
        # "Hace X días"
        m = re.search(r"hace\s+(\d+)\s+d[ií]a", s)
        if m:
            return (today - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d")

        # "Hace 1 semana" o "Hace X semanas"
        m = re.search(r"hace\s+(\d+)\s+semana", s)
        if m:
            return (today - timedelta(weeks=int(m.group(1)))).strftime("%Y-%m-%d")

        # "Hace 1 mes" o "Hace X meses"
        m = re.search(r"hace\s+(\d+)\s+mes", s)
        if m:
            days = int(m.group(1)) * 30
            return (today - timedelta(days=days)).strftime("%Y-%m-%d")

        # "Hoy"
        if "hoy" in s:
            return today.strftime("%Y-%m-%d")

        # "Ayer"
        if "ayer" in s:
            return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    except Exception:
        pass

    return ""  # No pudimos parsear


# ── Normalización de ubicación ─────────────────────────────────

# Mapa de ciudades/zonas conocidas → provincia
LOCATION_MAP = {
    # CABA y GBA
    "capital federal": "Buenos Aires", "caba": "Buenos Aires",
    "buenos aires":    "Buenos Aires", "palermo":  "Buenos Aires",
    "recoleta":        "Buenos Aires", "microcentro": "Buenos Aires",
    "belgrano":        "Buenos Aires", "barracas": "Buenos Aires",
    "san isidro":      "Buenos Aires", "vicente lópez": "Buenos Aires",
    "quilmes":         "Buenos Aires", "lomas de zamora": "Buenos Aires",
    "lanús":           "Buenos Aires", "morón": "Buenos Aires",
    "hurlingham":      "Buenos Aires", "tigre": "Buenos Aires",
    "pilar":           "Buenos Aires", "la plata": "Buenos Aires",
    # Otras provincias
    "córdoba":   "Córdoba",   "rosario":  "Santa Fe",
    "santa fe":  "Santa Fe",  "mendoza":  "Mendoza",
    "tucumán":   "Tucumán",   "salta":    "Salta",
    "neuquén":   "Neuquén",   "mar del plata": "Buenos Aires",
    "bahía blanca": "Buenos Aires",
}

def parse_location(loc_str: str) -> tuple[str, str]:
    """
    Devuelve (ciudad_limpia, provincia).
    Ej: "Recoleta, Capital Federal" → ("Recoleta", "Buenos Aires")
    """
    if not loc_str or not isinstance(loc_str, str):
        return ("", "")

    parts = [p.strip() for p in loc_str.split(",")]
    city     = parts[0] if parts else ""
    province = ""

    # Buscar en el mapa usando lowercase
    for part in parts:
        key = part.lower().strip()
        if key in LOCATION_MAP:
            province = LOCATION_MAP[key]
            break

    # Si no encontramos provincia pero hay "remoto" → marcarlo
    if not province and "remoto" in loc_str.lower():
        province = "Remoto"

    return (city, province)


# ── Normalización de modalidad ─────────────────────────────────
def parse_modality(modality_str: str, title: str, location: str) -> str:
    """Normaliza a: Remoto / Híbrido / Presencial / No especificado"""
    combined = f"{modality_str} {title} {location}".lower()

    if any(w in combined for w in ["remoto", "remote", "teletrabajo", "home office"]):
        return "Remoto"
    if any(w in combined for w in ["híbrido", "hibrido", "hybrid"]):
        return "Híbrido"
    if any(w in combined for w in ["presencial", "oficina"]):
        return "Presencial"
    return "No especificado"


# ── Filtro de avisos fuera de scope ───────────────────────────
# Palabras en el TÍTULO que indican que NO es un rol IT Jr. real
OUT_OF_SCOPE_TITLE = [
    "vendedor", "ventas", "cajero", "administrativa",
    "administrativo", "recepcionista", "limpieza", "seguridad",
    "conductor", "chofer", "almacén", "depósito", "repositor",
    "promotor", "cobrador", "teléfono", "telemarketing",
]

def is_out_of_scope(title: str) -> bool:
    t = title.lower()
    return any(word in t for word in OUT_OF_SCOPE_TITLE)


# ── Detección básica de stack técnico ─────────────────────────
# Después la IA va a hacer esto mejor, pero ya sacamos algo útil
TECH_KEYWORDS = {
    "Python": ["python"],
    "SQL": ["sql", "mysql", "postgresql", "sqlite", "oracle"],
    "Excel": ["excel"],
    "Power BI": ["power bi", "powerbi"],
    "R": [r"\br\b", "r studio", "rstudio"],
    "Tableau": ["tableau"],
    "JavaScript": ["javascript", "js"],
    "Java": [r"\bjava\b"],
    "Machine Learning": ["machine learning", "ml", "scikit", "sklearn"],
    "n8n": ["n8n"],
    "AWS": ["aws", "amazon web services"],
    "Git": ["git", "github", "gitlab"],
    "Docker": ["docker"],
    "Spark": ["spark", "pyspark"],
    "Pandas": ["pandas"],
    "NoSQL": ["mongodb", "nosql", "cassandra", "redis"],
}

def extract_stack(title: str, category: str) -> str:
    """
    Extrae tecnologías mencionadas en título + categoría.
    Devuelve string separado por comas: "Python, SQL, Excel"
    Nota: esto es básico. La IA lo mejora mucho en el Paso B.
    """
    text = f"{title} {category}".lower()
    found = []
    for tech, patterns in TECH_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                found.append(tech)
                break
    return ", ".join(found)


# ── Pipeline principal ─────────────────────────────────────────
def main():
    print("=" * 50)
    print("  LIMPIEZA DE DATOS — COMPUTRABAJO")
    print("=" * 50)

    # Cargar CSV
    if not INPUT_FILE.exists():
        print(f"[ERROR] No existe {INPUT_FILE}")
        print("        Corré primero computrabajo.py")
        return

    df = pd.read_csv(INPUT_FILE, encoding="utf-8")
    print(f"\nFilas cargadas: {len(df)}")
    print(f"Columnas: {list(df.columns)}")

    # ── 1. Eliminar filas sin título o sin URL ──
    before = len(df)
    df = df.dropna(subset=["title", "url"])
    df = df[df["title"].str.strip() != ""]
    df = df[df["url"].str.strip() != ""]
    print(f"\n[1] Sin título/URL eliminados: {before - len(df)} filas")

    # ── 2. Eliminar duplicados por URL ──
    before = len(df)
    df = df.drop_duplicates(subset=["url"])
    print(f"[2] Duplicados eliminados: {before - len(df)} filas")

    # ── 3. Filtrar fuera de scope ──
    before = len(df)
    df = df[~df["title"].apply(is_out_of_scope)]
    print(f"[3] Fuera de scope eliminados: {before - len(df)} filas")

    # ── 4. Normalizar fechas ──
    df["date_clean"] = df["date_posted"].apply(parse_date)
    dates_ok = df["date_clean"].str.strip().ne("").sum()
    print(f"[4] Fechas normalizadas: {dates_ok}/{len(df)}")

    # ── 5. Normalizar ubicación ──
    locations = df["location"].apply(parse_location)
    df["city"]     = locations.apply(lambda x: x[0])
    df["province"] = locations.apply(lambda x: x[1])
    print(f"[5] Ubicaciones procesadas ✓")

    # ── 6. Normalizar modalidad ──
    df["modality_clean"] = df.apply(
        lambda row: parse_modality(
            row.get("modality", ""),
            row.get("title", ""),
            row.get("location", "")
        ), axis=1
    )
    print(f"[6] Modalidades normalizadas ✓")

    # ── 7. Extraer stack básico ──
    df["stack_detected"] = df.apply(
        lambda row: extract_stack(row["title"], row.get("category", "")),
        axis=1
    )
    stack_found = df["stack_detected"].str.strip().ne("").sum()
    print(f"[7] Stack detectado en: {stack_found}/{len(df)} avisos")

    # ── 8. Columna de enriquecimiento por IA (vacía por ahora) ──
    # Se va a llenar en el Paso B (enrich.py)
    df["ai_enriched"]    = False
    df["ai_stack"]       = ""
    df["ai_seniority"]   = ""
    df["ai_is_real_jr"]  = ""

    # ── 9. Seleccionar y ordenar columnas finales ──
    df_clean = df[[
        "category", "title", "company", "city", "province",
        "modality_clean", "salary", "date_clean", "date_posted",
        "stack_detected", "ai_enriched", "ai_stack",
        "ai_seniority", "ai_is_real_jr", "url", "scraped_at"
    ]].copy()

    # Renombrar para claridad
    df_clean = df_clean.rename(columns={
        "modality_clean": "modality",
        "date_clean":     "date",
        "date_posted":    "date_raw",
    })

    # Ordenar por fecha descendente
    df_clean = df_clean.sort_values("date", ascending=False)

    # ── 10. Guardar ──
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    df_clean.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    # ── Reporte final ──
    print(f"\n{'=' * 50}")
    print(f"RESULTADO FINAL")
    print(f"{'=' * 50}")
    print(f"Filas en el clean CSV: {len(df_clean)}")
    print(f"Guardado en: {OUTPUT_FILE.resolve()}")
    print(f"\nDistribución por modalidad:")
    print(df_clean["modality"].value_counts().to_string())
    print(f"\nDistribución por provincia (top 10):")
    print(df_clean["province"].value_counts().head(10).to_string())
    print(f"\nCategorías de búsqueda:")
    print(df_clean["category"].value_counts().to_string())


if __name__ == "__main__":
    main()