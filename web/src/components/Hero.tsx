import { PillButton } from "./PillButton";
import { HeroStats } from "./HeroStats";
import { SearchBar } from "./SearchBar";
import { IconCheckCircle } from "./illustrations/icons";

// "Cualquier rubro" salió de acá el 17/08/2026: el bloque de números de la
// derecha ya lo dice más fuerte ("Todos los rubros"), y repetirlo restaba.
const trustBadges = ["Gratis para empezar", "Resultados en minutos", "Sin crear cuenta"];

export function Hero() {
  return (
    <section className="mx-auto grid max-w-6xl items-center gap-12 px-6 py-16 md:grid-cols-2 md:py-24">
      <div>
        <h1 className="text-4xl font-extrabold leading-tight text-brown-title md:text-5xl">
          Tu próximo trabajo, sin importar tu rubro
        </h1>
        <p className="mt-6 text-lg text-brown-body">
          Nuestra IA inclusiva te conecta con oportunidades en todas las áreas y
          profesiones, desde la salud hasta la tecnología, la ciencia y el comercio.
        </p>
        <div className="mt-8">
          <PillButton href="/subir-cv">Encontrá tu match →</PillButton>
        </div>

        <SearchBar />

        <ul className="mt-6 flex flex-col gap-2.5">
          {trustBadges.map((t) => (
            <li key={t} className="flex items-center gap-2 text-sm font-semibold text-brown-body">
              <IconCheckCircle className="h-5 w-5 shrink-0 text-olive" />
              {t}
            </li>
          ))}
        </ul>
      </div>

      <HeroStats />
    </section>
  );
}
