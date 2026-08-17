"""
bot_listener.py — Bot Telegram con comandos para el pipeline de CVs.

Comandos:
  /start, /help     Menú
  /status           ¿Procesando algo?
  /scrape           Pipeline completo desde cero (pide confirmación)
  /scrape ok        Confirma y arranca
  /refresh          Solo re-matchea sobre datos ya scrapeados
  /last             Reenvía la última lista
  N o N,N,N         Genera CVs adaptados para esos índices

Correrlo:
    python bot_listener.py
"""

import os
import sys
import subprocess
import threading
import time
import signal
import atexit
import ctypes
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TOKEN        = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID      = os.environ.get("TELEGRAM_CHAT_ID")
BASE_URL     = f"https://api.telegram.org/bot{TOKEN}"

PROJECT_DIR  = Path(__file__).parent
DATA_DIR     = PROJECT_DIR / "data"
CVS_DIR      = DATA_DIR / "cvs_adaptados"
OFFSET_FILE  = DATA_DIR / ".bot_offset"
LOCK_FILE    = DATA_DIR / ".bot.lock"
POLL_TIMEOUT = 30

# Pipelines: (mensaje_telegram, script, timeout_segundos)
SCRAPE_FULL = [
    ("Scrapeando ofertas en Computrabajo...", "computrabajo.py", 600),
    ("Limpiando datos...",                    "clean.py",        120),
    ("Enriqueciendo con IA (Groq)...",        "enrich.py",       600),
    ("Guardando en base de datos...",         "load_db.py",      120),
    ("Calculando matches con tu CV...",       "match.py",         60),
    ("Scrapeando descripciones de top 10...", "scrape_top.py",   300),
    ("Enviando lista a Telegram...",          "bot_daily.py",     60),
]

REFRESH = [
    ("Recalculando matches...",               "match.py",         60),
    ("Scrapeando descripciones de top 10...", "scrape_top.py",   300),
    ("Enviando lista a Telegram...",          "bot_daily.py",     60),
]

# Archivos que /scrape borra
FILES_TO_RESET = [
    "computrabajo_raw.csv",
    "computrabajo_clean.csv",
    "computrabajo_enriched.csv",
    "observatorio.db",
    "top_matches.csv",
    "top_matches_full.csv",
]

# ─────────────────────────────────────────────────────────────
# Estado en memoria
# ─────────────────────────────────────────────────────────────
state = {
    "busy": False,
    "task": None,
    "started_at": None,
    "awaiting_scrape_confirm": False,
}


# ─────────────────────────────────────────────────────────────
# PID Lock — evita instancias duplicadas
# ─────────────────────────────────────────────────────────────
def _is_pid_alive(pid: int) -> bool:
    """Verifica si un PID está vivo en Windows via WinAPI."""
    try:
        # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        exit_code = ctypes.c_ulong(0)
        ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return exit_code.value == 259  # STILL_ACTIVE
    except Exception:
        return False


def _release_lock():
    if LOCK_FILE.exists():
        try:
            LOCK_FILE.unlink()
        except OSError:
            pass


def _handle_signal(_signum, _frame):
    _release_lock()
    sys.exit(0)


