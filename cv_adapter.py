"""
cv_adapter.py — Generador interactivo de CVs adaptados

Muestra los top matches con su descripción completa,
te deja elegir cuáles adaptar, y genera un .docx por puesto
respetando el diseño de tu CV original.
"""

import os
import json
import time
import argparse
import subprocess
import pandas as pd
import fitz
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ── Config ─────────────────────────────────────────────────────
CV_PDF        = Path("CV_Marcos_Griffa_v2.pdf")
MATCHES_FILE  = Path("data/top_matches_full.csv")  # Ya tiene las descripciones
OUTPUT_DIR    = Path("data/cvs_adaptados")
MODEL         = "openai/gpt-oss-120b"  # Llama 3.x dado de baja por Groq (17/08/2026)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# ── Leer CV ────────────────────────────────────────────────────
def extract_cv_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


# ── Selección interactiva ──────────────────────────────────────
def show_and_select(df: pd.DataFrame) -> list:
    print("\n" + "=" * 70)
    print("  REVISIÓN DE PUESTOS — Elegí cuáles adaptar")
    print("=" * 70)

    for i, row in df.iterrows():
        title = str(row.get("title", ""))[:60]
        company = str(row.get("company", ""))[:40]
        city = str(row.get("city", ""))
        modality = str(row.get("modality", ""))
        score = row.get("score", 0)
        stack = str(row.get("ai_stack", ""))[:60]
        desc = str(row.get("description", ""))[:400]

        print(f"\n{'─' * 70}")
        print(f"[{i}] {title}")
        print(f"     {company}  |  {city}  |  {modality}  |  Score IA: {score}")
        print(f"     Stack pedido: {stack}")
        print(f"\n     Descripción:")
        # Indentar la descripción
        for line in desc.split(". ")[:4]:
            if line.strip():
                print(f"       {line.strip()}.")

    print(f"\n{'=' * 70}")
    print("¿Cuáles puestos querés adaptar?")
    print("Escribí los números separados por coma (ej: 4,7,8)")
    print("O escribí 'all' para todos, 'q' para salir")
    print(f"{'=' * 70}")

    while True:
        choice = input("\n>> ").strip().lower()

        if choice == "q":
            return []

        if choice == "all":
            return df.index.tolist()

        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            valid = [i for i in indices if 0 <= i < len(df)]
            if not valid:
                print("  [!] Ningún índice válido. Probá de nuevo.")
                continue
            return valid
        except ValueError:
            print("  [!] Formato inválido. Probá con: 4,7,8")


# ── Adaptar CV con IA ──────────────────────────────────────────
def adapt_cv(cv_text: str, job: dict) -> dict:
    """Le pide a Groq que adapte el CV usando la descripción real."""
    prompt = f"""Sos un experto en redacción de CVs para el mercado IT argentino.
Adaptá el CV de Marcos para que matchee mejor con una oferta laboral específica.

REGLAS:
- NO inventés experiencia ni skills que Marcos no tiene
- Solo reorganizá, reenfocá y optimizá el lenguaje existente
- Mantené exactamente la misma estructura de secciones
- Usá palabras clave del aviso donde sea honesto hacerlo
- El resultado debe sonar natural, no genérico

=== CV ORIGINAL ===
{cv_text[:2500]}

=== PUESTO ===
Título: {job.get('title', '')}
Empresa: {job.get('company', '')}
Modalidad: {job.get('modality', '')}
Stack pedido: {job.get('ai_stack', '')}

=== DESCRIPCIÓN COMPLETA DEL AVISO ===
{str(job.get('description', ''))[:1800]}

Respondé con un JSON con estas claves exactas:
{{
  "perfil": "<párrafo de perfil profesional adaptado al puesto, 3-4 oraciones>",
  "experiencia_ferrosider": "<3-4 bullets de Ferrosider reenfocados, separados por |>",
  "proyecto_1_nombre": "<nombre del proyecto más relevante para este puesto>",
  "proyecto_1_desc": "<descripción del proyecto más relevante, 2 líneas>",
  "proyecto_2_nombre": "<nombre del segundo proyecto>",
  "proyecto_2_desc": "<descripción del segundo proyecto, 2 líneas>",
  "skills_destacadas": "<4-5 skills técnicas más relevantes para este puesto, separadas por coma>",
  "headline": "<tagline de 1 línea debajo del nombre, orientado al puesto>"
}}
"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Respondés ÚNICAMENTE con JSON válido, sin markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=900,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw)
        except Exception as e:
            print(f"    [WARN] intento {attempt+1}: {e}")
            time.sleep(5)
    return {}


# ── Generar .docx ──────────────────────────────────────────────
def generate_docx(adapted: dict, output_path: Path):
    """Genera el .docx con Node.js manteniendo el diseño del CV original."""

    def esc(s):
        return str(s).replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    perfil = esc(adapted.get("perfil", ""))
    headline = esc(adapted.get("headline", "Estudiante de Ciencia de Datos · Python · SQL · n8n · IA Generativa"))
    ferrosider_bullets = adapted.get("experiencia_ferrosider", "").split("|")
    p1_nombre = esc(adapted.get("proyecto_1_nombre", "Observatorio IT Junior"))
    p1_desc = esc(adapted.get("proyecto_1_desc", ""))
    p2_nombre = esc(adapted.get("proyecto_2_nombre", "Web Scraping MercadoLibre"))
    p2_desc = esc(adapted.get("proyecto_2_desc", ""))
    skills = esc(adapted.get("skills_destacadas", "Python, SQL, n8n, IA Generativa"))

    ferrosider_js = "\n".join([
        f'new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, spacing: {{ after: 60 }}, children: [new TextRun({{ text: `{esc(b.strip())}`, size: 18 }})] }}),'
        for b in ferrosider_bullets if b.strip()
    ])

    js_code = f"""
