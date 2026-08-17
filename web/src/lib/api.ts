import type { MatchRunResponse } from "./types";
import { getUserId } from "./userId";

/** Sube el CV y corre todo el pipeline. Puede tardar 1-2 minutos. */
export async function uploadCvAndMatch(file: File): Promise<MatchRunResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("user_id", getUserId());

  const res = await fetch("/api/upload", { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error || "No pudimos procesar tu CV. Probá de nuevo en un rato.");
  }
  return res.json();
}

/** Trae la última corrida de matching guardada para este navegador. */
export async function getLatestResults(): Promise<MatchRunResponse | null> {
  const res = await fetch(`/api/results?user_id=${encodeURIComponent(getUserId())}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("No pudimos traer tus resultados.");
  return res.json();
}

/** Marca (o desmarca) una oferta como aplicada. */
export async function setApplied(jobId: string, applied: boolean): Promise<void> {
  const res = await fetch("/api/apply", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: getUserId(), job_id: jobId, applied }),
  });
  if (!res.ok) throw new Error("No pudimos guardar el cambio. Probá de nuevo.");
}
