"""
generar_datos_demo.py — Genera un dataset SINTÉTICO con la misma forma
exacta que las vistas de análisis (bi/sql/*.sql), para armar el dashboard
de portfolio en Power BI sin tocar la base de datos real de Supabase.

Por qué existe: hoy (26/08/2026) el proyecto recién arrancó y no hay
volumen real de búsquedas/CVs para que los visuales del dashboard se vean
bien. Estos datos son inventados con una semilla fija (reproducibles),
pero con una forma verosímil: mismas fuentes reales del proyecto
(Computrabajo, Jooble, RemoteOK, Jobicy, Himalayas, WeWorkRemotely) en
proporciones parecidas a las que se ven en una corrida real, varios meses
de fechas, y una tasa de aplicación creíble.

IMPORTANTE: esto NO escribe nada en Supabase. Solo genera 3 archivos CSV
en esta misma carpeta, con las columnas EXACTAS de vw_bi_cv_profiles,
vw_bi_cv_skills y vw_bi_ofertas — así el modelo de Power BI armado contra
estos CSVs es idéntico (mismas columnas, mismos tipos) al que resultaría
de conectarse a las vistas reales el día que haya datos de verdad. Cambiar
de uno a otro es solo un cambio de origen de datos en Power Query, sin
tocar relaciones ni medidas DAX.

Uso:
    python bi/datos_demo/generar_datos_demo.py

Genera:
    cv_profiles_demo.csv   (equivalente a vw_bi_cv_profiles)
    cv_skills_demo.csv     (equivalente a vw_bi_cv_skills)
    ofertas_demo.csv       (equivalente a vw_bi_ofertas)
"""

from __future__ import annotations

import csv
import hashlib
import random
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

OUT_DIR = Path(__file__).parent

# Ventana de fechas de la demo: ~5 meses, terminando "hoy" (fecha de
# referencia del proyecto). Con más actividad en los meses recientes,
# para que el gráfico de evolución cuente una historia de adopción
# creciente en vez de una línea plana.
HOY = date(2026, 8, 26)
INICIO = date(2026, 4, 1)

# ── Catálogo de áreas (mismo criterio que cv_profile.py: el área NO está
# hardcodeada a IT) ─────────────────────────────────────────────────────
AREAS = [
    # (área, es_tech, peso, [skills posibles], [títulos posibles])
    ("Data/Analytics", True, 3, [
        "SQL", "Python", "Power BI", "Excel avanzado", "Estadística",
        "Pandas", "Tableau", "ETL", "Visualización de datos",
    ], ["Analista de Datos Jr", "Data Analyst Semi Senior", "BI Analyst",
        "Analista de Business Intelligence"]),
    ("Desarrollo de Software", True, 3, [
        "JavaScript", "React", "Node.js", "Git", "APIs REST", "Python",
        "Java", "SQL", "Docker",
    ], ["Desarrollador Backend Jr", "Full Stack Developer", "Frontend Developer",
        "Desarrollador de Software Semi Senior"]),
    ("QA/Testing", True, 2, [
        "Testing manual", "Selenium", "Jira", "SQL", "Automatización",
        "Python", "Testing de APIs",
    ], ["QA Tester Jr", "Analista de Testing", "QA Automation Semi Senior"]),
    ("Ventas", False, 3, [
        "Negociación", "CRM", "Atención al cliente", "Excel", "Prospección",
        "Ventas B2B",
    ], ["Ejecutivo de Ventas", "Asesor Comercial", "Vendedor sin experiencia",
        "Key Account Manager Jr"]),
    ("Marketing", False, 2, [
        "Redes sociales", "Google Ads", "Copywriting", "Analytics", "Canva",
        "Email marketing",
    ], ["Community Manager", "Analista de Marketing Digital", "Marketing Jr"]),
    ("Administración", False, 3, [
        "Excel", "Facturación", "Atención al cliente", "Gestión documental",
        "SAP",
    ], ["Administrativo Contable", "Asistente Administrativo", "Analista Administrativo Jr"]),
    ("Salud", False, 2, [
        "Atención al paciente", "Primeros auxilios", "Historia clínica",
        "Bioseguridad",
    ], ["Enfermero/a", "Auxiliar de Enfermería", "Técnico en Salud"]),
    ("Biología", False, 1, [
        "Laboratorio", "Microscopía", "Muestreo", "Excel",
        "Redacción científica",
    ], ["Analista de Laboratorio Jr", "Técnico en Biología"]),
]

SENIORITIES = ["junior", "semi senior", "senior"]
SENIORITY_WEIGHTS = [0.45, 0.35, 0.20]

UBICACIONES_LOCAL = ["CABA", "GBA Norte", "GBA Sur", "Córdoba", "Rosario", "Mendoza"]
UBICACIONES_REMOTO = ["Remoto (Argentina)", "Remoto (LATAM)"]