const fs = require('fs');
const {{ Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
         AlignmentType, LevelFormat, BorderStyle, WidthType, ShadingType,
         VerticalAlign }} = require('docx');

const noBorder = {{ style: BorderStyle.NONE, size: 0, color: "FFFFFF" }};
const noBorders = {{ top: noBorder, bottom: noBorder, left: noBorder, right: noBorder, insideHorizontal: noBorder, insideVertical: noBorder }};

const txt = (text, opts = {{}}) => new TextRun({{ text, font: "Calibri", ...opts }});

const sectionTitle = (label) => new Paragraph({{
  spacing: {{ before: 140, after: 60 }},
  border: {{ bottom: {{ style: BorderStyle.SINGLE, size: 8, color: "F2C500", space: 2 }} }},
  children: [txt(label.toUpperCase(), {{ bold: true, size: 18, color: "1F3864", characterSpacing: 40 }})]
}});

const sidebarTitle = (label) => new Paragraph({{
  spacing: {{ before: 120, after: 50 }},
  border: {{ bottom: {{ style: BorderStyle.SINGLE, size: 6, color: "F2C500", space: 2 }} }},
  children: [txt(label.toUpperCase(), {{ bold: true, size: 16, color: "1F3864" }})]
}});

const skillPill = (text) => new Paragraph({{
  spacing: {{ after: 30 }},
  children: [txt("▸ " + text, {{ size: 17 }})]
}});

const leftCol = [
  sectionTitle("Perfil"),
  new Paragraph({{ spacing: {{ after: 80 }}, alignment: AlignmentType.JUSTIFIED, children: [txt(`{perfil}`, {{ size: 18 }})] }}),

  sectionTitle("Proyectos destacados"),
  new Paragraph({{ spacing: {{ before: 60, after: 20 }}, children: [txt(`{p1_nombre}`, {{ bold: true, size: 19, color: "1F3864" }})] }}),
  new Paragraph({{ spacing: {{ after: 40 }}, children: [txt(`{p1_desc}`, {{ size: 17 }})] }}),

  new Paragraph({{ spacing: {{ before: 100, after: 20 }}, children: [txt(`{p2_nombre}`, {{ bold: true, size: 19, color: "1F3864" }})] }}),
  new Paragraph({{ spacing: {{ after: 40 }}, children: [txt(`{p2_desc}`, {{ size: 17 }})] }}),

  new Paragraph({{ spacing: {{ before: 100, after: 20 }}, children: [txt("Aplicaciones lógicas en Python (Battleship, Minesweeper)", {{ bold: true, size: 19, color: "1F3864" }})] }}),
  new Paragraph({{ spacing: {{ after: 40 }}, children: [txt("Desarrollo desde cero aplicando POO y algoritmos. Ejercicios de pensamiento computacional sobre estructuras 2D.", {{ size: 17 }})] }}),

  sectionTitle("Experiencia laboral"),
  new Paragraph({{
    tabStops: [{{ type: "right", position: 6720 }}],
    spacing: {{ before: 60, after: 20 }},
    children: [
      txt("FERROSIDER", {{ bold: true, size: 19, color: "1F3864" }}),
      txt("\\t03/2024 – Actualidad", {{ size: 16, italics: true, color: "595959" }})
    ]
  }}),
  new Paragraph({{ spacing: {{ after: 40 }}, children: [txt("Surveyor / Control de Operaciones — Puerto Dock Sud", {{ italics: true, size: 17 }})] }}),
  {ferrosider_js}

  new Paragraph({{
    tabStops: [{{ type: "right", position: 6720 }}],
    spacing: {{ before: 140, after: 20 }},
    children: [
      txt("CADENA DE ALIMENTOS", {{ bold: true, size: 19, color: "1F3864" }}),
      txt("\\t10/2024 – 03/2025", {{ size: 16, italics: true, color: "595959" }})
    ]
  }}),
  new Paragraph({{ spacing: {{ after: 40 }}, children: [txt("Encargado de Local / Coordinador Operativo", {{ italics: true, size: 17 }})] }}),
  new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, spacing: {{ after: 40 }}, children: [txt("Coordinación del equipo y operativa diaria bajo presión.", {{ size: 17 }})] }}),
  new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, spacing: {{ after: 40 }}, children: [txt("Gestión de reportes de caja y comunicación entre áreas.", {{ size: 17 }})] }}),
];

