import Link from "next/link";
import { IconX, IconFacebook, IconInstagram, IconYoutube } from "./illustrations/icons";

// Links de legales/institucional — todavía no existen esas páginas, así
// que van a "#" (excepto Contact, que sí es una sección real de esta
// misma página). No hace falta crear las páginas para este MVP.
const footerLinks = [
  { label: "Privacy Policy", href: "#" },
  { label: "Terms of Service", href: "#" },
  { label: "About Us", href: "#" },
  { label: "Careers", href: "#" },
  { label: "Contact", href: "#contacto" },
];

// Redes — sin cuentas creadas todavía, van a "#" (pedido explícito de
// Marcos: no hace falta crear las cuentas para esto).
const socials = [
  { Icon: IconX, label: "X" },
  { Icon: IconFacebook, label: "Facebook" },
  { Icon: IconInstagram, label: "Instagram" },
  { Icon: IconYoutube, label: "YouTube" },
];

export function Footer() {
  return (
    <footer className="bg-[#1c223a] py-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6">
        <nav className="flex flex-wrap justify-center gap-x-6 gap-y-2 md:justify-start">
          {footerLinks.map((l) => (
            <Link key={l.label} href={l.href} className="text-sm font-semibold text-cream/90 hover:text-white">
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="flex flex-col items-center gap-4 md:flex-row md:justify-between">
          <p className="text-sm text-cream/70">© 2026 EmpatÍA | NextStep. Todos los derechos reservados.</p>
          <div className="flex gap-3">
            {socials.map((s) => (
              <a
                key={s.label}
                href="#"
                aria-label={s.label}
                className="flex h-9 w-9 items-center justify-center rounded-full bg-cream/90 text-[#1c223a] hover:bg-white"
              >
                <s.Icon className="h-4.5 w-4.5" />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
