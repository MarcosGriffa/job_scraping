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
export function Header() {
  const router = useRouter();
  const [email, setEmail] = useState<string | null | undefined>(undefined); // undefined = todavía no se sabe

  useEffect(() => {
    const supabase = createClient();

    supabase.auth.getUser().then(({ data }) => setEmail(data.user?.email ?? null));

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setEmail(session?.user?.email ?? null);
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

        {email ? (
          <div className="flex items-center gap-3">
            <span className="hidden max-w-[160px] truncate text-sm font-semibold text-brown-body sm:inline">
              {email}
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
