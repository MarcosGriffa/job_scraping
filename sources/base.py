"""
sources/base.py — Interfaz común para todas las fuentes de empleo.

Cada fuente (Computrabajo, RemoteOK, etc.) implementa la clase JobSource
y su método search(). Así el pipeline principal no necesita saber nada
sobre cómo scrapea o consulta cada portal — solo le pide una lista de
ofertas ya normalizadas.

Esquema normalizado de una oferta (dict):
{
    "source":      "computrabajo" | "remoteok" | ...,
    "title":       str,
    "company":     str,
    "location":    str,   # ciudad/país o "Remoto"
    "modality":    str,   # "remoto" | "hibrido" | "presencial" | ""
    "description": str,   # texto completo si está disponible, sino snippet
    "url":         str,
    "posted_at":   str,   # fecha como texto, formato variable según fuente
    "scraped_at":  str,   # ISO timestamp de cuándo se obtuvo
}
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def normalize_job(
    source: str,
    title: str,
    company: str = "",
    location: str = "",
    modality: str = "",
    description: str = "",
    url: str = "",
    posted_at: str = "",
) -> dict:
    """Arma un dict de oferta con el esquema normalizado, rellenando lo que falte."""
    return {
        "source": source,
        "title": (title or "").strip(),
        "company": (company or "").strip(),
        "location": (location or "").strip(),
        "modality": (modality or "").strip().lower(),
        "description": (description or "").strip(),
        "url": (url or "").strip(),
        "posted_at": (posted_at or "").strip(),
        "scraped_at": now_iso(),
    }


class JobSource(ABC):
    """Clase base que toda fuente de empleo debe implementar."""

    #: nombre corto de la fuente, usado en logs y en el campo "source"
    name: str = "base"

    #: True si esta fuente es específica de tecnología/IT (se activa solo
    #: cuando el clasificador de CV detecta que el área es tech).
    is_tech_vertical: bool = False

    @abstractmethod
    def search(self, query: str, max_results: int = 25) -> list[dict]:
        """
        Busca ofertas para un término de búsqueda dado.
        Devuelve una lista de dicts con el esquema normalizado (ver normalize_job).
        Nunca debería levantar una excepción hacia afuera: si algo falla,
        loguea el error y devuelve [] para no tumbar el resto del pipeline.
        """
        raise NotImplementedError
