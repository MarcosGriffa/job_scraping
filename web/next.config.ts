import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Next.js 16 cambió el default a 'attachment' (fuerza descarga en vez de
    // mostrar la imagen) como medida de seguridad para SVGs subidos por
    // usuarios. Acá solo servimos PNG propios desde public/illustrations/,
    // sin riesgo — sin este cambio, next/image no las muestra en pantalla,
    // el navegador las trata como si fueran para descargar.
    contentDispositionType: "inline",
  },
};

export default nextConfig;
