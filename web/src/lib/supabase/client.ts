// Cliente de Supabase para usar en Componentes de Cliente ("use client").
// Fase 3 — login real. Ver web/src/lib/supabase/server.ts para el
// equivalente del lado servidor (Route Handlers, Server Components).
import { createBrowserClient } from "@supabase/ssr";

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
