import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "@/lib/config";
import { getAccessToken } from "@/lib/supabase/server";

// Interruptor de avisos por mail (opt-in, apagado por defecto — ver
// notificaciones_semanales.py). GET trae el estado actual, POST lo cambia.

export async function GET() {
  const token = await getAccessToken();
  if (!token) {
    return NextResponse.json({ error: "Iniciá sesión para ver esto." }, { status: 401 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${FASTAPI_URL}/api/notifications/settings`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch {
    return NextResponse.json(
      { error: "No se pudo conectar con el motor. ¿Está corriendo el backend (api/main.py)?" },
      { status: 502 }
    );
  }

  const data = await upstream.json().catch(() => null);
  if (!upstream.ok) {
    return NextResponse.json({ error: data?.detail || "Error al traer la configuración." }, { status: upstream.status });
  }
  return NextResponse.json(data);
}

export async function POST(request: NextRequest) {
  const token = await getAccessToken();
  if (!token) {
    return NextResponse.json({ error: "Iniciá sesión para hacer esto." }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  if (typeof body?.activas !== "boolean") {
    return NextResponse.json({ error: "Falta 'activas' (true/false)." }, { status: 400 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${FASTAPI_URL}/api/notifications/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ activas: body.activas }),
    });
  } catch {
    return NextResponse.json(
      { error: "No se pudo conectar con el motor. ¿Está corriendo el backend (api/main.py)?" },
      { status: 502 }
    );
  }

  const data = await upstream.json().catch(() => null);
  if (!upstream.ok) {
    return NextResponse.json({ error: data?.detail || "Error al guardar el cambio." }, { status: upstream.status });
  }
  return NextResponse.json(data);
}
