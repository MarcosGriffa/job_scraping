// /auth/callback — adonde Supabase manda de vuelta a la persona después de
// confirmar el mail (registro con contraseña) o de volver de Google. Los
// dos casos terminan acá con el mismo parámetro `code`, que se canjea por
// una sesión real.
//
// Acá también, y SOLO acá, se dispara la migración de datos anónimos (ver
// api/main.py POST /api/account/claim). Por qué acá y no en el formulario
// de registro: con la confirmación de mail activada, mandar el formulario
// todavía no da una sesión — recién existe cuando se confirma. Y con
// Google, alta y login son el mismo botón, así que no hay un "momento de
// registro" separado para engancharse. La señal que sí sirve para los dos
// casos: comparar created_at vs last_sign_in_at del usuario recién
// autenticado — si están pegados en el tiempo, es la primera vez que esta
// cuenta inicia sesión en su vida, o sea que es un alta. En un login
// normal, created_at queda viejo y last_sign_in_at es ahora: no migra
// nada, tal como pidió Marcos ("nunca en un login, para no pisar datos en
// compus compartidas").
import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { ANON_COOKIE_KEY } from "@/lib/userId";

const UMBRAL_ALTA_NUEVA_MS = 10_000; // 10s: alcanza y sobra para distinguir alta de login

export async function GET(request: NextRequest) {
  const { searchParams, origin } = request.nextUrl;
  const code = searchParams.get("code");
  const next = searchParams.get("next") || "/";

  if (!code) {
    return NextResponse.redirect(`${origin}/login?error=Falta el código de confirmación.`);
  }

  const supabase = await createClient();
  const { data, error } = await supabase.auth.exchangeCodeForSession(code);

  if (error || !data.session) {
    return NextResponse.redirect(
      `${origin}/login?error=${encodeURIComponent("El link ya no es válido o venció. Probá iniciar sesión de nuevo.")}`
    );
  }

  const { user, access_token } = data.session;
  const creado = new Date(user.created_at).getTime();
  const ultimoLogin = new Date(user.last_sign_in_at ?? user.created_at).getTime();
  const esAltaNueva = Math.abs(ultimoLogin - creado) < UMBRAL_ALTA_NUEVA_MS;

  if (esAltaNueva) {
    const anonId = request.cookies.get(ANON_COOKIE_KEY)?.value ?? "";
    try {
      const fastapiUrl = process.env.FASTAPI_URL || "http://localhost:8000";
      await fetch(`${fastapiUrl}/api/account/claim`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${access_token}`,
        },
        body: JSON.stringify({ anon_id: anonId }),
      });
    } catch {
      // Si esto falla, la cuenta se crea igual — la persona no pierde el
      // acceso por un problema de migración. Peor caso: no se recuperan
      // los resultados viejos de la sesión anónima, no es fatal.
    }
  }

  return NextResponse.redirect(`${origin}${next}`);
}
