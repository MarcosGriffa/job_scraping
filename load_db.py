"""
Paso C: Carga el CSV limpio en una base de datos SQLite.
Power BI se conecta a este archivo .db
"""
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime


INPUT_FILE = Path("data/computrabajo_enriched.csv")
DB_FILE    = Path("data/observatorio.db")


def main():
    print("=" * 50)
    print("  CARGA A SQLITE")
    print("=" * 50)

    if not INPUT_FILE.exists():
        print(f"[ERROR] No existe {INPUT_FILE}")
        print("        Corré primero clean.py")
        return

    # Cargar CSV
    df = pd.read_csv(INPUT_FILE, encoding="utf-8")
    print(f"\nFilas a cargar: {len(df)}")

    # Conectar / crear la base
    DB_FILE.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_FILE)

    # Guardar como tabla SQL
    # if_exists="replace" → sobreescribe cada vez que corrés el script
    # Así Power BI siempre ve datos frescos cuando refrescás
    df.to_sql("jobs", conn, if_exists="replace", index=False)

    # Verificar
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]
    print(f"Filas en la tabla 'jobs': {count}")

    # Mostrar las columnas que quedaron
    cursor.execute("PRAGMA table_info(jobs)")
    cols = [row[1] for row in cursor.fetchall()]
    print(f"Columnas: {cols}")

    # Algunas consultas de prueba
    print("\n--- Preview de datos ---")
    cursor.execute("""
        SELECT modality, COUNT(*) as cantidad
        FROM jobs
        GROUP BY modality
        ORDER BY cantidad DESC
    """)
    print("\nPor modalidad:")
    for row in cursor.fetchall():
        print(f"  {row[0]:<20} {row[1]}")

    cursor.execute("""
        SELECT province, COUNT(*) as cantidad
        FROM jobs
        WHERE province != ''
        GROUP BY province
        ORDER BY cantidad DESC
        LIMIT 8
    """)
    print("\nPor provincia (top 8):")
    for row in cursor.fetchall():
        print(f"  {row[0]:<20} {row[1]}")

    conn.close()
    print(f"\n✓ Base guardada en: {DB_FILE.resolve()}")
    print("  Ya podés conectar Power BI a este archivo.")


        # Notificar a n8n via webhook
    import requests as req
    from collections import Counter



    # Stack más pedido
    all_stack = []
    for s in df["ai_stack"].dropna():
        all_stack.extend([x.strip() for x in str(s).split(",") if x.strip()])
    stack_counter = Counter(all_stack)

    # Generar filas HTML para stack
    stack_rows = ""
    for tech, count in stack_counter.most_common(8):
        if tech and tech != "No especificado":
            pct = round(count / len(df) * 100)
            if pct > 30:
                badge = '<span class="badge badge-green">Alta demanda</span>'
            elif pct > 15:
                badge = '<span class="badge badge-blue">Media</span>'
            else:
                badge = '<span class="badge badge-gray">Baja</span>'
            stack_rows += f"<tr><td><b>{tech}</b></td><td>{count}</td><td>{badge}</td></tr>"

    # Provincias
    provincia_rows = ""
    for prov, count in df["province"].value_counts().head(6).items():
        if prov and str(prov).strip():
            provincia_rows += f"<tr><td>{prov}</td><td>{count}</td></tr>"

        # Palabras que indican NO junior en el título
    no_jr_keywords = ["senior", "ssr", "sr.", " sr ", "semi senior", "semisenior", 
                       "lead", "lider", "líder", "manager", "architect", "principal"]

    def es_junior(row):
        titulo = str(row.get("title", "")).lower()
        seniority = str(row.get("ai_seniority", "")).lower()
    
        # Si el título tiene palabras de senior, descartarlo
        for kw in no_jr_keywords:
            if kw in titulo:
                return False
    
        # Si la IA lo marcó como no junior, descartarlo
        if str(row.get("ai_is_real_jr", "")).upper() == "FALSE":
            return False
        
        return True

    top_avisos = df[
        df.apply(es_junior, axis=1) &
        (df["ai_stack"].str.strip() != "") & 
        (df["ai_stack"] != "No especificado")
    ].head(3)

    avisos_rows = ""
    for _, row in top_avisos.iterrows():
        title = str(row.get("title", ""))[:45]
        company = str(row.get("company", "N/A"))[:25]
        location = str(row.get("city", ""))
        modality = str(row.get("modality", ""))
        avisos_rows += f"<tr><td>{title}</td><td>{company}</td><td>{location}</td><td>{modality}</td></tr>"

    # Métricas
    real_jr = int((df["ai_is_real_jr"] == True).sum()) if "ai_is_real_jr" in df.columns else 0
    descartados = int((df["ai_descartado"] == True).sum()) if "ai_descartado" in df.columns else 0
    pct_remoto = round((df["modality"] == "Remoto").sum() / len(df) * 100)
    stack_top = stack_counter.most_common(1)[0][0] if stack_counter else "N/A"

    webhook_url = "http://localhost:5678/webhook-test/pipeline-completado"
    payload = {
        "total_avisos": len(df),
        "real_jr": real_jr,
        "descartados": descartados,
        "pct_remoto": pct_remoto,
        "stack_top": stack_top,
        "stack_tabla": stack_rows,
        "provincia_tabla": provincia_rows,
        "avisos_tabla": avisos_rows,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    try:
        response = req.post(webhook_url, json=payload, timeout=10)
        print(f"\n✓ n8n notificado: {response.status_code}")
    except Exception as e:
        print(f"\n[WARN] No se pudo notificar a n8n: {e}")

if __name__ == "__main__":
    main()