# Fase 2 — "EmpatÍA | NextStep": el motor de matching, ahora como web

La Fase 1 (ver `README_FASE1.md`) construyó el "cerebro" — el motor que lee
un CV, entiende el rubro, busca ofertas en varios portales y arma un
ranking explicado con IA — y corría por consola. Esta fase le pone una cara
de verdad: subís tu CV desde el navegador, ves los resultados en una
página linda, y marcás las que ya aplicaste.

**No se tocó nada del motor** (`cv_profile.py`, `semantic_match.py`,
`pipeline.py`, `sources/`, `cv_tailor.py`) — la web lo llama, no lo
reemplaza.

---

## 🚀 Cómo arrancarlo (la forma fácil)

**Doble clic en `INICIAR_WEB.bat`.** Listo.

Ese archivo levanta las dos piezas que hacen falta y abre el navegador
solo. Vas a ver aparecer **dos ventanas negras** — son el motor y la web
funcionando; déjalas abiertas mientras usás el sitio.

Para **apagar todo**: cerrá esas dos ventanas negras.

> La primera vez puede tardar unos minutos (instala dependencias). Las
> veces siguientes arranca en segundos.

Si algo falla, el .bat te dice qué falta en castellano (Python, Node.js o
el archivo `.env`).

> ⚠️ **Si hay que tocar `INICIAR_WEB.bat`, no lo edites a mano.** Los
> archivos `.bat` son muy quisquillosos: si les entra una letra con acento
> o se guardan con finales de línea de Linux, Windows ejecuta los comandos
> partidos por la mitad y todo falla con errores incomprensibles (ya nos
> pasó). Editá `tools/generar_bat.py` y corré `python tools/generar_bat.py`,
> que lo regenera con el formato correcto y valida que haya quedado bien.
> Para probarlo sin abrir ventanas: `python tools/probar_bat.py`.

### La forma manual (si el .bat falla o querés ver los errores)

Dos terminales, a la vez. En la primera, el motor:

```
python -m uvicorn api.main:app --reload --port 8000
```

Se corre **desde la carpeta raíz del proyecto** (`job_scraping/`), no desde
adentro de `api/`. Si ves esto, quedó bien:

```
[storage] backend de persistencia activo: supabase
Uvicorn running on http://127.0.0.1:8000
```

En la segunda, la web:

```
npm --prefix web run dev
```

Y entrás a **http://localhost:3000**.

---

## Cómo está armado

```
Navegador (Next.js, carpeta web/)
     │  subís el CV, ves los resultados, tildás "ya apliqué"
     ▼
API web (FastAPI, carpeta api/) ──► llama al motor existente:
     │                                cv_profile.py, pipeline.py,
     │                                semantic_match.py (sin tocarlos)
     ▼
Supabase (base de datos real en la nube)
     guarda: CVs subidos, resultados de cada búsqueda,
             qué ofertas marcaste como "ya aplicado"
```

Piezas nuevas de esta fase:

- **`web/`** — la página (Next.js). Landing + "subir tu CV" + "tus matches".
- **`api/`** — la API que conecta la web con el motor de Python y con la
  base de datos. Corre aparte, con FastAPI.
- **`supabase/schema.sql`** — el "molde" de las 3 tablas de la base de
  datos (ya corrido una vez en el proyecto de Supabase).
- **`INICIAR_WEB.bat`** — el arranque de un solo clic.

---

## Qué tiene la web hoy

### La página principal

Diseñada a partir de los bocetos que fue mandando Marcos, con paleta
cálida (crema, terracota, oliva, mostaza). Secciones, de arriba a abajo:

1. **Portada** — título, buscador y una composición tipo "mapa mental":
   tres profesionales ilustrados (salud, tecnología, comercio) conectados
   por líneas al logo central "TUS MATCHES".
2. **Cómo funciona el match de EmpatÍA** — tres tarjetas grandes de
   colores explicando los pasos, con ilustraciones propias.
3. **Oportunidades destacadas del día** — si ya subiste un CV, muestra
   **tus tres mejores matches reales** con su puntaje; si todavía no
   subiste ninguno, muestra ejemplos aclarando que lo son.
4. **Historias de éxito** — tres testimonios.
5. **Alcance global de oportunidades** — mapamundi con pines.
6. **Contacto** y **pie de página**.

Detalle de estilo, decidido con Marcos: **no hay ni un emoji** en toda la
página. Todos los iconitos e ilustraciones son dibujos propios hechos a
medida (viven en `web/src/components/illustrations/`), para que todo tenga
el mismo aire.

### Las tres pantallas

- **`/`** — la página principal de arriba.
- **`/subir-cv`** — subís el CV (PDF o texto). Mientras se procesa (tarda
  1 o 2 minutos: busca en los portales y usa IA varias veces) se ve una
  pantalla de carga con mensajes de progreso.
- **`/resultados`** — la lista de ofertas rankeadas, con puntaje, por qué
  matchea (o no), el botón **"Generar CV para esta oferta"** y el checkbox
  **"Marcar como aplicado"**. Al tildarlo el título se tacha y aparece el
  cartel "Ya aplicaste".

### El CV adaptado a cada oferta

En cada oferta hay un botón **"Generar CV para esta oferta"**. Al apretarlo
se arma un CV adaptado a ese aviso puntual (unos 5-10 segundos) y se
descarga en Word.

