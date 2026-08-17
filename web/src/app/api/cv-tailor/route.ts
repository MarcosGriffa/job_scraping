import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "@/lib/config";

// Generar el CV adaptado tarda unos segundos (una llamada a la IA), no los
// minutos del matching completo — pero le damos margen por las dudas.
export const maxDuration = 120;

export async function GET(request: NextRequest) {
  const userId = request.nextUrl.searchParams.get("user_id") || "default";
  const jobId = request.nextUrl.searchParams.get("job_id") || "";

  if (!jobId) {
    return NextResponse.json({ error: "Falta job_id." }, { status: 400 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(
      `${FASTAPI_URL}/api/cv/tailor?user_id=${encodeURIComponent(userId)}&job_id=${encodeURIComponent(jobId)}`,
      { cache: "no-store" }
    );
  } catch {
    return NextResponse.json(
      { error: "No se pudo conectar con el motor. ¿Está corriendo el backend (api/main.py)?" },
      { status: 502 }
    );
  }

  if (!upstream.ok) {
    const data = await upstream.json().catch(() => null);
    return NextResponse.json(
      { error: data?.detail || "No se pudo generar el CV adaptado." },
      { status: upstream.status }
    );
  }

  // Reenviamos el archivo tal cual, conservando el nombre de descarga que
  // eligió el backend (viene en Content-Disposition).
  return new NextResponse(upstream.body, {
    status: 200,
    headers: {
      "Content-Type":
        upstream.headers.get("content-type") ??
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "Content-Disposition": upstream.headers.get("content-disposition") ?? "attachment",
    },
  });
}
