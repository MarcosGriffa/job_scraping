interface Testimonial {
  quote: string;
  name: string;
  role: string;
  company: string;
  photo: string;
  cardBg: string;
}

// Los 3 que pasó Marcos — ahora sí los 3 juntos: uno muestra un resultado
// concreto y rápido, otro el valor central del producto (la experiencia
// sirve para OTRO rubro), y el tercero refuerza que llegan oportunidades
// relevantes de forma continua, no solo una vez. Las empresas son
// ficticias, al mismo nivel que el resto de los ejemplos del sitio.
//
// Las fotos son de randomuser.me (gratis, sin key) — son caras generadas
// para usarse justo en este tipo de mockup/demo, no son fotos de personas
// reales identificables.
const testimonials: Testimonial[] = [
  {
    quote:
      "En una semana tenía tres entrevistas agendadas con roles que ni sabía que existían para mi perfil.",
    name: "Valentina R.",
    role: "Analista de Datos",
    company: "Datalytics",
    photo: "https://randomuser.me/api/portraits/women/65.jpg",
    cardBg: "bg-olive-tint",
  },
  {
    quote:
      "Nunca pensé que una IA pudiera entender que mi experiencia en ventas también servía para atención al cliente en salud.",
    name: "Diego M.",
    role: "Asesor Comercial",
    company: "Clínica San Rafael",
    photo: "https://randomuser.me/api/portraits/men/32.jpg",
    cardBg: "bg-terracota-tint",
  },
  {
    quote:
      "Subí mi CV una vez y desde entonces me llegan oportunidades que realmente tienen que ver conmigo, no listados genéricos.",
    name: "Camila F.",
    role: "Bióloga",
    company: "OceanData",
    photo: "https://randomuser.me/api/portraits/women/68.jpg",
    cardBg: "bg-mustard-tint",
  },
];

export function Testimonials() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-16 md:py-20">
      <h2 className="text-center text-3xl font-extrabold uppercase tracking-wide text-brown-title">
        Historias de éxito
      </h2>

      <div className="mt-10 grid gap-6 md:grid-cols-3">
        {testimonials.map((t) => (
          <div key={t.name} className={`flex flex-col items-center rounded-3xl p-8 text-center ${t.cardBg}`}>
            {/* eslint-disable-next-line @next/next/no-img-element -- foto externa (randomuser.me), no vale la pena pasarla por el optimizador de Next para un avatar chico */}
            <img
              src={t.photo}
              alt={t.name}
              width={88}
              height={88}
              className="h-20 w-20 rounded-full object-cover md:h-22 md:w-22"
            />
            <span className="mt-3 block font-serif text-4xl leading-none text-brown-title/40" aria-hidden="true">
              &ldquo;
            </span>
            <p className="mt-1 text-brown-title">{t.quote}</p>
            <p className="mt-4 font-bold text-brown-title">{t.name}</p>
            <p className="text-sm text-brown-body">
              {t.role}, {t.company}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
