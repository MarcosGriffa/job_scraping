import { ArtProfile, ArtAnalysis, ArtMatch } from "./illustrations/HowItWorksArt";

const steps = [
  {
    Art: ArtProfile,
    title: "Crea tu Perfil Integral.",
    text: "Importa tu CV, conecta tu portafolio y completa nuestra evaluación de perfil para que la IA entienda tus fortalezas y pasiones.",
    top: "bg-olive",
    bottom: "bg-olive-tint",
  },
  {
    Art: ArtAnalysis,
    title: "Nuestra IA de Vanguardia Analiza.",
    text: "El algoritmo escanea miles de ofertas, considerando no solo palabras clave, sino también el contexto de la empresa y tu potencial.",
    top: "bg-mustard",
    bottom: "bg-mustard-tint",
  },
  {
    Art: ArtMatch,
    title: "Recibe Matches Reales.",
    text: "Te presentamos solo las oportunidades con el mayor puntaje de compatibilidad, para que apliques con confianza.",
    top: "bg-terracota",
    bottom: "bg-terracota-tint",
  },
];

export function HowItWorks() {
  return (
    <section id="como-funciona" className="mx-auto max-w-6xl px-6 py-16 md:py-24">
      <h2 className="text-center text-3xl font-extrabold uppercase tracking-wide text-brown-title">
        Cómo funciona el match de EmpatÍA
      </h2>

      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {steps.map((step, i) => (
          <div key={step.title} className="overflow-hidden rounded-3xl">
            <div className={`flex justify-center pb-10 pt-8 ${step.top}`}>
              <step.Art />
            </div>
            <div className={`-mt-6 rounded-t-[2.5rem] px-7 pb-8 pt-8 ${step.bottom}`}>
              <h3 className="text-lg font-extrabold text-brown-title">
                {i + 1}. {step.title}
              </h3>
              <p className="mt-3 text-sm text-brown-title/80">{step.text}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