const rightCol = [
  sidebarTitle("Educación"),
  new Paragraph({{ spacing: {{ after: 20 }}, children: [txt("Universidad de Buenos Aires", {{ bold: true, italics: true, size: 18 }})] }}),
  new Paragraph({{ spacing: {{ after: 20 }}, children: [txt("Lic. en Ciencia de Datos", {{ size: 17 }})] }}),
  new Paragraph({{ spacing: {{ after: 60 }}, children: [txt("En curso — 1° año", {{ size: 15, italics: true, color: "595959" }})] }}),
  new Paragraph({{ spacing: {{ after: 100 }}, children: [txt("Estadística · Bases de Datos · Visualización · Python / SQL", {{ size: 14, color: "595959" }})] }}),
  new Paragraph({{ spacing: {{ after: 20 }}, children: [txt("Instituto Dr. Nicolás Avellaneda", {{ bold: true, italics: true, size: 17 }})] }}),
  new Paragraph({{ spacing: {{ after: 60 }}, children: [txt("Secundario completo", {{ size: 16, color: "595959" }})] }}),

  sidebarTitle("Stack técnico"),
  ..."{skills}".split(",").map(s => skillPill(s.trim())),
  skillPill("Git / GitHub"),
  skillPill("Excel avanzado"),

  sidebarTitle("Idiomas"),
  skillPill("Español (Nativo)"),
  skillPill("Inglés (Intermedio)"),

  sidebarTitle("Competencias"),
  skillPill("Trabajo en equipo"),
  skillPill("Comunicación con stakeholders"),
  skillPill("Aprendizaje continuo"),
  skillPill("Resolución de problemas"),

  sidebarTitle("Sobre mí"),
  new Paragraph({{ spacing: {{ after: 40 }}, alignment: AlignmentType.JUSTIFIED, children: [txt("Juego al rugby desde los 10 años. Disciplina, trabajo colectivo y mentalidad competitiva.", {{ size: 15 }})] }}),
];

const headerTable = new Table({{
  width: {{ size: 10440, type: WidthType.DXA }},
  columnWidths: [6960, 3480],
  borders: noBorders,
  rows: [new TableRow({{ children: [
    new TableCell({{
      borders: noBorders, width: {{ size: 6960, type: WidthType.DXA }},
      shading: {{ fill: "1F3864", type: ShadingType.CLEAR }},
      margins: {{ top: 240, bottom: 240, left: 360, right: 240 }},
      verticalAlign: VerticalAlign.CENTER,
      children: [
        new Paragraph({{ spacing: {{ after: 80 }}, children: [txt("Marcos Griffa", {{ bold: true, italics: true, size: 44, color: "FFFFFF" }})] }}),
        new Paragraph({{ children: [txt(`{headline}`, {{ size: 17, color: "FFFFFF" }})] }})
      ]
    }}),
    new TableCell({{
      borders: noBorders, width: {{ size: 3480, type: WidthType.DXA }},
      shading: {{ fill: "1F3864", type: ShadingType.CLEAR }},
      margins: {{ top: 240, bottom: 240, left: 200, right: 240 }},
      verticalAlign: VerticalAlign.CENTER,
      children: [
        new Paragraph({{ spacing: {{ after: 30 }}, children: [txt("11 6142-8659", {{ size: 15, color: "FFFFFF" }})] }}),
        new Paragraph({{ spacing: {{ after: 30 }}, children: [txt("marcosgriffa04@gmail.com", {{ size: 15, color: "FFFFFF" }})] }}),
        new Paragraph({{ spacing: {{ after: 30 }}, children: [txt("linkedin.com/in/marcos-griffa-605aa3259", {{ size: 14, color: "FFFFFF" }})] }}),
        new Paragraph({{ spacing: {{ after: 30 }}, children: [txt("github.com/MarcosGriffa", {{ size: 15, color: "FFFFFF" }})] }}),
        new Paragraph({{ children: [txt("portfolio-griffa.vercel.app", {{ size: 14, color: "FFFFFF" }})] }}),
      ]
    }})
  ]}})]
}});

