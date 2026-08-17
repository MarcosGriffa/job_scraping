import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "@/lib/config";

export async function GET(request: NextRequest) {
  const userId = request.nextUrl.searchParams.get("user_id") || "default";

  let upstream: Response;
  try {
    upstream = await fetch(`${FASTAPI_URL}/api/match/latest?user_id=${encodeURIComponent(userId)}`, {
      cache: "no-store",
    });
  } catch {
    return NextResponse.json(
      { error: "No se pudo conectar con el motor de matching. ¿Está corriendo el backend (api/main.py)?" },
      { status: 502 }
    );
  }

  if (upstream.status === 404) {
    return NextResponse.json({ error: "Todavía no hay resultados." }, { status: 404 });
  }

  const data = await upstream.json().catch(() => null);
  if (!upstream.ok) {
    return NextResponse.json({ error: data?.detail || "Error al traer resultados." }, { status: upstream.status });
  }

  return NextResponse.json(data);
}
