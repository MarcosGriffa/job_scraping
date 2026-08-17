"""
rate_limit.py — Freno contra abuso de las búsquedas.

Una búsqueda completa es cara: scrapea 6 portales, gasta cupo de Jooble
(500 consultas de por vida en el plan gratis) y hace ~11 llamadas a la IA.
Con el sitio publicado, cualquiera puede dispararlas. Sin un freno, un
puñado de visitantes puede quemar los cupos de todos.

Dos controles, que tapan agujeros distintos:

  1. LIMITE DIARIO (2 por día). Se cuenta sobre la tabla match_results,
     que ya existe: cuántas búsquedas completó esa persona en las últimas
     24 horas. Se eligió contar ahí en vez de crear una tabla nueva porque
     así el límite vive en la base y sobrevive a los reinicios del
     servidor — importante, porque los hostings gratuitos borran el disco
     cada vez que reinician.

  2. UNA A LA VEZ (en memoria). El control de arriba cuenta búsquedas ya
     TERMINADAS, así que no frena a alguien que dispare diez pedidos a la
     vez antes de que termine la primera. Este segundo control marca al
     usuario como "ocupado" mientras su búsqueda corre.

Limitación conocida y aceptada: el control 2 vive en la memoria del
proceso. Si algún día el motor corre en varias máquinas a la vez, cada una
tendría su propia lista. Para el volumen de hoy (una sola máquina) alcanza;
si eso cambia, hay que moverlo a la base.

La identidad es el id anónimo de la cookie del navegador, igual que el
resto del sistema. No es infalible — quien borre las cookies arranca de
cero — pero frena el abuso casual, que es lo que buscamos. Cuando existan
las cuentas reales (Fase 3), el límite pasa a colgar del usuario real y se
vuelve mucho más firme.
"""

from __future__ import annotations

import threading

from . import storage

BUSQUEDAS_POR_DIA = 2
VENTANA_HORAS = 24

# user_ids con una búsqueda corriendo AHORA
_en_curso: set[str] = set()
_lock = threading.Lock()


class LimiteAlcanzado(Exception):
    """Se pasó del límite. El mensaje va tal cual a la pantalla del usuario."""


def verificar_y_reservar(user_id: str) -> None:
    """Deja pasar o levanta LimiteAlcanzado. Si deja pasar, marca al usuario
    como ocupado — hay que llamar a `liberar()` al terminar, pase lo que pase."""
    user_id = user_id or storage.DEFAULT_USER_ID

    with _lock:
        if user_id in _en_curso:
            raise LimiteAlcanzado(
                "Ya tenés una búsqueda en curso. Esperá a que termine "
                "(tarda entre 1 y 3 minutos) antes de empezar otra."
            )

    try:
        hechas = storage.count_recent_runs(user_id, hours=VENTANA_HORAS)
    except Exception:
        # Si la base falla, no bloqueamos a la persona por un problema nuestro.
        hechas = 0

    if hechas >= BUSQUEDAS_POR_DIA:
        raise LimiteAlcanzado(
            f"Llegaste al límite de {BUSQUEDAS_POR_DIA} búsquedas por día. "
            "Podés volver a buscar mañana. Mientras tanto, tus resultados "
            "anteriores siguen disponibles y podés seguir generando CVs "
            "adaptados para esas ofertas."
        )

    with _lock:
        _en_curso.add(user_id)


def liberar(user_id: str) -> None:
    """Marca que la búsqueda de este usuario terminó (haya salido bien o mal)."""
    with _lock:
        _en_curso.discard(user_id or storage.DEFAULT_USER_ID)