def acquire_lock():
    """Escribe data/.bot.lock con el PID actual. Sale si ya hay una instancia viva."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if LOCK_FILE.exists():
        try:
            existing_pid = int(LOCK_FILE.read_text().strip())
            if _is_pid_alive(existing_pid):
                print(f"[FATAL] Ya hay una instancia corriendo (PID {existing_pid}).")
                print(f"        Cerrala con Ctrl+C antes de arrancar una nueva.")
                print(f"        Si ya no existe, borrá manualmente: {LOCK_FILE}")
                sys.exit(1)
            else:
                print(f"[WARN] Lock obsoleto de PID {existing_pid} (proceso ya muerto). Sobrescribiendo.")
        except (ValueError, OSError):
            pass  # Archivo corrupto — sobrescribir

    LOCK_FILE.write_text(str(os.getpid()))
    atexit.register(_release_lock)
    signal.signal(signal.SIGTERM, _handle_signal)


# ─────────────────────────────────────────────────────────────
# Helpers Telegram
# ─────────────────────────────────────────────────────────────
def send_message(text: str):
    try:
        requests.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        print(f"[send_message ERROR] {e}")


def send_document(file_path: Path, caption: str = ""):
    try:
        with open(file_path, "rb") as f:
            requests.post(
                f"{BASE_URL}/sendDocument",
                data={"chat_id": CHAT_ID, "caption": caption},
                files={"document": f},
                timeout=60,
            )
    except Exception as e:
        print(f"[send_document ERROR] {e}")


# ─────────────────────────────────────────────────────────────
# Offset (para no reprocesar al reiniciar)
# ─────────────────────────────────────────────────────────────
def load_offset() -> int:
    if OFFSET_FILE.exists():
        try:
            return int(OFFSET_FILE.read_text().strip())
        except Exception:
            return 0
    return 0


def save_offset(offset: int):
    OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_FILE.write_text(str(offset))


# ─────────────────────────────────────────────────────────────
# Subprocess con logging en tiempo real (Popen + threads)
# ─────────────────────────────────────────────────────────────
def _stream_reader(stream, lines: list, label: str):
    """Lee un stream línea por línea e imprime en tiempo real."""
    try:
        for line in stream:
            line = line.rstrip("\n")
            lines.append(line)
            print(f"  [{label}] {line}", flush=True)
    except Exception:
        pass


def run_script(
    script: str,
    timeout: int = 120,
    extra_args: list[str] | None = None,
) -> tuple[bool, str]:
    """
    Corre un script Python con logging en tiempo real vía Popen.
    Devuelve (ok, error_msg_si_falla).
    """
    if not (PROJECT_DIR / script).exists():
        return False, f"No existe el archivo: {script}"

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"]       = "1"
    env["PYTHONUNBUFFERED"] = "1"   # fuerza output sin buffer

    cmd = [sys.executable, "-u", script]  # -u: unbuffered
    if extra_args:
        cmd.extend(extra_args)

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=PROJECT_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        t_out = threading.Thread(
            target=_stream_reader,
            args=(proc.stdout, stdout_lines, script),
            daemon=True,
        )
        t_err = threading.Thread(
            target=_stream_reader,
            args=(proc.stderr, stderr_lines, f"{script}!"),
            daemon=True,
        )
        t_out.start()
        t_err.start()

        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            t_out.join(timeout=2)
            t_err.join(timeout=2)
            return False, f"Timeout: {script} tardó más de {timeout}s"

        t_out.join(timeout=5)
        t_err.join(timeout=5)

        print(f"  [{script}] returncode={proc.returncode}", flush=True)

        if proc.returncode == 0:
            return True, ""

        error = "\n".join(stderr_lines[-50:]) or "\n".join(stdout_lines[-50:]) or "sin output"
        return False, error[-1500:]

    except Exception as e:
        return False, f"Excepción lanzando {script}: {e}"


# ─────────────────────────────────────────────────────────────
# Comandos
# ─────────────────────────────────────────────────────────────
MENU = (
    "🤖 <b>Bot de CVs — Comandos</b>\n\n"
    "/scrape — Pipeline completo desde cero (5-10 min)\n"
    "/refresh — Solo recalcular matches (~1 min)\n"
    "/last — Reenviar la última lista\n"
    "/status — ¿Estoy procesando algo?\n"
    "/help — Mostrar este menú\n\n"
    "💡 Después de recibir la lista, respondé con los números:\n"
    "<code>4</code>  o  <code>4,7,8</code>\n"
    "(separados por coma, sin espacios)"
)


def cmd_help():
    send_message(MENU)


def cmd_status():
    if not state["busy"]:
        send_message("✅ <b>Libre.</b> Mandame un comando.")
        return
    elapsed = (datetime.now() - state["started_at"]).total_seconds()
    mins, secs = divmod(int(elapsed), 60)
    send_message(
        f"⏳ <b>Procesando:</b> <code>{state['task']}</code>\n"
        f"Hace {mins}m {secs}s.\n"
        f"Esperá a que termine."
    )


def cmd_last():
    matches_file = DATA_DIR / "top_matches_full.csv"
    if not matches_file.exists():
        send_message("❌ No hay lista previa. Mandá /scrape primero.")
        return

    state["busy"] = True
    state["task"] = "last"
    state["started_at"] = datetime.now()
    try:
        ok, err = run_script("bot_daily.py", timeout=60)
        if not ok:
            send_message(f"❌ Error reenviando:\n<code>{err}</code>")
    finally:
        state["busy"] = False
        state["task"] = None


def cmd_scrape(confirmed: bool):
    if not confirmed:
        state["awaiting_scrape_confirm"] = True
        send_message(
            "⚠️ <b>/scrape</b> va a:\n"
            "• Borrar todos los datos viejos\n"
            "• Re-scrapear Computrabajo (~2 min)\n"
            "• Re-enriquecer con IA (~1-2 min)\n"
            "• Re-matchear y mandar nueva lista\n\n"
            "Total estimado: 5-10 min.\n\n"
            "Confirmá con <code>/scrape ok</code> para arrancar, "
            "o ignorá este mensaje."
        )
        return

    state["awaiting_scrape_confirm"] = False
    state["busy"] = True
    state["task"] = "scrape"
    state["started_at"] = datetime.now()

    try:
        send_message("🗑️ Borrando datos viejos...")
        for fname in FILES_TO_RESET:
            f = DATA_DIR / fname
            if f.exists():
                f.unlink()
                print(f"[reset] borrado: {f.name}")

        run_pipeline(SCRAPE_FULL, label="scrape")

    finally:
        state["busy"] = False
        state["task"] = None


def cmd_refresh():
    state["busy"] = True
    state["task"] = "refresh"
    state["started_at"] = datetime.now()
    try:
        if not (DATA_DIR / "computrabajo_enriched.csv").exists():
            send_message("❌ No hay datos enriched. Mandá /scrape primero.")
            return
        run_pipeline(REFRESH, label="refresh")
    finally:
        state["busy"] = False
        state["task"] = None


def run_pipeline(steps: list[tuple[str, str, int]], label: str):
    """Corre una secuencia de scripts, notificando por Telegram en cada paso."""
    total = len(steps)
    started = time.time()

    for i, (msg, script, timeout) in enumerate(steps, 1):
        send_message(f"🔄 <b>Paso {i}/{total}</b>\n{msg}")
        print(f"\n{'=' * 60}\n  [{i}/{total}] {script}  (timeout={timeout}s)\n{'=' * 60}")

        step_start = time.time()
        ok, err = run_script(script, timeout=timeout)
        elapsed = time.time() - step_start

        if not ok:
            send_message(
                f"❌ <b>Falló en paso {i}/{total}</b> ({script})\n"
                f"<code>{err[-800:]}</code>\n\n"
                f"Pipeline abortado."
            )
            return

        print(f"  ✓ {script} OK en {elapsed:.1f}s")

    total_elapsed = time.time() - started
    mins, secs = divmod(int(total_elapsed), 60)
    send_message(f"🎉 <b>{label.title()} completo</b> en {mins}m {secs}s.")


# ─────────────────────────────────────────────────────────────
# Generación de CVs
# ─────────────────────────────────────────────────────────────
def parse_indices(text: str) -> str | None:
    cleaned = text.replace(" ", "")
    if not cleaned:
        return None
    parts = cleaned.split(",")
    if not all(p.isdigit() for p in parts):
        return None
    return ",".join(parts)


def _load_job_urls(indices: str) -> dict:
    """Devuelve {n: {title, company, url}} para cada índice seleccionado (n es 1-based)."""
    import traceback
    matches_file = DATA_DIR / "top_matches_full.csv"

    if not matches_file.exists():
        print("[job_urls] top_matches_full.csv no existe")
        return {}
    try:
        import pandas as pd
        df = pd.read_csv(matches_file, encoding="utf-8")
        print(f"[job_urls] {len(df)} filas | cols: {df.columns.tolist()}")

        selected = [int(i) for i in indices.split(",") if i.strip().isdigit()]
        print(f"[job_urls] índices pedidos: {selected}")

        result = {}
        for n, idx in enumerate(selected, 1):
            if not (0 <= idx < len(df)):
                print(f"[job_urls] idx={idx} fuera de rango")
                continue
            row = df.iloc[idx]
            url = str(row["url"]).strip() if "url" in df.columns else ""
            url = url if url.startswith("http") else ""
            result[n] = {
                "title":   str(row["title"])   if "title"   in df.columns else "",
                "company": str(row["company"]) if "company" in df.columns else "",
                "url":     url,
            }
            print(f"[job_urls] n={n} idx={idx} → '{result[n]['title'][:40]}' | {url[:60]}")

        return result

    except Exception:
        print(f"[ERROR job_urls]\n{traceback.format_exc()}")
        return {}


def cmd_generate_cvs(indices: str):
    state["busy"] = True
    state["task"] = "cvs"
    state["started_at"] = datetime.now()
    try:
        send_message(
            f"🚀 <b>Generando CVs para los puestos {indices}...</b>\n"
            f"Esto tarda 1-2 minutos por CV."
        )

        CVS_DIR.mkdir(parents=True, exist_ok=True)
        for old in CVS_DIR.glob("*.docx"):
            old.unlink()

        ok, err = run_script("cv_adapter.py", timeout=600, extra_args=["--indices", indices])
        if not ok:
            send_message(f"❌ Error generando CVs:\n<code>{err}</code>")
            return

        cvs = sorted(CVS_DIR.glob("CV_Marcos_*.docx"))
        if not cvs:
            send_message("⚠️ cv_adapter terminó OK pero no encontré CVs generados.")
            return

        job_info = _load_job_urls(indices)
        send_message(f"✅ <b>{len(cvs)} CV(s) generados.</b>")

        for n, cv in enumerate(cvs, 1):
            job = job_info.get(n, {})
            title   = job.get("title", cv.stem)
            company = job.get("company", "")
            url     = job.get("url", "")

            caption = f"📄 {title}" + (f" @ {company}" if company else "")
            send_document(cv, caption=caption)

            if url:
                send_message(f"🔗 <b>Aplicar:</b> {url}")

        send_message("🎉 <b>¡Listo!</b> Revisá los CVs y aplicá.")

    finally:
        state["busy"] = False
        state["task"] = None


# ─────────────────────────────────────────────────────────────
# Router de mensajes
# ─────────────────────────────────────────────────────────────
def handle_message(text: str, from_chat_id: str):
    if str(from_chat_id) != str(CHAT_ID):
        print(f"[ignorado] chat ajeno: {from_chat_id}")
        return

    text  = text.strip()
    lower = text.lower()
    print(f"[handle] {text!r}")

    if lower in ("/start", "/help"):
        cmd_help()
        return

    if lower == "/status":
        cmd_status()
        return

    if lower.startswith("/scrape"):
        if state["busy"]:
            send_message(f"⏳ Ya estoy procesando <code>{state['task']}</code>. Mandá /status.")
            return
        cmd_scrape(confirmed=(lower == "/scrape ok"))
        return

    if lower == "/refresh":
        if state["busy"]:
            send_message(f"⏳ Ya estoy procesando <code>{state['task']}</code>. Mandá /status.")
            return
        cmd_refresh()
        return

    if lower == "/last":
        if state["busy"]:
            send_message(f"⏳ Ya estoy procesando <code>{state['task']}</code>. Mandá /status.")
            return
        cmd_last()
        return

    indices = parse_indices(text)
    if indices is not None:
        if state["busy"]:
            send_message(f"⏳ Ya estoy procesando <code>{state['task']}</code>. Esperá a que termine.")
            return
        cmd_generate_cvs(indices)
        return

    send_message(f"❓ No entendí: <code>{text[:50]}</code>\nMandá /help para ver los comandos.")


# ─────────────────────────────────────────────────────────────
# Loop principal
# ─────────────────────────────────────────────────────────────
def main():
    if not TOKEN or not CHAT_ID:
        print("[FATAL] Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en .env")
        sys.exit(1)

    acquire_lock()  # Muere aquí si ya hay otra instancia viva

    for attempt in range(10):
        try:
            me = requests.get(f"{BASE_URL}/getMe", timeout=10).json()
            if not me.get("ok"):
                print(f"[FATAL] Token invalido: {me}")
                sys.exit(1)
            print(f"Bot conectado: @{me['result']['username']}")
            break
        except Exception as e:
            if attempt < 9:
                print(f"[WARN] Sin conexion a Telegram (intento {attempt+1}/10): {e}")
                time.sleep(30)
            else:
                print(f"[FATAL] No pude contactar Telegram despues de 10 intentos.")
                sys.exit(1)

    offset = load_offset()
    print("=" * 50)
    print("  BOT LISTENER - CV GENERATOR")
    print("=" * 50)
    print(f"PID:     {os.getpid()}  (lock: {LOCK_FILE.name})")
    print(f"Chat ID: {CHAT_ID}")
    print(f"Offset:  {offset}")
    print("Comandos: /scrape /refresh /last /status /help")
    print("(Ctrl+C para detener)\n")

    send_message("🟢 <b>Bot arrancado.</b> Mandá /help para ver los comandos.")

    while True:
        try:
            r = requests.get(
                f"{BASE_URL}/getUpdates",
                params={"offset": offset, "timeout": POLL_TIMEOUT},
                timeout=POLL_TIMEOUT + 10,
            )
            data = r.json()

            if not data.get("ok"):
                print(f"[getUpdates ERROR] {data}")
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                save_offset(offset)

                msg = update.get("message")
                if not msg:
                    continue

                text          = msg.get("text", "")
                from_chat_id  = msg.get("chat", {}).get("id", "")
                print(f"[recibido] chat={from_chat_id} text={text!r}")
                handle_message(text, from_chat_id)

        except requests.exceptions.ReadTimeout:
            continue
        except KeyboardInterrupt:
            print("\n[Listener] Detenido por el usuario.")
            send_message("🔴 <b>Bot detenido.</b>")
            break
        except Exception as e:
            print(f"[loop ERROR] {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
