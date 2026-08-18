import { NextResponse } from "next/server";
import { FASTAPI_URL } from "@/lib/config";
import { getAccessToken } from "@/lib/supabase/server";

// La usan dos lugares con expectativas distintas:
//   - /resultados (requiere sesión, ya la garantiza proxy.ts)
//   - FeaturedJobs.tsx en la landing (sin cuenta también es válido — ahí
//     "sin sesión" simplemente quiere decir "mostrame los ejemplos", no es
//     un error). Por eso, sin sesión, devolvemos 404 derecho (mismo
//     resultado que "todavía no hay resultados") en vez de 401 — el
//     llamador ya sabe manejar el 404.
export async function GET() {
  const token = await getAccessToken();
  if (!token) {
    return NextResponse.json({ error: "Todavía no hay resultados." }, { status: 404 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${FASTAPI_URL}/api/match/latest`, {
      cache: "no-store",
      headers: { Authorization: `Bearer ${token}` },
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
