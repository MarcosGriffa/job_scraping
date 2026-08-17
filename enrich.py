"""
Sprint 4: Enriquecimiento con IA (Groq) — versión optimizada

Cambios vs versión original:
- Sin delay artificial (Groq aguanta 30 req/min en tier free, no necesitamos sleeps)
- Paralelización con ThreadPoolExecutor (5 requests en vuelo a la vez)
- Deduplicación por (title, company): ofertas repetidas reusan el mismo resultado
- Resume desde donde quedó (ai_enriched == True se saltea)
"""

import os
import json
import sqlite3
import pandas as pd
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ── Config ─────────────────────────────────────────────────────
INPUT_FILE   = Path("data/computrabajo_clean.csv")
OUTPUT_FILE  = Path("data/computrabajo_enriched.csv")
DB_FILE      = Path("data/observatorio.db")

MODEL          = "openai/gpt-oss-20b"   # Llama 3.x dado de baja por Groq (17/08/2026)
MAX_RETRIES    = 3
PARALLEL_REQS  = 5      # llamadas concurrentes a Groq
SAVE_EVERY     = 50     # guardar progreso cada N ofertas enriquecidas

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# ── Prompt ─────────────────────────────────────────────────────
SYSTEM_PROMPT = """Sos un experto en análisis del mercado laboral IT argentino.
Analizás avisos de empleo y extraés información estructurada.
Respondés ÚNICAMENTE con JSON válido, sin texto adicional, sin markdown."""


def build_prompt(row: dict) -> str:
    return f"""Analizá este aviso de empleo IT y respondé con JSON:

Título: {row.get('title', '')}
Empresa: {row.get('company', '')}
Categoría de búsqueda: {row.get('category', '')}
Ubicación: {row.get('city', '')} {row.get('province', '')}
Modalidad detectada: {row.get('modality', '')}

Respondé con este JSON exacto:
{{
  "stack_real": ["tecnologia1", "tecnologia2"],
  "seniority_real": "Junior|Semi-Senior|Senior|No especificado",
  "is_real_jr": true|false,
  "tipo_empresa": "Consultora RRHH|Startup|Multinacional|PyME|No especificado",
  "descartado": true|false,
  "motivo_descarte": "razón si descartado, sino null"
}}

Reglas:
- stack_real: solo tecnologías concretas (Python, SQL, Java, etc). Máximo 5.
- is_real_jr: false si pide más de 2 años de experiencia o es claramente Senior
- descartado: true si no es un rol IT real (ventas, administrativo, etc)
- Si no hay info suficiente, usá "No especificado"
"""


# ── Llamada a Groq ─────────────────────────────────────────────
def enrich_job(row: dict) -> dict:
    """Llama a Groq y devuelve los campos enriquecidos."""
    import time

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": build_prompt(row)}
                ],
                temperature=0.1,
                max_tokens=200,
            )

            raw = response.choices[0].message.content.strip()

            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            data = json.loads(raw)
            return {
                "ai_enriched":     True,
                "ai_stack":        ", ".join(data.get("stack_real", [])),
                "ai_seniority":    data.get("seniority_real", ""),
                "ai_is_real_jr":   data.get("is_real_jr", True),
                "ai_tipo_empresa": data.get("tipo_empresa", ""),
                "ai_descartado":   data.get("descartado", False),
                "ai_motivo":       data.get("motivo_descarte", ""),
            }

        except json.JSONDecodeError:
            time.sleep(1)
        except Exception as e:
            # Probable rate limit: backoff exponencial corto
            wait = 2 ** attempt
            print(f"    [retry {attempt+1}] {type(e).__name__}: esperando {wait}s")
            time.sleep(wait)

    return {
        "ai_enriched": False,
        "ai_stack": "", "ai_seniority": "",
        "ai_is_real_jr": None, "ai_tipo_empresa": "",
        "ai_descartado": None, "ai_motivo": ""
    }


# ── Helpers ────────────────────────────────────────────────────
def make_dedup_key(row: dict) -> str:
    """Misma oferta = mismo (título, empresa) normalizados."""
    title = str(row.get("title", "")).strip().lower()
    company = str(row.get("company", "")).strip().lower()
    return f"{title}||{company}"


def save_df(df: pd.DataFrame):
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")


