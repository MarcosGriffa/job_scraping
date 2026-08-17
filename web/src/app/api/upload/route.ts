import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "@/lib/config";

// Corre el pipeline completo (clasificar CV + buscar en portales + matchear
// con IA) — puede tardar 1-2 minutos. No le ponemos límite de tiempo propio,
// dejamos que corra lo que tenga que correr en desarrollo local.
export const maxDuration = 300;

export async function POST(request: NextRequest) {
  let incoming: FormData;
  try {
    incoming = await request.formData();
  } catch {
    return NextResponse.json({ error: "No se pudo leer el archivo enviado." }, { status: 400 });
  }

  const file = incoming.get("file");
  const userId = (incoming.get("user_id") as string) || "default";

  if (!(file instanceof Blob)) {
    return NextResponse.json({ error: "Falta el archivo del CV." }, { status: 400 });
  }

  const forward = new FormData();
  const filename = file instanceof File ? file.name : "cv.pdf";
  forward.append("file", file, filename);
  forward.append("user_id", userId);

  let upstream: Response;
  try {
    upstream = await fetch(`${FASTAPI_URL}/api/match`, { method: "POST", body: forward });
  } catch {
    return NextResponse.json(
      { error: "No se pudo conectar con el motor de matching. ¿Está corriendo el backend (api/main.py)?" },
      { status: 502 }
    );
  }

  const data = await upstream.json().catch(() => null);
  if (!upstream.ok) {
    return NextResponse.json(
      { error: data?.detail || "El motor de matching devolvió un error." },
      { status: upstream.status }
    );
  }

  return NextResponse.json(data);
}
