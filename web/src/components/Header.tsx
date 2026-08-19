"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

// "Beneficios" se sacó el 13/08/2026: apuntaba a la sección vieja de
// "Destacados", que quedó reemplazada por "Oportunidades destacadas del
// día" — el link no llevaba a ningún lado.
const navItems = [
  { href: "#como-funciona", label: "Cómo funciona" },
  { href: "#contacto", label: "Contacto" },
];

// Fase 3 (18/08/2026): el botón "Ingresar" (antes deshabilitado, "Próximamente")
// ahora refleja la sesión real. Client Component porque necesita leer el
// estado de auth y reaccionar a login/logout sin recargar la página.
// Con Google, Supabase guarda el nombre real en user_metadata (Google lo
// manda siempre) — mostramos eso en vez del mail, es más prolijo y más
// corto. Con mail+contraseña no hay nombre de ningún lado, ahí seguimos
// mostrando el mail como antes (confirmado contra una cuenta real: Google
// deja tanto "full_name" como "name" con el mismo valor; alcanza con
// cualquiera de los dos).
function nombreParaMostrar(user: { email?: string; user_metadata?: Record<string, unknown> } | null | undefined) {
  if (!user) return null;
  const meta = user.user_metadata ?? {};
  return (meta.full_name as string) || (meta.name as string) || user.email || null;
}

export function Header() {
  const router = useRouter();
  const [nombre, setNombre] = useState<string | null | undefined>(undefined); // undefined = todavía no se sabe

  useEffect(() => {
    const supabase = createClient();

    supabase.auth.getUser().then(({ data }) => setNombre(nombreParaMostrar(data.user)));

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setNombre(nombreParaMostrar(session?.user));
    });
    return () => sub.subscription.unsubscribe();
  }, []);

  async function cerrarSesion() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/");
    router.refresh();
  }

  return (
    <header className="sticky top-0 z-20 bg-cream/95 backdrop-blur border-b border-brown-title/10">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-xl font-extrabold text-brown-title">
          Empat<span className="text-terracota">IA</span>{" "}
          <span className="font-normal text-brown-body">| NextStep</span>
        </Link>

        <nav className="hidden gap-8 md:flex">
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="text-sm font-semibold text-brown-title hover:text-terracota"
            >
              {item.label}
            </a>
          ))}
        </nav>

        {nombre ? (
          <div className="flex items-center gap-3">
            <span className="hidden max-w-[160px] truncate text-sm font-semibold text-brown-body sm:inline">
              {nombre}
            </span>
            <button
              type="button"
              onClick={cerrarSesion}
              className="rounded-full border-2 border-brown-title/20 px-5 py-2 text-sm font-bold text-brown-title hover:border-terracota hover:text-terracota"
            >
              Cerrar sesión
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="rounded-full border-2 border-brown-title/20 px-5 py-2 text-sm font-bold text-brown-title hover:border-terracota hover:text-terracota"
          >
            Ingresar
          </Link>
        )}
      </div>
    </header>
  );
}
