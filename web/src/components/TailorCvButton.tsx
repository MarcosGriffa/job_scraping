"use client";

import { useState } from "react";
import { getUserId } from "@/lib/userId";
import { IconUpload } from "./illustrations/icons";

/**
 * Botón "Generar CV para esta oferta".
 *
 * Nada se genera automáticamente: recién cuando la persona aprieta acá se
 * arma el CV adaptado a ESA oferta puntual (unos segundos). El backend lo
 * deja cacheado, así que si lo vuelve a pedir sale al instante.
 */
export function TailorCvButton({ jobId }: { jobId: string }) {
  const [estado, setEstado] = useState<"listo" | "generando">("listo");
  const [error, setError] = useState<string | null>(null);

  async function generar() {
    setEstado("generando");
    setError(null);
    try {
      const res = await fetch(
        `/api/cv-tailor?user_id=${encodeURIComponent(getUserId())}&job_id=${encodeURIComponent(jobId)}`
      );
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.error || "No se pudo generar el CV.");
      }

      // Nombre de archivo que eligió el backend (Content-Disposition)
      const disp = res.headers.get("content-disposition") || "";
      const match = disp.match(/filename\*?=(?:UTF-8''|")?([^";]+)/i);
      const filename = match ? decodeURIComponent(match[1].replace(/"$/, "")) : "CV_adaptado.docx";

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo generar el CV.");
    } finally {
      setEstado("listo");
    }
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <button
        type="button"
        onClick={generar}
        disabled={estado === "generando"}
        className="inline-flex items-center gap-2 rounded-full border-2 border-olive px-4 py-2 text-sm font-bold text-olive transition-colors hover:bg-olive hover:text-white disabled:cursor-wait disabled:opacity-60"
      >
        {estado === "generando" ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-olive border-t-transparent" />
            Generando…
          </>
        ) : (
          <>
            <IconUpload className="h-4 w-4 rotate-180" />
            Generar CV para esta oferta
          </>
        )}
      </button>
      {error && <span className="text-xs font-semibold text-terracota-dark">{error}</span>}
    </div>
  );
}