# ── Pipeline principal ─────────────────────────────────────────
def main():
    print("=" * 55)
    print("  ENRIQUECIMIENTO CON IA — GROQ (paralelo + dedup)")
    print("=" * 55)

    if not INPUT_FILE.exists():
        print(f"[ERROR] No existe {INPUT_FILE}. Corré clean.py primero.")
        return

    # Si ya hay un enriched parcial (de una corrida previa), lo cargamos para no perder progreso
    if OUTPUT_FILE.exists():
        df = pd.read_csv(OUTPUT_FILE, encoding="utf-8")
        print(f"Continuando desde {OUTPUT_FILE} ({len(df)} filas)")
    else:
        df = pd.read_csv(INPUT_FILE, encoding="utf-8")
        print(f"Empezando desde cero: {len(df)} avisos")

    # Asegurar columnas IA
    str_cols  = ["ai_stack", "ai_seniority", "ai_tipo_empresa", "ai_motivo"]
    bool_cols = ["ai_enriched", "ai_is_real_jr", "ai_descartado"]

    for col in str_cols:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype(object)

    for col in bool_cols:
        if col not in df.columns:
            df[col] = None
        df[col] = df[col].astype(object)

    # ── Dedup: 1 llamada por (título, empresa) único ──
    df["_dedup_key"] = df.apply(lambda r: make_dedup_key(r.to_dict()), axis=1)

    # Pendientes: filas que no están enriquecidas todavía
    pending_mask = df["ai_enriched"] != True
    pending_keys = df.loc[pending_mask, "_dedup_key"].unique().tolist()

    print(f"Filas pendientes: {pending_mask.sum()}")
    print(f"Ofertas únicas (dedup): {len(pending_keys)}")
    print(f"Ahorro por dedup: {pending_mask.sum() - len(pending_keys)} llamadas evitadas\n")

    if not pending_keys:
        print("Todo ya está enriquecido.")
        df.drop(columns=["_dedup_key"], inplace=True, errors="ignore")
        save_df(df)
        return

    # Una fila representativa por cada key única (la primera ocurrencia)
    representative_rows = (
        df[pending_mask]
          .drop_duplicates(subset="_dedup_key", keep="first")
          .set_index("_dedup_key")
    )

    results: dict[str, dict] = {}
    completed = 0
    errors = 0

    # ── Procesar en paralelo ──
    with ThreadPoolExecutor(max_workers=PARALLEL_REQS) as executor:
        future_to_key = {
            executor.submit(enrich_job, representative_rows.loc[k].to_dict()): k
            for k in pending_keys
        }

        for future in as_completed(future_to_key):
            key = future_to_key[future]
            try:
                result = future.result()
            except Exception as e:
                print(f"    [FATAL] {key[:60]}: {e}")
                result = {"ai_enriched": False}

            results[key] = result
            completed += 1

            row_preview = representative_rows.loc[key].to_dict()
            title = str(row_preview.get("title", ""))[:50]
            if result.get("ai_enriched"):
                stack = result.get("ai_stack") or "sin stack"
                print(f"  [{completed}/{len(pending_keys)}] ✓ {title}  |  {result.get('ai_seniority')}  |  {stack}")
            else:
                errors += 1
                print(f"  [{completed}/{len(pending_keys)}] ✗ {title}")

            # Guardar progreso periódicamente
            if completed % SAVE_EVERY == 0:
                _apply_results_to_df(df, results)
                save_df(df)
                print(f"\n  [Progreso guardado: {completed}/{len(pending_keys)}]\n")

    # Aplicar todos los resultados al DataFrame (incluidos duplicados)
    _apply_results_to_df(df, results)

    # Limpiar columna auxiliar y guardar
    df.drop(columns=["_dedup_key"], inplace=True, errors="ignore")
    save_df(df)

    # Actualizar SQLite
    print("\nActualizando SQLite...")
    conn = sqlite3.connect(DB_FILE)
    df.to_sql("jobs", conn, if_exists="replace", index=False)
    conn.close()

    # ── Reporte ──
    enriched    = (df["ai_enriched"] == True).sum()
    real_jr     = (df["ai_is_real_jr"] == True).sum()
    descartados = (df["ai_descartado"] == True).sum()

    print(f"\n{'=' * 55}")
    print("RESULTADO")
    print(f"{'=' * 55}")
    print(f"Enriquecidos: {enriched}/{len(df)}")
    print(f"Son realmente Jr: {real_jr}")
    print(f"Descartados (off-topic): {descartados}")
    print(f"Errores en esta corrida: {errors}")

    all_stack = []
    for s in df["ai_stack"].dropna():
        all_stack.extend([x.strip() for x in s.split(",") if x.strip()])

    print(f"\nTop stack (IA):")
    for tech, count in Counter(all_stack).most_common(10):
        print(f"  {tech:<20} {count}")

    print(f"\n✓ Guardado en {OUTPUT_FILE}")


def _apply_results_to_df(df: pd.DataFrame, results: dict[str, dict]):
    """Propaga el resultado de cada key única a todas las filas con esa key."""
    for key, result in results.items():
        mask = df["_dedup_key"] == key
        for col, val in result.items():
            df.loc[mask, col] = val


if __name__ == "__main__":
    main()