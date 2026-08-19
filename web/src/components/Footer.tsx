import Link from "next/link";

// Footer simple, con la marca y el único link institucional que hoy tiene
// contenido real detrás. Antes tenía más (Privacy Policy, Terms, About Us,
// Careers, redes sociales) — se sacaron el 18/08/2026 porque eran
// placeholders sin destino. La Política de Privacidad volvió el
// 19/08/2026, ahora que /privacidad existe de verdad.
export function Footer() {
  return (
    <footer className="bg-[#1c223a] py-8">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-3 px-6 text-center">
        <p className="text-sm text-cream/70">© 2026 EmpatÍA | NextStep. Todos los derechos reservados.</p>
        <Link href="/privacidad" className="text-sm font-semibold text-cream/90 hover:text-white">
          Política de Privacidad
        </Link>
      </div>
    </footer>
  );
}