Dos cosas pensadas a propósito:

- **No se genera nada hasta que lo pedís.** Antes, el generador armaba los
  10 CVs de una apenas terminaba la búsqueda: se gastaba tiempo y llamadas
  a la IA en CVs que nadie iba a mirar. Ahora se arma solo el que pediste.
- **Queda guardado.** Si volvés a apretar el mismo botón, te lo da al
  instante sin rehacerlo. Y si subís un CV nuevo, se regenera solo (porque
  cambió el CV de origen), así nunca te baja una versión vieja.

El archivo se descarga con el nombre de la oferta
(`CV_Analista_de_Datos_NombreEmpresa.docx`), así no se te mezclan.

> Sale en **Word**, no en PDF, decidido así por ahora: te deja retocarlo
> antes de mandarlo. Si en algún momento se rompe el encuadre del diseño
> (ya pasó una vez con el espaciado), ahí conviene pasar a PDF.

---

## Cómo se acuerda de vos sin pedirte cuenta

Todavía no hay usuario y contraseña. En su lugar, la primera vez que
entrás el navegador guarda un **código anónimo en una cookie** (dura un
año). Ese código es el que ata tus resultados y tus "ya apliqué".

Consecuencias prácticas, para que no te sorprenda:

- Si volvés **desde el mismo navegador**, tus resultados siguen ahí.
- Si entrás **desde otra computadora o navegador**, arranca de cero.
- Si borrás las cookies, arranca de cero.

Cuando llegue el login de verdad, ese código se reemplaza por el usuario
real sin tener que rehacer nada: tanto la API como la base ya están
preparadas para recibir cualquier identificador.

---

## La base de datos (Supabase)

Está **conectada y funcionando** con el proyecto real de Supabase
(`SUPABASE_URL` y las dos claves viven en el `.env`, que **nunca** se sube
al repositorio). Se guardan tres cosas:

- **`cv_profiles`** — cada CV que se sube y cómo lo clasificó la IA.
- **`match_results`** — el resultado de cada búsqueda (las ofertas
  rankeadas).
- **`applied_jobs`** — qué ofertas marcaste como "ya aplicado". El motor
  las **excluye automáticamente** en búsquedas futuras (no tiene sentido
  gastar IA explicando una oferta a la que ya aplicaste). Esto está
  probado: en una corrida nueva no volvió a aparecer ninguna de las
  marcadas.

Las tablas se crearon una sola vez pegando `supabase/schema.sql` en el
**SQL Editor** del panel de Supabase. Si algún día hiciera falta rehacerlas,
se puede volver a pegar: no borra nada si ya existen.

Si algún día se quiere probar sin Supabase (por ejemplo sin internet),
alcanza con vaciar esas tres variables del `.env`: el sistema cae solo a
guardar en archivos locales, sin tocar una línea de código.

---

## De dónde salen las ofertas

**Fuentes generales** (siempre, cualquier rubro):

- **Computrabajo**
- **Jooble** (agregado 13/08/2026) — es un metabuscador: junta avisos de
  muchos portales a la vez, apuntado al sitio argentino. Casi duplicó la
  cantidad de ofertas que ve el motor.

**Fuentes de tecnología** (solo si el CV es de sistemas): RemoteOK, Jobicy,
Himalayas, WeWorkRemotely.

> ⚠️ **Ojo con el cupo de Jooble.** Su plan gratuito permite **500
> consultas en total, de por vida** (no por mes). Cada CV que alguien sube
> gasta unas 5, así que alcanza para unos 100 CVs. Cuando se agote, Jooble
> va a devolver cero ofertas **sin romper nada** (el resto de las fuentes
> sigue funcionando igual), pero conviene tenerlo en el radar si el sitio
> empieza a tener usuarios de verdad.

---

## Un par de problemas reales que aparecieron (y cómo se resolvieron)

Quedan anotados porque son el tipo de cosa que vuelve a morder:

- **Las búsquedas devolvían cero desde la web, pero funcionaban por
  consola.** Windows, al correr el motor "por detrás" de la web, usaba una
  codificación vieja que no sabe escribir la flecha `→` que el motor
  imprime para mostrar el progreso. Cada búsqueda moría en silencio. Se
  arregló forzando UTF-8 al arrancar la API (y también en el .bat).

- **Las ilustraciones no se veían.** La versión nueva de Next.js cambió un
  ajuste de seguridad y servía las imágenes como "descarga" en vez de
  mostrarlas. Se corrigió en `web/next.config.ts`.

- **La primera clave de Jooble no servía.** Era del sitio de Estados
  Unidos: devolvía miles de avisos pero todos de allá, y cero al filtrar
  por Argentina. La API es **por país** — la clave hay que sacarla
  entrando desde `ar.jooble.org`.

---

## Qué falta (a propósito)

- **Publicarla en internet.** Hoy todo corre en la computadora de Marcos.
  Cuando se haga: la web (Next.js) va derecho a Vercel, pero **el motor
  Python no entra ahí** — cada búsqueda tarda 1-2 minutos y Vercel corta a
  los 10 segundos. Necesita un hosting aparte (Render o Railway tienen
  plan gratis para empezar).
- **Login de verdad** — hoy cada navegador se identifica solo, sin cuenta.
