"use client";

import Image from "next/image";
import { MatchesLogo } from "./illustrations/MatchesLogo";

/**
 * HeroMindMap — v4. Última ronda de ajustes de Marcos (13/08):
 *   - El logo central ahora escala en % del contenedor, igual que las
 *     ilustraciones de personas — mismo mecanismo, así "30% más chico que
 *     los profesionales" es simplemente un número (LOGO_WIDTH).
 *   - Más separación entre el logo y cada persona.
 *   - Líneas: color brown-title (el marrón oscuro que ya se usa en todo
 *     el sitio), no el tono muestreado de la referencia.
 */

const CENTER = { x: 50, y: 45 };

// Ancho de los profesionales: 40/38/30 (promedio ~36). El logo tiene que
// ser "solo un 30% más chico" -> 70% de ese promedio.
const LOGO_WIDTH = 26;
const LOGO_RATIO = 100 / 116; // viewBox del logo (ver MatchesLogo.tsx)

// Líneas "orbitales" extra que pidió Marcos (dibujó arcos grandes conectando
// a los profesionales entre sí, además de las que ya van al centro) — mismo
// color y técnica que el resto, un toque más finas/tenues para que queden
// de fondo y no compitan con las líneas principales.
const orbitLines = [
  { d: "M22 8 Q50 -14 78 8" }, // Salud ↔ Tecnología, por arriba
  { d: "M90 28 Q110 56 64 85" }, // Tecnología ↔ Comercio, por la derecha
  { d: "M10 28 Q-10 56 36 85" }, // Salud ↔ Comercio, por la izquierda (cierra el circuito)
];

const BLOB_PATH =
  "M62.96 41.18 Q65.4 45.0 62.59 48.55 Q59.79 52.11 57.38 56.21 Q54.98 60.31 50.51 58.74 " +
  "Q46.04 57.17 41.67 55.7 Q37.3 54.23 37.5 49.61 Q37.7 45.0 37.7 40.53 " +
  "Q37.7 36.07 42.01 34.88 Q46.32 33.68 50.55 31.97 Q54.79 30.26 57.66 33.81 Q60.52 37.36 62.96 41.18";

const branches: {
  variant: "salud" | "tecnologia" | "comercio";
  label: string;
  x: number;
  y: number;
  width: number;
  ratio: number;
  lineTo: { x: number; y: number };
  labelPos: { x: number; y: number };
  /** Punto de control de la curva. Por defecto se calcula solo (bow hacia
   * afuera), pero "Comercio" lo necesita explícito: al ser una línea recta
   * hacia abajo, el cálculo automático la hacía pasar justo por detrás del
   * texto del logo. */
  control?: { x: number; y: number };
}[] = [
  {
    variant: "salud",
    label: "Salud",
    x: 17,
    y: 17,
    width: 40,
    ratio: 900 / 834,
    lineTo: { x: 35, y: 30 },
    labelPos: { x: 17, y: -4 },
  },
  {
    variant: "tecnologia",
    label: "Tecnología",
    x: 83,
    y: 19,
    width: 38,
    ratio: 900 / 939,
    lineTo: { x: 65, y: 30 },
    labelPos: { x: 83, y: -4 },
  },
  {
    variant: "comercio",
    label: "Comercio",
    x: 50,
    y: 84,
    width: 30,
    ratio: 900 / 1147,
    lineTo: { x: 50, y: 61 },
    control: { x: 65, y: 50 },
    labelPos: { x: 50, y: 106 },
  },
];

export function HeroMindMap() {
  return (
    <div className="relative mx-auto aspect-[100/110] w-full max-w-lg">
      <svg
        viewBox="0 0 100 110"
        className="absolute inset-0 h-full w-full overflow-visible"
        aria-hidden="true"
      >
        {orbitLines.map((line, i) => (
          <path
            key={`orbit-${i}`}
            d={line.d}
            fill="none"
            stroke="var(--color-brown-title)"
            strokeOpacity={0.35}
            strokeWidth={0.7}
            strokeLinecap="round"
          />
        ))}

        {branches.map((b) => {
          const control = b.control ?? { x: (CENTER.x + b.lineTo.x) / 2, y: (CENTER.y + b.lineTo.y) / 2 - 4 };
          return (
            <path
              key={b.label}
              d={`M ${CENTER.x} ${CENTER.y} Q ${control.x} ${control.y} ${b.lineTo.x} ${b.lineTo.y}`}
              fill="none"
              stroke="var(--color-brown-title)"
              strokeOpacity={0.75}
              strokeWidth={0.9}
              strokeLinecap="round"
            />
          );
        })}

        {/* Nodo central: blob orgánico — mismo color que el fondo del hero,
            no blanco (quedaba como un parche disruptivo). */}
        <path d={BLOB_PATH} fill="var(--color-cream)" stroke="var(--color-brown-title)" strokeOpacity={0.25} strokeWidth={0.5} />
      </svg>

      {/* Sombra detrás de cada persona: degradado marrón clarito (no el
          color de categoría que había antes) — pedido de Marcos. */}
      {branches.map((b) => (
        <div
          key={`glow-${b.label}`}
          style={{
            left: `${b.x}%`,
            top: `${b.y}%`,
            width: `${b.width * 0.95}%`,
            aspectRatio: "1 / 1",
            background:
              "radial-gradient(circle, rgba(154,120,94,0.4) 0%, rgba(154,120,94,0.18) 45%, rgba(154,120,94,0) 72%)",
          }}
          className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full"
        />
      ))}

      {/* Personas — PNG con transparencia real, sin marco circular */}
      {branches.map((b) => (
        <div
          key={b.label}
          style={{ left: `${b.x}%`, top: `${b.y}%`, width: `${b.width}%`, aspectRatio: `${b.ratio}` }}
          className="absolute -translate-x-1/2 -translate-y-1/2 drop-shadow-[0_6px_10px_rgba(74,47,32,0.18)]"
        >
          <Image
            src={`/illustrations/${b.variant}.png`}
            alt={b.label}
            fill
            sizes="260px"
            className="object-contain"
          />
        </div>
      ))}

      {/* Etiquetas de rubro — siempre afuera de la ilustración, nunca pisándola */}
      {branches.map((b) => (
        <span
          key={`label-${b.label}`}
          style={{ left: `${b.labelPos.x}%`, top: `${b.labelPos.y}%` }}
          className="absolute -translate-x-1/2 -translate-y-1/2 whitespace-nowrap rounded-full bg-terracota px-2.5 py-1 text-[11px] font-bold text-white"
        >
          {b.label}
        </span>
      ))}

      {/* Logo del nodo central — mismo mecanismo de escala (% del
          contenedor) que las personas, para que "70% del tamaño de los
          profesionales" sea un número real, no una aproximación visual. */}
      <div
        style={{
          left: `${CENTER.x}%`,
          top: `${CENTER.y}%`,
          width: `${LOGO_WIDTH}%`,
          aspectRatio: `${LOGO_RATIO}`,
        }}
        className="absolute z-10 -translate-x-1/2 -translate-y-1/2"
      >
        <MatchesLogo />
      </div>
    </div>
  );
}
