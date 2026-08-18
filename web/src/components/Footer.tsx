// Footer simple, solo con la marca. Antes tenía links institucionales
// (Privacy Policy, Terms, About Us, Careers) e íconos de redes sociales —
// se sacaron el 18/08/2026: ninguna de esas páginas existe todavía y
// Marcos no tiene esas cuentas creadas, así que eran placeholders que no
// llevaban a ningún lado. Se vuelve a armar cuando haya algo real detrás.
export function Footer() {
  return (
    <footer className="bg-[#1c223a] py-8">
      <div className="mx-auto max-w-6xl px-6 text-center">
        <p className="text-sm text-cream/70">© 2026 EmpatÍA | NextStep. Todos los derechos reservados.</p>
      </div>
    </footer>
  );
}