# Fuentes generales: siempre disponibles, cualquier rubro.
FUENTES_GENERALES = ["Jooble", "Computrabajo"]
# Fuentes tech: solo para CVs is_tech=True (ver README_FASE2.md).
FUENTES_TECH = ["RemoteOK", "Jobicy", "Himalayas", "WeWorkRemotely"]

# Pesos calibrados para que, sumando ambos pools en un CV tech, la
# proporción entre las 3 fuentes más frecuentes quede parecida a una
# corrida real del proyecto (Jooble > Computrabajo > Jobicy).
PESOS_FUENTE_TECH = {
    "Jooble": 0.35, "Computrabajo": 0.22, "Jobicy": 0.20,
    "RemoteOK": 0.12, "Himalayas": 0.07, "WeWorkRemotely": 0.04,
}
PESOS_FUENTE_NO_TECH = {"Jooble": 0.62, "Computrabajo": 0.38}

EMPRESAS = [
    "Grupo Andina", "NovaTech Solutions", "Consultora Delta", "Laboratorios BioSur",
    "Retail Horizonte", "Estudio Contable Medina", "Clínica San Rafael",
    "Agro Insumos del Sur", "Banco Regional", "Textil Patagonia",
    "Data Forge", "Cloudberry Labs", "Comercial Los Andes", "Vitalis Salud",
    "Puerto Digital", "Sistemas Australes", "Manufactura Rioplatense",
    "Marketing Cono Sur", "BioLab Argentina", "TechNova Remote",
]

N_USUARIOS = 9
N_CVS = 16


def _job_id(titulo: str, empresa: str, fuente: str) -> str:
    """Mismo criterio que api/job_utils.py:make_job_id — hash estable de
    título+empresa+fuente, para que un job_id no cambie si se regenera."""
    basis = f"{titulo.strip().lower()}::{empresa.strip().lower()}::{fuente}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def _fecha_aleatoria(desde: date, hasta: date, sesgo_reciente: bool = True) -> date:
    """Fecha al azar en el rango, con más densidad hacia el final del
    rango si sesgo_reciente=True (simula adopción creciente)."""
    dias = (hasta - desde).days
    if sesgo_reciente:
        # random.triangular con moda cerca del final: más corridas en los
        # últimos meses que al principio del proyecto.
        offset = random.triangular(0, dias, dias * 0.8)
    else:
        offset = random.uniform(0, dias)
    return desde + timedelta(days=int(offset))


def generar_cvs() -> list[dict]:
    usuarios = [f"anon_{uuid.uuid4().hex[:10]}" for _ in range(N_USUARIOS)]
    pesos_area = [a[2] for a in AREAS]

    cvs = []
    for i in range(N_CVS):
        user_id = usuarios[i % N_USUARIOS] if i < N_USUARIOS else random.choice(usuarios)
        area, is_tech, _, skills_pool, _ = random.choices(AREAS, weights=pesos_area, k=1)[0]
        seniority = random.choices(SENIORITIES, weights=SENIORITY_WEIGHTS, k=1)[0]
        cantidad_skills = random.randint(min(4, len(skills_pool)), min(9, len(skills_pool)))
        skills = random.sample(skills_pool, cantidad_skills)
        # Uniforme (no sesgada): que los CVs se repartan parejo entre los 5
        # meses de la demo, así después las corridas (que salen DESPUÉS de
        # la creación del CV) cubren varios meses y no se amontonan al final.
        created_at = INICIO + timedelta(days=random.randint(0, (HOY - timedelta(days=20) - INICIO).days))

        cvs.append({
            "cv_id": str(uuid.uuid4()),
            "user_id": user_id,
            "area": area,
            "is_tech": is_tech,
            "seniority": seniority,
            "skills": skills,
            "titulos_posibles": next(a[4] for a in AREAS if a[0] == area),
            "created_at": created_at,
        })
    return cvs


