import Link from "next/link";

// "Beneficios" se sacó el 13/08/2026: apuntaba a la sección vieja de
// "Destacados", que quedó reemplazada por "Oportunidades destacadas del
// día" — el link no llevaba a ningún lado.
const navItems = [
  { href: "#como-funciona", label: "Cómo funciona" },
  { href: "#contacto", label: "Contacto" },
];

export function Header() {
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

        <button
          type="button"
          title="Próximamente"
          className="rounded-full border-2 border-brown-title/20 px-5 py-2 text-sm font-bold text-brown-title/50 cursor-not-allowed"
        >
          Ingresar
        </button>
      </div>
    </header>
  );
}
