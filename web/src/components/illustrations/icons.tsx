/**
 * icons.tsx — set de íconos propios (línea simple, sin relleno), para
 * reemplazar TODOS los emojis del sitio (pedido de Marcos, 13/08: "cero
 * emojis en toda la página, todo tiene que ser ilustración propia
 * coherente con la paleta"). Se usan en "Cómo funciona", "Destacados" y
 * los pines del mapamundi.
 *
 * Todos comparten viewBox 0 0 24 24, trazo (no relleno), heredan el color
 * de texto del contenedor (currentColor) — así cada sección los puede
 * pintar con su propio color de acento sin duplicar componentes.
 */

import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

const base = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

export function IconUpload(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M12 14V3" />
      <path d="M8 7l4-4 4 4" />
      <path d="M5 15v3a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-3" />
    </svg>
  );
}

export function IconMatch(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect x="3" y="7" width="12" height="12" rx="3" />
      <rect x="9" y="5" width="12" height="12" rx="3" />
      <path d="M11 12l2 2 4-4" />
    </svg>
  );
}

export function IconRocket(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M12 2c3 2.2 5 6 5 10 0 2-1 3.8-2 5l-3 2-3-2c-1-1.2-2-3-2-5 0-4 2-7.8 5-10z" />
      <circle cx="12" cy="10" r="1.6" />
      <path d="M7.5 14c-2 0-3 2-3 5 2-1 3-1 4-3" />
      <path d="M16.5 14c2 0 3 2 3 5-2-1-3-1-4-3" />
      <path d="M10 19c0 1.8 1 3 2 3s2-1.2 2-3" />
    </svg>
  );
}

export function IconHealth(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect x="9" y="3" width="6" height="18" rx="2" />
      <rect x="3" y="9" width="18" height="6" rx="2" />
    </svg>
  );
}

export function IconTech(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect x="4" y="4" width="16" height="10.5" rx="1.5" />
      <path d="M2.5 18.5h19l-1.8-2H4.3l-1.8 2z" />
    </svg>
  );
}

export function IconScience(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M10 2h4" />
      <path d="M10 2v6.5l-5.2 9.2A2 2 0 0 0 6.5 21h11a2 2 0 0 0 1.7-3.3L14 8.5V2" />
      <circle cx="9.5" cy="17" r="0.9" fill="currentColor" stroke="none" />
      <circle cx="13.5" cy="18.7" r="0.7" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconCommerce(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M6 8h12l1 12a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2L6 8z" />
      <path d="M9 8V6a3 3 0 0 1 6 0v2" />
    </svg>
  );
}

export function IconAdmin(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M3 20h18" />
      <path d="M6 20v-7" />
      <path d="M12 20V6" />
      <path d="M18 20v-10" />
    </svg>
  );
}

export function IconDesign(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M12 3a9 9 0 1 0 5 16.5c1-.7.5-2-.5-2.5-.7-.4-1-1-1-1.7 0-1 .8-1.6 1.8-1.6H19a3 3 0 0 0 3-3.2C21.6 6.2 17.4 3 12 3z" />
      <circle cx="8" cy="12" r="1" fill="currentColor" stroke="none" />
      <circle cx="9.5" cy="8" r="1" fill="currentColor" stroke="none" />
      <circle cx="14.5" cy="7.5" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconCheckCircle(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M8.5 12.3l2.3 2.3 4.7-5" />
    </svg>
  );
}

export function IconChevronRight(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M9 5l7 7-7 7" />
    </svg>
  );
}

export function IconMail(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect x="3" y="5" width="18" height="14" rx="2.5" />
      <path d="M3.5 6.5l8.5 7 8.5-7" />
    </svg>
  );
}

export function IconNetwork(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <circle cx="12" cy="5" r="2.4" />
      <circle cx="5" cy="18" r="2.4" />
      <circle cx="19" cy="18" r="2.4" />
      <path d="M10.5 7L6.5 15.8" />
      <path d="M13.5 7l4 8.8" />
      <path d="M7.4 18h9.2" />
    </svg>
  );
}

export function IconGlobe(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M3.2 9.5h17.6" />
      <path d="M3.2 14.5h17.6" />
      <path d="M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9S9.4 5.6 12 3z" />
    </svg>
  );
}

export function IconPin(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z" />
      <circle cx="12" cy="9.5" r="2.4" />
    </svg>
  );
}

// Íconos de redes sociales — versiones simplificadas propias (no son los
// logos oficiales, es la misma línea de dibujo simple que el resto del
// set), para el footer nuevo.
export function IconX(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M4 4l16 16" />
      <path d="M20 4L4 20" />
    </svg>
  );
}

export function IconFacebook(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M14 21v-8h3l.5-3.5H14V7.2c0-1 .4-1.7 2-1.7h1.6V2.2C17.1 2.1 16 2 14.8 2 12 2 10.5 3.7 10.5 6.8v2.7H7.5V13h3v8" />
    </svg>
  );
}

export function IconInstagram(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4.2" />
      <circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconYoutube(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect x="2.5" y="6" width="19" height="12" rx="4" />
      <path d="M10.5 9.5l5 2.5-5 2.5z" fill="currentColor" stroke="none" />
    </svg>
  );
}
