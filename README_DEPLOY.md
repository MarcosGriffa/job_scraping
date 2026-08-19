# Publicar EmpatÍA | NextStep — paso a paso

Dos piezas, dos servicios:

- **La web** (Next.js, carpeta `web/`) → **Vercel**
- **El motor** (Python/FastAPI, carpeta `api/`) → **Render**

Los dos se despliegan leyendo este mismo repositorio de GitHub. Cada uno
detecta cambios y se actualiza solo cuando se sube algo nuevo a `main`.

## 0. Antes de arrancar

Vas a necesitar tener a mano las claves que ya están en tu `.env` local
(Groq, Supabase, Jooble, Cohere) — se vuelven a cargar en el panel de cada
servicio, nunca se suben al repositorio.

## 1. Motor → Render

1. Entrá a [render.com](https://render.com) y creá cuenta con GitHub.
2. **New +** → **Blueprint** → elegí este repositorio. Render va a leer
   `render.yaml` solo y va a proponer crear el servicio `empatia-nextstep-motor`
   (plan **Free**). Confirmá.
3. Andá a la pestaña **Environment** del servicio y cargá estas variables
   (los mismos valores que tenés en tu `.env` local):
   - `GROQ_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SECRET_KEY`
   - `JOOBLE_API_KEY`
   - `COHERE_API_KEY`
   - `ALLOWED_ORIGINS` — dejala **vacía por ahora**, se completa en el paso 3
     una vez que sepamos la URL de la web.
4. Guardá. Render va a instalar dependencias y arrancar — tarda unos
   minutos la primera vez. Cuando termine, la pestaña de arriba muestra la
   URL del servicio, algo como `https://empatia-nextstep-motor.onrender.com`.
5. Confirmá que responde: entrá a `<esa URL>/health` en el navegador y
   tiene que decir `{"status":"ok","storage_backend":"supabase"}`.

**Ojo con el plan gratis:**
- Se "duerme" a los 15 minutos sin uso. La primera visita después de un
  rato tarda ~1 minuto extra en despertar, sumado a los 1-3 minutos normales
  de una búsqueda.
- El disco se borra en cada reinicio. No rompe nada (ver README_FASE2.md),
  pero los CVs adaptados que quedaron cacheados se regeneran solos si hace
  falta.

## 2. Web → Vercel

1. Entrá a [vercel.com](https://vercel.com) y creá cuenta con GitHub.
2. **Add New** → **Project** → elegí este repositorio.
3. En **Root Directory**, cambiala a `web` (el proyecto de Next.js no está
   en la raíz del repo, está en esa carpeta). Vercel detecta Next.js solo
   apenas la cambiás.
4. En **Environment Variables**, agregá:
   - `FASTAPI_URL` = la URL de Render del paso 1 (sin la barra final), ej.
     `https://empatia-nextstep-motor.onrender.com`
   - `NEXT_PUBLIC_SUPABASE_URL` = mismo valor que `SUPABASE_URL` en Render.
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = mismo valor que `SUPABASE_PUBLISHABLE_KEY`
     en Render (la clave pública, segura para el navegador — **nunca** la
     `SUPABASE_SECRET_KEY`, esa es solo para el motor).
   - Las tres tienen que estar tildadas para el ambiente **Production**, no
     solo Preview/Development — es un tilde que se pasa por alto fácil.
5. **Deploy**. Tarda 1-2 minutos. Al terminar da una URL pública, algo
   como `https://empatia-nextstep.vercel.app`.

> ⚠️ **Las variables `NEXT_PUBLIC_*` se incrustan en el código AL COMPILAR,
> no se leen en caliente.** Si las agregás o corregís *después* de que ya
> existe un build, un "Redeploy" común puede reutilizar ese build viejo
> (con la variable todavía ausente adentro) y el error sigue apareciendo
> aunque la variable ya esté bien cargada en el panel. Nos pasó (18/08/2026:
> "Error: Your project's URL and Key are required to create a Supabase
> client" en el 100% de los pedidos, con las variables ya cargadas). La
> señal de alarma es la fecha del deployment activo: si dice "Ready" pero
> con una fecha vieja, sospechá de esto. La forma confiable de arreglarlo:
> al Redeploy-ear, buscar la opción de **no usar la caché de build** (o,
> más simple, subir cualquier commit nuevo — un push siempre fuerza un
> build de cero).

## 3. Cerrar el círculo: restringir el motor a la web

Con la URL de Vercel ya conocida, volvé a Render → Environment → completá:

- `ALLOWED_ORIGINS` = `https://empatia-nextstep.vercel.app` (la URL exacta
  del paso 2, sin barra final)

Guardá — Render reinicia el servicio solo con la variable nueva.

## 4. Probar

1. Entrá a la URL de Vercel.
2. Subí un CV real y esperá los resultados (1-3 min, o más si el motor
   estaba dormido).
3. Probá "Generar CV para esta oferta" y "Marcar como aplicado".
4. Volvé a entrar más tarde (o desde el celular) — los resultados no
   persisten entre dispositivos todavía (eso es Fase 3, cuentas reales).

## Si algo no anda

- **La web carga pero al subir CV tira error de conexión**: revisá que
  `FASTAPI_URL` en Vercel apunte a la URL de Render con `https://` y sin
  barra al final.
- **"CORS" en la consola del navegador**: `ALLOWED_ORIGINS` en Render no
  coincide con la URL real de Vercel (mayúsculas, `www.`, barra final —
  tiene que ser EXACTA).
- **Tarda muchísimo la primera vez**: normal, el motor gratis se durmió.
  Solo la primera visita en un rato largo lo sufre.
- **500 al subir CV**: mirá los **Logs** del servicio en Render — casi
  siempre es una clave que falta o está mal copiada.

## Un dominio propio (opcional, no hace falta para publicar)

Tanto Vercel como Render aceptan agregar un dominio propio (tipo
`empatia-nextstep.com.ar`) desde su panel, gratis en la config — lo único
pago es comprar el dominio en sí (~USD 10-15/año). No es necesario para
tener el sitio funcionando en público; se puede sumar después.
