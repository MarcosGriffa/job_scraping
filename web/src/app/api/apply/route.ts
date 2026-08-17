import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "@/lib/config";

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => null);
  if (!body?.job_id) {
    return NextResponse.json({ error: "Falta job_id." }, { status: 400 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${FASTAPI_URL}/api/jobs/apply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: body.user_id || "default",
        job_id: body.job_id,
        applied: body.applied ?? true,
      }),
    });
  } catch {
    return NextResponse.json(
      { error: "No se pudo conectar con el motor de matching. ¿Está corriendo el backend (api/main.py)?" },
      { status: 502 }
    );
  }

  const data = await upstream.json().catch(() => null);
  if (!upstream.ok) {
    return NextResponse.json({ error: data?.detail || "Error al guardar el cambio." }, { status: upstream.status });
  }

  return NextResponse.json(data);
}
