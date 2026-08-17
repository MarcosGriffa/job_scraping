/**
 * HowItWorksArt.tsx — las 3 ilustraciones grandes de "Cómo funciona el
 * match de EmpatÍA" (mockup nuevo de Marcos, 13/08). Reemplazan a los
 * íconos chicos que había antes. Mismo criterio de siempre: SVG propio,
 * formas simples, colores del proyecto — nada de emoji ni imágenes bajadas.
 */

export function ArtProfile() {
  return (
    <svg viewBox="0 0 120 100" className="h-28 w-auto" aria-hidden="true">
      {/* Documento (CV) */}
      <rect x="28" y="8" width="58" height="82" rx="5" fill="var(--color-cream)" stroke="var(--color-brown-title)" strokeOpacity={0.3} strokeWidth={1.2} />
      {/* Foto de perfil */}
      <rect x="36" y="16" width="18" height="18" rx="3" fill="var(--color-olive-tint)" />
      <circle cx="45" cy="22" r="4" fill="var(--color-olive-dark)" />
      <path d="M38 33 Q45 26 52 33" fill="var(--color-olive-dark)" />
      {/* Líneas de texto */}
      <rect x="58" y="18" width="22" height="2.6" rx="1.3" fill="var(--color-brown-body)" opacity={0.5} />
      <rect x="58" y="24" width="18" height="2.6" rx="1.3" fill="var(--color-brown-body)" opacity={0.35} />
      <rect x="58" y="30" width="20" height="2.6" rx="1.3" fill="var(--color-brown-body)" opacity={0.35} />
      <rect x="36" y="42" width="44" height="2.4" rx="1.2" fill="var(--color-brown-body)" opacity={0.3} />
      <rect x="36" y="48" width="44" height="2.4" rx="1.2" fill="var(--color-brown-body)" opacity={0.3} />
      <rect x="36" y="54" width="30" height="2.4" rx="1.2" fill="var(--color-brown-body)" opacity={0.3} />
      {/* Gráfico de barras */}
      <rect x="36" y="72" width="6" height="12" rx="1.5" fill="var(--color-olive-dark)" />
      <rect x="45" y="66" width="6" height="18" rx="1.5" fill="var(--color-olive)" />
      <rect x="54" y="70" width="6" height="14" rx="1.5" fill="var(--color-olive-dark)" />
      {/* Gráfico de torta */}
      <circle cx="72" cy="75" r="9" fill="var(--color-mustard-tint)" />
      <path d="M72 75 L72 66 A9 9 0 0 1 80 79 Z" fill="var(--color-mustard)" />
    </svg>
  );
}

export function ArtAnalysis() {
  return (
    <svg viewBox="0 0 120 100" className="h-28 w-auto" aria-hidden="true">
      {/* Líneas de circuito */}
      {[
        "M78 30 L98 30 L98 20",
        "M82 45 L104 45",
        "M78 60 L98 60 L98 72",
      ].map((d) => (
        <path key={d} d={d} fill="none" stroke="var(--color-brown-title)" strokeOpacity={0.35} strokeWidth={1.4} strokeLinecap="round" />
      ))}
      <circle cx="98" cy="18" r="2.4" fill="var(--color-terracota)" />
      <circle cx="104" cy="45" r="2.4" fill="var(--color-olive)" />
      <circle cx="98" cy="74" r="2.4" fill="var(--color-mustard)" />

      {/* Engranajes detrás de la lupa */}
      <g transform="translate(38 28)">
        {[0, 60, 120, 180, 240, 300].map((deg) => (
          <rect key={deg} x={-2.6} y={-16} width={5.2} height={7} rx={1} fill="var(--color-terracota)" transform={`rotate(${deg})`} />
        ))}
        <circle r="11" fill="var(--color-terracota)" />
        <circle r="4" fill="var(--color-cream)" />
      </g>
      <g transform="translate(30 52)">
        {[0, 60, 120, 180, 240, 300].map((deg) => (
          <rect key={deg} x={-2.2} y={-13} width={4.4} height={6} rx={1} fill="var(--color-olive)" transform={`rotate(${deg})`} />
        ))}
        <circle r="9" fill="var(--color-olive)" />
        <circle r="3.4" fill="var(--color-cream)" />
      </g>

      {/* Lupa */}
      <circle cx="58" cy="42" r="20" fill="var(--color-cream)" stroke="var(--color-brown-title)" strokeWidth={3} />
      <circle cx="58" cy="42" r="20" fill="var(--color-mustard-tint)" opacity={0.5} />
      <rect x="70" y="58" width="10" height="26" rx="4" fill="var(--color-brown-title)" transform="rotate(38 70 58)" />
    </svg>
  );
}

export function ArtMatch() {
  return (
    <svg viewBox="0 0 120 100" className="h-28 w-auto" aria-hidden="true">
      {/* Clipboard */}
      <rect x="14" y="14" width="46" height="74" rx="5" fill="var(--color-cream)" stroke="var(--color-brown-title)" strokeOpacity={0.3} strokeWidth={1.2} />
      <rect x="28" y="9" width="18" height="8" rx="3" fill="var(--color-terracota-dark)" />
      <circle cx="37" cy="13" r="1.6" fill="var(--color-cream)" />
      {[26, 42, 58].map((y) => (
        <g key={y}>
          <path d={`M20 ${y + 3} l3 3 l5 -6`} fill="none" stroke="var(--color-olive)" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" />
          <rect x="32" y={y} width="22" height="2.4" rx="1.2" fill="var(--color-brown-body)" opacity={0.4} />
        </g>
      ))}
      <rect x="20" y="72" width="6" height="6" rx="1.5" fill="none" stroke="var(--color-brown-body)" strokeWidth={1.6} opacity={0.4} />

      {/* Apretón de manos */}
      <g>
        <rect x="66" y="46" width="16" height="11" rx="2.5" fill="#4a5a72" transform="rotate(-18 66 46)" />
        <rect x="88" y="46" width="16" height="11" rx="2.5" fill="#5c6f8a" transform="rotate(18 88 46)" />
        <path d="M68 56 Q78 68 90 56 Q94 61 90 66 Q78 78 66 66 Q62 61 68 56 Z" fill="#c98b5e" />
      </g>
      {/* Pulgar arriba */}
      <g transform="translate(90 26)">
        <rect x="-4" y="0" width="16" height="10" rx="3" fill="#e8b98a" />
        <path d="M-4 2 Q-10 2 -10 8 Q-10 14 -3 14 L0 14 L0 2 Z" fill="#e8b98a" />
        <rect x="-1" y="-14" width="6" height="16" rx="3" fill="#e8b98a" />
      </g>
    </svg>
  );
}