def generar_ofertas(cvs: list[dict]) -> list[dict]:
    ofertas = []
    for cv in cvs:
        n_corridas = random.randint(1, 4)
        # Cada corrida posterior a la creación del CV, nunca antes — pero
        # cerca en el tiempo (no salteando hasta HOY), para que la
        # actividad de cada CV quede agrupada alrededor de su propio mes
        # en vez de amontonarse toda al final del rango.
        for _ in range(n_corridas):
            dias_disponibles = max(1, (HOY - cv["created_at"]).days)
            offset = int(random.triangular(0, min(60, dias_disponibles), 10))
            fecha_busqueda_date = cv["created_at"] + timedelta(days=offset)
            fecha_busqueda = datetime.combine(
                fecha_busqueda_date, datetime.min.time()
            ) + timedelta(hours=random.randint(9, 21), minutes=random.randint(0, 59))
            match_id = str(uuid.uuid4())

            n_ofertas = random.randint(6, 10)  # EXPLAIN_TOP_N real = 10
            pesos_fuente = PESOS_FUENTE_TECH if cv["is_tech"] else PESOS_FUENTE_NO_TECH
            fuentes_pool = list(pesos_fuente.keys())
            pesos = list(pesos_fuente.values())

            for _ in range(n_ofertas):
                titulo = random.choice(cv["titulos_posibles"])
                empresa = random.choice(EMPRESAS)
                fuente = random.choices(fuentes_pool, weights=pesos, k=1)[0]
                ubicacion = (
                    random.choice(UBICACIONES_REMOTO)
                    if fuente in FUENTES_TECH
                    else random.choice(UBICACIONES_LOCAL + UBICACIONES_REMOTO[:1])
                )

                score = max(30, min(98, round(random.triangular(35, 98, 72))))
                # Entero 0-100, en la misma escala que score — igual que la
                # vista vw_bi_ofertas, que también la expone escalada (ver el
                # comentario ahí). Entero a propósito: un decimal 0-1 escrito
                # con punto ("0.6511") lo malinterpreta cualquier herramienta
                # con configuración regional española, que lee ese punto como
                # separador de miles y entiende 6511.
                similarity = round(
                    max(25, min(97, score + random.gauss(0, 7)))
                )
                # Más score => menos gaps, en promedio.
                gaps_max = 3 if score < 70 else 1
                cantidad_gaps = random.randint(0, gaps_max)
                cantidad_matches = random.randint(2, 4)

                job_id = _job_id(titulo, empresa, fuente)

                dias_desde_busqueda = (HOY - fecha_busqueda_date).days
                prob_aplicada = 0.10 + (score - 30) / 68 * 0.30
                aplicada = dias_desde_busqueda >= 2 and random.random() < prob_aplicada
                aplicada_en = None
                if aplicada:
                    delta_dias = random.randint(1, max(1, min(dias_desde_busqueda, 20)))
                    aplicada_en = fecha_busqueda + timedelta(
                        days=delta_dias, hours=random.randint(0, 23)
                    )

                ofertas.append({
                    "match_id": match_id,
                    "user_id": cv["user_id"],
                    "cv_id": cv["cv_id"],
                    "fecha_busqueda": fecha_busqueda,
                    "job_id": job_id,
                    "titulo": titulo,
                    "empresa": empresa,
                    "ubicacion": ubicacion,
                    "fuente": fuente,
                    "similarity": similarity,
                    "score": score,
                    "cantidad_matches": cantidad_matches,
                    "cantidad_gaps": cantidad_gaps,
                    "aplicada": aplicada,
                    "aplicada_en": aplicada_en,
                })
    return ofertas


def escribir_cv_profiles(cvs: list[dict]) -> None:
    path = OUT_DIR / "cv_profiles_demo.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cv_id", "user_id", "area", "is_tech", "seniority",
                    "cantidad_skills", "created_at"])
        for cv in cvs:
            w.writerow([
                cv["cv_id"], cv["user_id"], cv["area"], cv["is_tech"],
                cv["seniority"], len(cv["skills"]),
                cv["created_at"].isoformat(),
            ])
    print(f"OK -> {path} ({len(cvs)} filas)")


def escribir_cv_skills(cvs: list[dict]) -> None:
    path = OUT_DIR / "cv_skills_demo.csv"
    filas = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cv_id", "user_id", "skill"])
        for cv in cvs:
            for skill in cv["skills"]:
                w.writerow([cv["cv_id"], cv["user_id"], skill])
                filas += 1
    print(f"OK -> {path} ({filas} filas)")


def escribir_ofertas(ofertas: list[dict]) -> None:
    path = OUT_DIR / "ofertas_demo.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["match_id", "user_id", "cv_id", "fecha_busqueda", "job_id",
                    "titulo", "empresa", "ubicacion", "fuente", "similarity",
                    "score", "cantidad_matches", "cantidad_gaps", "aplicada",
                    "aplicada_en"])
        for o in ofertas:
            w.writerow([
                o["match_id"], o["user_id"], o["cv_id"],
                o["fecha_busqueda"].isoformat(sep=" "),
                o["job_id"], o["titulo"], o["empresa"], o["ubicacion"],
                o["fuente"], o["similarity"], o["score"],
                o["cantidad_matches"], o["cantidad_gaps"], o["aplicada"],
                o["aplicada_en"].isoformat(sep=" ") if o["aplicada_en"] else "",
            ])
    print(f"OK -> {path} ({len(ofertas)} filas)")


if __name__ == "__main__":
    cvs = generar_cvs()
    ofertas = generar_ofertas(cvs)

    escribir_cv_profiles(cvs)
    escribir_cv_skills(cvs)
    escribir_ofertas(ofertas)

    print(f"\nListo. {len(cvs)} CVs, {len(ofertas)} ofertas evaluadas, "
          f"semilla={SEED} (reproducible).")
    print("Recordatorio: esto NO toca Supabase — son 3 CSV locales para el "
          "dashboard de demo (ver bi/README.md).")
