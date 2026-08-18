// proxy.ts — Fase 3. En Next.js 16 este archivo reemplazó a middleware.ts
// (mismo mecanismo, nombre nuevo — ver node_modules/next/dist/docs/.../proxy.md).
//
// Hace dos cosas en cada pedido:
//   1. Refresca la sesión de Supabase (patrón estándar de @supabase/ssr:
//      sin esto, la sesión se vence sola aunque la persona siga usando el
//      sitio).
//   2. Si el pedido es a una ruta que requiere cuenta (/subir-cv,
//      /resultados) y no hay sesión, redirige a /crear-cuenta ANTES de que
//      se dibuje nada — evita el "flash" de la pantalla protegida.
//
// La landing y el resto del sitio siguen libres, sin cuenta (decisión de
// producto de Marcos, 18/08/2026): "no se puede usar el matching sin
// cuenta" incluye ver resultados, no solo subir el CV.
import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

const RUTAS_PROTEGIDAS = ["/subir-cv", "/resultados"];

export async function proxy(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
        },
      },
    }
  );

  // getUser() (no getSession()) valida el token contra Supabase — es la
  // forma recomendada acá, porque getSession() solo lee la cookie sin
  // verificarla.
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const necesitaSesion = RUTAS_PROTEGIDAS.some(
    (ruta) => request.nextUrl.pathname === ruta || request.nextUrl.pathname.startsWith(`${ruta}/`)
  );

  if (necesitaSesion && !user) {
    const destino = request.nextUrl.clone();
    destino.pathname = "/crear-cuenta";
    destino.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(destino);
  }

  return response;
}

export const config = {
  matcher: [
    // Corre en todo menos assets estáticos y optimización de imágenes —
    // si no, cada CSS/JS/imagen pasa por acá de arriba sin necesidad.
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
