// URL del backend Python (FastAPI, carpeta api/ en la raíz del repo).
// En desarrollo local corre en el puerto 8000 por defecto — ver README_FASE2.md.
// Se puede pisar con la variable de entorno FASTAPI_URL en web/.env.local.
export const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";
