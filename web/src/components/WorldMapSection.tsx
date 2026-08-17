"use client";

import dynamic from "next/dynamic";
import { IconHealth, IconTech, IconScience, IconCommerce, IconAdmin, IconDesign } from "./illustrations/icons";

// react-simple-maps calcula las proyecciones geográficas con floats que no
// dan bit-a-bit igual en Node (servidor) que en el navegador — React tira
// un warning de "hydration mismatch" en la consola aunque el mapa se vea
// perfecto (es solo un dígito decimal de diferencia en la posición). Se
// evita de raíz cargando el mapa SOLO en el cliente, sin server-render.
const WorldMapDots = dynamic(() => import("./WorldMapDots").then((m) => m.WorldMapDots), {
  ssr: false,
  loading: () => <div className="mx-auto aspect-[900/460] w-full max-w-3xl" />,
});

// Leyenda de rubros debajo del mapa — suma contenido/presencia a la
// sección (pedido de Marcos: "cargarla más") sin inventar números o
// estadísticas que no tenemos todavía.
const rubros = [
  { Icon: IconHealth, label: "Salud" },
  { Icon: IconTech, label: "Tecnología" },
  { Icon: IconScience, label: "Ciencia" },
  { Icon: IconCommerce, label: "Comercio" },
  { Icon: IconAdmin, label: "Administración" },
  { Icon: IconDesign, label: "Diseño" },
];

export function WorldMapSection() {
  return (
    <section className="bg-cream-soft py-16 md:py-24">
      <div className="mx-auto max-w-4xl px-6 text-center">
        <h2 className="text-3xl font-extrabold uppercase tracking-wide text-brown-title md:text-4xl">
          Alcance global de oportunidades
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-brown-body">
          Conectando talento en todos los continentes. Encuentra tu trabajo ideal, localmente o
          de forma remota.
        </p>
        <div className="mt-10">
          <WorldMapDots />
        </div>

        <div className="mx-auto mt-10 flex max-w-2xl flex-wrap items-center justify-center gap-3">
          {rubros.map((r) => (
            <span
              key={r.label}
              className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-semibold text-brown-title"
            >
              <r.Icon className="h-4 w-4 text-terracota" />
              {r.label}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
