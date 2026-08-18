// Fase 2 (histórico): sin login, cada navegador tenía un id anónimo propio
// (esta cookie) para poder guardar resultados y "ofertas aplicadas" sin
// cuenta.
//
// Fase 3 (18/08/2026): usar el matching ya requiere cuenta real, así que
// esta cookie DEJÓ DE ESCRIBIRSE — no queda ninguna acción anónima que
// genere datos nuevos, así que no tiene sentido seguir creándola.
//
// Se deja solo el NOMBRE acá (no las funciones de leer/escribir, que ya no
// las llama nadie) porque /auth/callback todavía necesita leer esta cookie
// del lado servidor, para quien ya la tenía de una visita anterior: al
// crear una cuenta, esos datos viejos se migran una sola vez a la cuenta
// nueva. Ver api/main.py POST /api/account/claim y
// web/src/app/auth/callback/route.ts.
export const ANON_COOKIE_KEY = "empatia_user_id";