const bodyTable = new Table({{
  width: {{ size: 10440, type: WidthType.DXA }},
  columnWidths: [6960, 3480],
  borders: noBorders,
  rows: [new TableRow({{ children: [
    new TableCell({{
      borders: noBorders, width: {{ size: 6960, type: WidthType.DXA }},
      margins: {{ top: 200, bottom: 200, left: 200, right: 300 }},
      verticalAlign: VerticalAlign.TOP,
      children: leftCol
    }}),
    new TableCell({{
      borders: noBorders, width: {{ size: 3480, type: WidthType.DXA }},
      shading: {{ fill: "F5F5F5", type: ShadingType.CLEAR }},
      margins: {{ top: 200, bottom: 200, left: 240, right: 240 }},
      verticalAlign: VerticalAlign.TOP,
      children: rightCol
    }})
  ]}})]
}});

const doc = new Document({{
  styles: {{ default: {{ document: {{ run: {{ font: "Calibri", size: 20 }} }} }} }},
  numbering: {{ config: [{{ reference: "bullets", levels: [{{ level: 0, format: LevelFormat.BULLET, text: "▪", alignment: AlignmentType.LEFT, style: {{ paragraph: {{ indent: {{ left: 240, hanging: 160 }} }} }} }}] }}] }},
  sections: [{{ properties: {{ page: {{ size: {{ width: 12240, height: 15840 }}, margin: {{ top: 720, right: 720, bottom: 720, left: 720 }} }} }}, children: [headerTable, new Paragraph({{ spacing: {{ after: 80 }}, children: [txt("")] }}), bodyTable] }}]
}});

Packer.toBuffer(doc).then(buffer => {{
  fs.writeFileSync("{output_path.as_posix()}", buffer);
  console.log("OK");
}});
"""

    js_file = Path("data/_temp_cv.js")
    js_file.write_text(js_code, encoding="utf-8")

    env = os.environ.copy()
    env["NODE_PATH"] = os.path.expandvars(r"%APPDATA%\npm\node_modules")
    result = subprocess.run(
        ["node", str(js_file)],
        capture_output=True, text=True, env=env
    )
    js_file.unlink()

    if "OK" in result.stdout:
        return True
    print(f"    [ERROR Node] {result.stderr[:300]}")
    return False


# ── Main ───────────────────────────────────────────────────────
def main(indices_arg: str = None):
    print("=" * 70)
    print("  CV ADAPTER INTERACTIVO")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cv_text = extract_cv_text(CV_PDF)
    print(f"CV leído: {len(cv_text)} caracteres\n")

    df = pd.read_csv(MATCHES_FILE, encoding="utf-8")

    if indices_arg is not None:
        try:
            selected = [int(x.strip()) for x in indices_arg.split(",") if x.strip()]
            selected = [i for i in selected if 0 <= i < len(df)]
        except ValueError:
            print(f"[ERROR] Índices inválidos: {indices_arg}")
            return
    else:
        selected = show_and_select(df)

    if not selected:
        print("\nNo se seleccionó ningún puesto. Saliendo.")
        return

    print(f"\n✓ Generarás {len(selected)} CV(s) adaptado(s)\n")

    for n, idx in enumerate(selected, 1):
        job = df.iloc[idx]
        title = str(job.get("title", ""))[:50]
        company = str(job.get("company", ""))[:25]

        print(f"\n[{n}/{len(selected)}] Adaptando para: {title}")
        print(f"         Empresa: {company}")

        # Adaptar con IA
        print(f"         Generando texto con IA...")
        adapted = adapt_cv(cv_text, job.to_dict())

        if not adapted:
            print(f"         ✗ Error adaptando")
            continue

        # Generar archivo
        safe_title = "".join(c for c in title if c.isalnum() or c in " -")[:30].strip()
        output_path = OUTPUT_DIR / f"CV_Marcos_{n:02d}_{safe_title}.docx"

        print(f"         Generando .docx...")
        if generate_docx(adapted, output_path):
            print(f"         ✓ Guardado: {output_path.name}")
        else:
            print(f"         ✗ Error generando archivo")

        time.sleep(2)

    print(f"\n{'=' * 70}")
    print(f"CVs generados en: {OUTPUT_DIR.resolve()}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--indices", type=str, default=None,
                        help="Índices separados por coma (ej: 4,7,8). Si no se pasa, modo interactivo.")
    args = parser.parse_args()
    main(args.indices)