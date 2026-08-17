"use client";

import { ComposableMap, Geographies, Geography, Line, Marker } from "react-simple-maps";
// world-atlas: datos de mapa de verdad (Natural Earth, dominio público),
// instalado como paquete — no depende de bajar nada en runtime.
import landData from "world-atlas/land-110m.json";
import { IconHealth, IconTech, IconScience, IconCommerce, IconAdmin, IconDesign } from "./illustrations/icons";

type Point = [number, number]; // [longitud, latitud]

// 12 ciudades en los 6 continentes habitados (antes eran 6) — pedido de
// Marcos de "cargar más" la sección para que no se vea vacía. Los íconos
// son los mismos de icons.tsx (nada de emoji).
const PINS: { Icon: typeof IconHealth; label: string; coords: Point }[] = [
  { Icon: IconCommerce, label: "Comercio", coords: [-58.38, -34.6] }, // Buenos Aires
  { Icon: IconCommerce, label: "Comercio", coords: [-46.6, -23.5] }, // São Paulo
  { Icon: IconHealth, label: "Salud", coords: [-74.0, 40.7] }, // Nueva York
  { Icon: IconHealth, label: "Salud", coords: [-99.1, 19.4] }, // Ciudad de México
  { Icon: IconAdmin, label: "Administración", coords: [-3.7, 40.4] }, // Madrid
  { Icon: IconAdmin, label: "Administración", coords: [-0.1, 51.5] }, // Londres
  { Icon: IconScience, label: "Ciencia", coords: [3.4, 6.5] }, // Lagos
  { Icon: IconScience, label: "Ciencia", coords: [31.2, 30.0] }, // El Cairo
  { Icon: IconTech, label: "Tecnología", coords: [77.6, 12.9] }, // Bangalore
  { Icon: IconTech, label: "Tecnología", coords: [139.7, 35.7] }, // Tokio
  { Icon: IconTech, label: "Tecnología", coords: [-79.4, 43.7] }, // Toronto
  { Icon: IconDesign, label: "Diseño", coords: [151.2, -33.9] }, // Sídney
];

// Red tipo "hub": Buenos Aires (casa del producto) conectada con varias
// ciudades, más un par de conexiones cruzadas — da más sensación de red
// que una sola cadena.
const LINKS: [number, number][] = [
  [0, 2],
  [0, 4],
  [0, 8],
  [2, 5],
  [4, 6],
  [4, 9],
  [8, 10],
  [8, 11],
  [6, 7],
  [1, 0],
  [3, 2],
  [9, 11],
];

export function WorldMapDots() {
  return (
    <ComposableMap
      projection="geoNaturalEarth1"
      projectionConfig={{ scale: 155 }}
      width={900}
      height={460}
      className="mx-auto w-full max-w-3xl"
      role="img"
      aria-label="Mapa mundi con oportunidades conectadas"
    >
      <Geographies geography={landData}>
        {({ geographies }) =>
          geographies.map((geo) => (
            <Geography
              key={geo.rsmKey}
              geography={geo}
              fill="var(--color-terracota)"
              fillOpacity={0.85}
              stroke="var(--color-cream)"
              strokeWidth={0.6}
              style={{
                default: { outline: "none" },
                hover: { outline: "none" },
                pressed: { outline: "none" },
              }}
            />
          ))
        }
      </Geographies>

      {LINKS.map(([a, b], i) => (
        <Line
          key={i}
          from={PINS[a].coords}
          to={PINS[b].coords}
          stroke="var(--color-brown-title)"
          strokeWidth={0.8}
          strokeOpacity={0.3}
          strokeLinecap="round"
        />
      ))}

      {PINS.map((pin, i) => (
        <Marker key={i} coordinates={pin.coords}>
          <circle r={9.5} fill="var(--color-terracota)" stroke="var(--color-cream)" strokeWidth={1.3} />
          <pin.Icon x={-5.5} y={-5.5} width={11} height={11} stroke="var(--color-cream)" strokeWidth={2.4} />
        </Marker>
      ))}
    </ComposableMap>
  );
}
