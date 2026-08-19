"""
emailer.py — Envío del resumen semanal de matches nuevos, con Resend.

Por qué Resend: tiene un plan gratis generoso (3.000 mails/mes) y se puede
mandar sin tener un dominio propio todavía (usa su dominio de prueba,
resend.dev) — el día que haya un dominio real, cambia con una variable de
entorno, sin tocar código. Ver la comparación completa en la conversación
del 19/08/2026.

Necesita RESEND_API_KEY en el .env (o en las variables de entorno de
donde corra notificaciones_semanales.py — ver ese archivo y el workflow
de GitHub Actions). Sin esa clave, no rompe nada del resto del sitio —
solo esta función puntual falla, con un error claro.
"""

from __future__ import annotations

import os

import resend

REMITENTE = os.getenv("RESEND_FROM_EMAIL", "EmpatÍA | NextStep <onboarding@resend.dev>")
SITIO_URL = os.getenv("SITE_URL", "https://jobscraping.vercel.app")

_configurado = False


def _asegurar_configurado() -> None:
    global _configurado
    if _configurado:
        return
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta RESEND_API_KEY en el .env — sacá una gratis en resend.com "
            "(no hace falta dominio propio para empezar, ver emailer.py)."
        )
    resend.api_key = api_key
    _configurado = True


def _fila_oferta_html(oferta: dict) -> str:
    """Una oferta, como fila de la tabla del mail. HTML con estilos en
    línea a propósito — los clientes de mail no leen bien las hojas de
    estilo aparte, ni las clases de Tailwind del resto del sitio."""
    titulo = oferta.get("title", "Oferta")
    empresa = oferta.get("company", "")
    ubicacion = oferta.get("location", "")
    score = oferta.get("score")
    url = oferta.get("url", SITIO_URL)
    return f"""
    <tr>
      <td style="padding:16px 0;border-bottom:1px solid #e8ddd0;">
        <p style="margin:0;font-weight:700;color:#3a2e22;font-size:16px;">{titulo}</p>
        <p style="margin:4px 0 0;color:#6b5d4f;font-size:14px;">{empresa}{' · ' + ubicacion if ubicacion else ''}</p>
        {f'<p style="margin:6px 0 0;color:#3a2e22;font-size:14px;"><strong>Compatibilidad:</strong> {score}/100</p>' if score is not None else ''}
        <a href="{url}" style="display:inline-block;margin-top:10px;color:#c1652f;font-weight:700;text-decoration:none;font-size:14px;">Ver aviso →</a>
      </td>
    </tr>
    """


def enviar_resumen_semanal(destinatario_mail: str, nombre: str | None, ofertas_nuevas: list[dict]) -> None:
    """Manda el mail con las ofertas nuevas de esta semana. No llamar con
    una lista vacía — el llamador (notificaciones_semanales.py) ya filtra
    antes: si no hay nada nuevo, no se manda nada."""
    if not ofertas_nuevas:
        raise ValueError("enviar_resumen_semanal() no se llama con la lista vacía — filtrar antes.")

    _asegurar_configurado()

    saludo = f"Hola {nombre.split(' ')[0]}," if nombre else "Hola,"
    cantidad = len(ofertas_nuevas)
    plural = "s" if cantidad != 1 else ""

    filas = "".join(_fila_oferta_html(o) for o in ofertas_nuevas)

    html = f"""
    <div style="max-width:560px;margin:0 auto;padding:32px 24px;font-family:sans-serif;background:#fdf6ec;">
      <p style="color:#3a2e22;font-size:16px;">{saludo}</p>
      <p style="color:#3a2e22;font-size:16px;">
        Encontramos <strong>{cantidad} oferta{plural} nueva{plural}</strong> que matchea con tu perfil
        desde la última vez.
      </p>
      <table style="width:100%;border-collapse:collapse;margin-top:8px;">
        {filas}
      </table>
      <p style="margin-top:28px;">
        <a href="{SITIO_URL}/resultados" style="display:inline-block;background:#c1652f;color:#fff;padding:12px 24px;border-radius:999px;font-weight:700;text-decoration:none;font-size:14px;">
          Ver todos tus resultados
        </a>
      </p>
      <p style="margin-top:32px;color:#9c8f7f;font-size:12px;">
        Te llega esto porque activaste los avisos por mail en tu cuenta de EmpatÍA | NextStep.
        Podés desactivarlos cuando quieras desde tus resultados.
      </p>
    </div>
    """

    resend.Emails.send({
        "from": REMITENTE,
        "to": destinatario_mail,
        "subject": f"{cantidad} oferta{plural} nueva{plural} que matchea con vos",
        "html": html,
    })
