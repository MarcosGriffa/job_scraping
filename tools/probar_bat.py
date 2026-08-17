"""Simula la ejecucion real de INICIAR_WEB.bat con cmd.exe.

No se puede probar el .bat tal cual sin pantalla: 'start ... cmd /k' abre
ventanas nuevas, y sin escritorio no arrancan. Pero eso NO es lo que se
rompio -- lo que se rompio fue el PARSEO del archivo (lineas partidas,
comandos ejecutados por pedazos).

Entonces: se hace una copia identica donde solo se neutraliza lo que
necesita pantalla (abrir ventanas, pause, timeout) y se corre esa copia
con cmd.exe REAL. Si el parseo esta bien, no aparece ningun
"no se reconoce" y el flujo llega hasta el final por el camino correcto.
"""

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGINAL = RAIZ / "INICIAR_WEB.bat"
COPIA = RAIZ / "_test_iniciar_web.bat"

texto = ORIGINAL.read_text(encoding="ascii")

# Neutralizar SOLO lo que exige una pantalla interactiva
reemplazos = [
    (r'start "EmpatIA - MOTOR \(no cerrar\)" cmd /k ', "echo [SIMULADO] MOTOR ejecutaria: "),
    (r'start "EmpatIA - WEB \(no cerrar\)" cmd /k ', "echo [SIMULADO] WEB ejecutaria: "),
    (r"start http://localhost:3000", "echo [SIMULADO] abriria el navegador"),
    # sin servidores levantados, cortar la espera enseguida
    (r"if %INTENTOS% GEQ 45", "if %INTENTOS% GEQ 2"),
    # 'pause' y 'timeout' cuelgan o fallan sin consola interactiva
    (r"^pause$", "echo [SIMULADO] pause"),
    (r"^timeout /t \d+ /nobreak > nul$", "echo [SIMULADO] espera"),
    (r"^    timeout /t \d+ /nobreak > nul$", "echo [SIMULADO] espera"),
]
for patron, nuevo in reemplazos:
    texto = re.sub(patron, nuevo, texto, flags=re.MULTILINE)

COPIA.write_text(texto, encoding="ascii", newline="\r\n")

try:
    proc = subprocess.run(
        ["cmd", "/c", str(COPIA)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        cwd=str(RAIZ),
    )
    salida = (proc.stdout or "") + (proc.stderr or "")
finally:
    COPIA.unlink(missing_ok=True)

print("=" * 62)
print("SALIDA DE cmd.exe")
print("=" * 62)
print(salida.strip())
print("=" * 62)

# ---- Veredicto ----
errores_parseo = [
    ln for ln in salida.splitlines()
    if "no se reconoce" in ln.lower()
    or "is not recognized" in ln.lower()
    or "no esperado" in ln.lower()
    or "unexpected" in ln.lower()
    or "sintaxis" in ln.lower()
]

print()
print("VEREDICTO")
print(f"  errores de parseo            : {len(errores_parseo)}")
for e in errores_parseo[:8]:
    print(f"      {e.strip()[:78]}")
print(f"  detecto Python correctamente : {'[ERROR] No encuentro Python' not in salida}")
print(f"  detecto Node correctamente   : {'[ERROR] No encuentro Node' not in salida}")
print(f"  encontro el .env             : {'[ERROR] Falta el archivo .env' not in salida}")
print(f"  llego a lanzar el MOTOR      : {'[SIMULADO] MOTOR ejecutaria' in salida}")
print(f"  llego a lanzar la WEB        : {'[SIMULADO] WEB ejecutaria' in salida}")

ok = (
    not errores_parseo
    and "[ERROR]" not in salida
    and "[SIMULADO] MOTOR ejecutaria" in salida
    and "[SIMULADO] WEB ejecutaria" in salida
)
print()
print("RESULTADO:", "OK - el .bat se parsea y ejecuta bien" if ok else "FALLA - revisar arriba")
sys.exit(0 if ok else 1)
