// Cliente de Supabase para usar del lado servidor (Route Handlers, Server
// Components, proxy.ts). A diferencia del de client.ts, este lee/escribe
// la sesión desde las cookies del pedido — así el servidor sabe quién sos
// sin que el navegador tenga que mandar nada aparte.
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

/** Fase 3 — el token de la sesión actual (o null si no hay sesión), para
 * que las rutas /api/* del lado servidor se lo manden al motor Python como
 * "Authorization: Bearer <token>". Usa getSession() (no getUser()) porque
 * acá el token solo se REENVÍA — quien de verdad lo valida por firma es el
 * motor (api/auth.py); no hace falta duplicar esa verificación acá. */
export async function getAccessToken(): Promise<string | null> {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token ?? null;
}

export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) => cookieStore.set(name, value, options));
        } catch {
          // Se llama desde un Server Component (no puede escribir cookies) —
          // inofensivo si proxy.ts ya está refrescando la sesión en cada
          // pedido, que es el caso acá.
        }
      },
    },
  });
}
