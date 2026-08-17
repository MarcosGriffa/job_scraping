// Fase 2: todavía no hay login. Para poder llevar la cuenta de "qué ofertas
// ya marcó esta persona como aplicada" sin cuentas de usuario, le asignamos
// un id anónimo al navegador la primera vez que entra.
//
// v2 (13/08): guardado en una COOKIE (antes era localStorage) — pedido
// explícito de esta etapa. La cookie la puede leer también el servidor si
// hiciera falta más adelante, y persiste 1 año. Si el navegador ya tenía
// el id viejo en localStorage, se migra a la cookie con el mismo valor,
// así no se pierden los resultados/aplicados que ya tenía esa persona.
//
// Cuando llegue el login de verdad (Fase 3), esto se reemplaza por el
// user_id real de la sesión — API y base ya reciben cualquier string.
const KEY = "empatia_user_id";
const ONE_YEAR_SECONDS = 60 * 60 * 24 * 365;

function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function writeCookie(name: string, value: string) {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${ONE_YEAR_SECONDS}; samesite=lax`;
}

export function getUserId(): string {
  if (typeof window === "undefined") return "default";

  let id = readCookie(KEY);
  if (!id) {
    // Migración desde localStorage (donde vivía el id hasta ahora)
    id = window.localStorage.getItem(KEY) ?? crypto.randomUUID();
    writeCookie(KEY, id);
  }
  return id;
}
