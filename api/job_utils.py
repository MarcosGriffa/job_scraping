"""job_utils.py — helpers chicos compartidos por matching.py y main.py."""

from __future__ import annotations

import hashlib
import re


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def make_job_id(job: dict) -> str:
    """ID estable para una oferta, para poder marcarla como 'aplicada' y
    reconocerla en corridas futuras. Se basa en la URL (si existe) o si no
    en título+empresa+fuente normalizados — mismo criterio de "misma oferta"
    que ya usa pipeline.py para deduplicar."""
    url = (job.get("url") or "").strip()
    basis = url if url else f"{_normalize(job.get('title'))}::{_normalize(job.get('company'))}::{job.get('source', '')}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]
