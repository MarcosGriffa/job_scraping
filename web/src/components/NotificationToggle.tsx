"use client";

import { useEffect, useState } from "react";
import { IconMail } from "./illustrations/icons";

/**
 * Interruptor de avisos por mail — opt-in, apagado por defecto (ver
 * notificaciones_semanales.py). Se ofrece acá, en /resultados, porque es
 * donde tiene sentido: recién después de ver que el matching funciona es
 * cuando vale la pena ofrecer "avisame si aparece algo nuevo".
 */
export function NotificationToggle() {
  const [activas, setActivas] = useState<boolean | null>(null); // null = cargando
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/notifications")
      .then((r) => r.json())
      .then((d) => setActivas(Boolean(d.activas)))
      .catch(() => setActivas(false));
  }, []);

  async function cambiar(nuevoValor: boolean) {
    setGuardando(true);
    setError(null);
    const anterior = activas;
    setActivas(nuevoValor); // optimista
    try {
      const res = await fetch("/api/notifications", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ activas: nuevoValor }),
      });
      if (!res.ok) throw new Error();
    } catch {
      setActivas(anterior); // revertir si falló
      setError("No se pudo guardar. Probá de nuevo.");
    } finally {
      setGuardando(false);
    }
  }

  if (activas === null) return null; // evita el "flash" mientras carga

  return (
    <label className="mt-6 flex items-center gap-3 rounded-2xl border border-brown-title/10 bg-white px-4 py-3 text-sm">
      <IconMail className="h-5 w-5 shrink-0 text-olive" />
      <span className="flex-1 font-semibold text-brown-title">
        Avisame por mail cuando aparezcan matches nuevos
      </span>
      <input
        type="checkbox"
        checked={activas}
        disabled={guardando}
        onChange={(e) => cambiar(e.target.checked)}
        className="h-5 w-5 shrink-0 rounded-md accent-olive disabled:opacity-50"
      />
      {error && <span className="w-full text-xs font-semibold text-terracota-dark">{error}</span>}
    </label>
  );
}
