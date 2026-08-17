# Observatorio IT Junior

Pipeline automatizado que scrapea ofertas de trabajo IT junior en Argentina, las ranquea contra tu perfil y genera CVs adaptados con IA — todo controlable por Telegram desde el celular.

---

## ¿Qué hace?

1. **Scrapea** ofertas IT junior de Computrabajo Argentina (Python, Data, QA, Backend, etc.)
2. **Enriquece** cada oferta con IA (Groq / LLaMA): detecta stack tecnológico, seniority y modalidad
3. **Rankea** las ofertas contra tu CV usando keyword matching sobre el stack extraído
4. **Manda** el Top 10 del día a Telegram con score, empresa, ubicación y tecnologías
5. **Genera CVs** adaptados a cada puesto elegido usando IA (Groq) y los manda como `.docx` por Telegram, junto con el link para aplicar

Todo se controla desde Telegram con comandos de texto, sin abrir la computadora.

---

## Demo

```
Vos → /scrape ok

Bot → Paso 1/7: Scrapeando Computrabajo...
Bot → Paso 2/7: Limpiando datos...
Bot → Paso 3/7: Enriqueciendo con IA...
...
Bot → Top 10 Matches del día:
      [0] Analista de Datos Jr — Score 100/100
      [1] Desarrollador Backend Jr — Score 95/100
      ...

Vos → 0,4

Bot → Generando CVs para puestos 0,4...
Bot → [archivo] CV_Marcos_01_Analista de Datos Jr.docx
Bot → Aplicar: https://ar.computrabajo.com/...
Bot → [archivo] CV_Marcos_02_Desarrollador Backend Jr.docx
Bot → Aplicar: https://ar.computrabajo.com/...
```

---

## Arquitectura

```
Telegram (celular)
      │
      │  long polling
      ▼
bot_listener.py  ◄── único proceso corriendo, orquesta todo
      │
      ├── /scrape ok ──► computrabajo.py  → raw CSV
      │                  clean.py         → CSV limpio
      │                  enrich.py        → CSV + ai_stack, ai_seniority (Groq, paralelo)
      │                  load_db.py       → SQLite
      │                  match.py         → top_matches.csv (keyword scoring)
      │                  scrape_top.py    → top_matches_full.csv + descripciones
      │                  bot_daily.py     → lista Top 10 a Telegram
      │
      └── "0,4,6" ─────► cv_adapter.py   → CV_Marcos_01_*.docx (Groq + Node/docx)
                                            envia .docx + URL por Telegram
```

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Scraping | `requests` + `BeautifulSoup4` |
| IA / LLM | Groq API — `llama-3.3-70b-versatile` + `llama-3.1-8b-instant` |
| PDF | `PyMuPDF` |
| Datos | `pandas`, `SQLite` |
| Generación de CV | Node.js + `docx` npm package |
| Bot | Telegram Bot API (long polling) |
| Lenguaje | Python 3.13 |

---

## Comandos del bot

| Comando | Acción |
|---|---|
| `/scrape` | Muestra advertencia y pide confirmación |
| `/scrape ok` | Pipeline completo desde cero (~12 min) |
| `/refresh` | Solo recalcula matches y manda nueva lista (~1 min) |
| `/last` | Reenvía el último Top 10 sin re-scrapear |
| `/status` | Muestra qué está procesando y hace cuánto |
| `/help` | Menú de comandos |
| `0` o `0,4,6` | Genera CVs adaptados para esos puestos |

---

## Instalación

### Requisitos previos
- Python 3.11+
- Node.js 18+ con el paquete `docx` instalado globalmente:
  ```bash
  npm install -g docx
  ```

### Setup

```bash
# 1. Clonar el repo
git clone https://github.com/TU_USUARIO/job_scraping.git
cd job_scraping

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 3. Crear archivo .env con tus credenciales
cp .env.example .env
# Editar .env con tus API keys
```

### Variables de entorno (`.env`)

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
GROQ_API_KEY=tu_api_key_aqui
```

- **Telegram Bot Token**: crear un bot con [@BotFather](https://t.me/botfather)
- **Chat ID**: obtenerlo con [@userinfobot](https://t.me/userinfobot)
- **Groq API Key**: crear cuenta gratuita en [console.groq.com](https://console.groq.com)

### Agregar tu CV

Reemplazá `CV_Marcos_Griffa_v2.pdf` con tu CV en PDF y actualizá la ruta en `cv_adapter.py` y `match.py`.

### Correr el bot

```bash
python bot_listener.py
```

Para que arranque automáticamente al iniciar Windows, agregá un acceso directo a `start_bot.bat` en la carpeta de Inicio (`shell:startup`).

---

## Estructura del proyecto

```
job_scraping/
├── bot_listener.py      # Bot principal — orquesta todo via Telegram
├── bot_daily.py         # Envía el Top 10 a Telegram
├── computrabajo.py      # Scraper de ofertas IT
├── clean.py             # Limpieza y normalización del CSV
├── enrich.py            # Enriquecimiento con IA (stack, seniority)
├── load_db.py           # Persistencia en SQLite
├── match.py             # Scoring de ofertas contra el perfil
├── scrape_top.py        # Scrapea descripción completa del Top 10
├── cv_adapter.py        # Genera CVs adaptados con IA
├── start_bot.bat        # Script de arranque para Windows
├── requirements.txt
├── .env.example
└── data/                # Generado en runtime (ignorado por git)
    ├── computrabajo_raw.csv
    ├── computrabajo_enriched.csv
    ├── top_matches.csv
    ├── top_matches_full.csv
    ├── observatorio.db
    └── cvs_adaptados/
```

---

## Autor

**Marcos Griffa** — Estudiante de Ciencia de Datos (UBA)  
[LinkedIn](https://linkedin.com/in/marcos-griffa-605aa3259) · [GitHub](https://github.com/MarcosGriffa) · [Portfolio](https://portfolio-griffa.vercel.app)
