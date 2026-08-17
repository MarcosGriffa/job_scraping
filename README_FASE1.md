# Fase 1 — Motor de matching universal CV ↔ Empleo

## 🆕 v1.4 — diseño real de dos columnas en los CV adaptados (11/08/2026)

Los primeros CVs generados por `cv_tailor.py` (v1.3) tenían texto plano,
una sola columna, sin colores — no se parecía en nada al diseño real de
Marcos (dos columnas, header navy, sidebar). Se reconstruyó a mano en
`render_cv_docx()` (no teníamos el archivo fuente de Canva, así que se
armó a partir de la descripción del diseño):

- Header de ancho completo con fondo navy (#1A1D2E): nombre en serif
  blanco itálica a la izquierda, datos de contacto alineados a la derecha
  con iconos (☎ ✉ ▪).
- Barra fina dorada (#F2C230) de acento debajo del header.
- Cuerpo a dos columnas (tabla 1x2 sin bordes, ~62%/38%): Perfil,
  Proyectos y Experiencia a la izquierda; Educación y Habilidades a la
  derecha.
- Habilidades como "pills" de color: las primeras (después del
  reordenamiento por IA para esa oferta puntual) en dorado, el resto en
  gris — es decir, el dorado ahora refleja qué skills la IA priorizó
  como más relevantes para ESA oferta, no una lista fija.
- Todo entra en **una sola página** A4.

Un bug real en el camino: el letter-spacing en los títulos de sección
("PROYECTOS DESTACADOS", etc.) hacía que Word cortara la palabra a la
mitad al ajustar el renglón en columnas angostas (ej. "PROYE CTOS
DESTACADOS"). Se sacó el letter-spacing por completo — se prefirió texto
legible antes que la estética del espaciado.

`render_cv_docx(cv_data, output_path)` es agnóstico de Groq/adaptación
— solo depende de la forma de `cv_data` — para poder reusarse con
cualquier CV a futuro. Por ahora el estilo (colores/tipografía) es fijo,
como "template default", porque es el único diseño de referencia que
tenemos. Si en algún momento aparece el archivo fuente original (Canva u
otro), se puede armar un segundo template sin tocar el resto del pipeline.

## v1.3 — cv_tailor.py: CVs adaptados por oferta, sin inventar nada (10/08/2026)

Nueva pieza del pipeline: `cv_tailor.py`. Reemplaza al `cv_adapter.py` viejo
(que estaba 100% hardcodeado al CV de Marcos: nombre, universidad, empresa
Ferrosider, proyectos, hobby de rugby, todo escrito a mano en el código, y
generaba el .docx llamando a Node.js). La versión nueva:

- Sirve para **cualquier CV**: detecta las secciones automáticamente (Perfil,
  Experiencia, Educación, Habilidades, etc.), sea cual sea el formato —
  incluso headers "espaciados letra por letra" como los que deja PyMuPDF al
  extraer ciertos PDFs (ej. `P E R F I L`).
- Usa el modelo CHICO de Groq (`llama-3.1-8b-instant`) para reordenar y
  reformular — no necesita el modelo grande, así no depende del cupo que se
  agota.
- Genera el .docx con `python-docx` (Python puro), no con Node.js.

**Lo más importante — la garantía de "no inventar nada" está scripteada, no
es solo una instrucción en el prompt**: cada reescritura de la IA pasa por
`_is_safe_rewrite()`, que compara las palabras de la versión adaptada contra
TODO el texto del CV original y, si aparece una sola palabra de contenido
que no estaba en ningún lado del CV, descarta la reescritura y usa el texto
original tal cual. Se ajustó a tolerancia CERO después de encontrar en una
prueba real que con 1 palabra de margen la IA cambió "Estudiante de Ciencia
de Datos" por "Analista de datos" en el perfil de Marcos — un cambio de una
sola palabra, pero que le inventaba un estatus laboral que no tiene. Con
tolerancia cero, el Perfil y los bullets de Experiencia (reescritura libre)
casi siempre quedan igual al original — es lo esperable y lo seguro; donde
sí se nota la adaptación real es en qué proyecto/skill aparece primero
(reordenamiento de líneas completas, sin reescribir palabras).

Cada .docx trae el dato de a qué aviso puntual corresponde: `Oferta: <título>
— <empresa>` y `Aplicar a esta oferta: <url>` (agregado el 10/08/2026 a
pedido — el .docx solo, sin esto, no decía para qué puesto se había
adaptado ni dónde aplicar). Al principio lo puse como pie de página al
final del documento, en letra chica — Marcos no lo vio (quedaba en una
página 2 fácil de no llegar a mirar en una vista previa rápida). Corregido
el 11/08/2026: ahora va arriba de todo, justo debajo del nombre y los
datos de contacto, en negrita.

Uso:
```
python cv_tailor.py CV_Marcos_Griffa_v3.pdf --top 10
```
Genera los .docx en `data/cvs_adaptados/<nombre_cv>/`.

## v1.2 — corrida en la máquina con internet real (10/08/2026)

Primera vez que se pudo correr todo contra los sitios reales. Resultado de
`debug_sources.py` y de probar cada fuente en vivo:

- ✅ **Confirmado con CV de ventas**: `pipeline.py test_cvs/cv_ventas.txt`
  detecta bien el área ("Ventas"), NO activa las fuentes tech, y los
  matches son todos de atención al cliente/retail/ventas, con scores
  80-90/100. El motor generaliza bien a un rubro no-IT.
- ❌ **Multitrabajos y Konzerta: dados de baja, no es cuestión de selectores**.
  Confirmé que el HTML que baja `requests()` es un loader vacío (como ya
  sabíamos) pero además encontré, navegando cada sitio como usuario real:
  - **Multitrabajos es de Ecuador**, no de Argentina ("Trabajos en Ecuador -
    Empleos Multitrabajos 2020"). No existe `multitrabajos.com.ar` ni
    subdominio `ar.`.
  - **Konzerta es de Panamá** ("Hay 2.634 trabajos esperándote en Panamá").
    Tampoco existe versión argentina.
  - Las dos SÍ tienen una API JSON real detrás del loader (ej.
    `/api/avisos/searchV2` en Multitrabajos), pero está protegida por
    Cloudflare y devuelve 403 a cualquier pedido que no venga de un
    navegador real — y aunque se pudiera sortear eso, seguirían siendo
    ofertas de otro país.
  - Conclusión: quedan comentadas en `pipeline.py` (`GENERAL_SOURCES`).
    No vale la pena seguir invirtiendo tiempo acá.
- ✅ **Himalayas arreglado**: el endpoint viejo (`/api/jobs`) daba 404 — Himalayas
  lo movió a `/jobs/api`. Además esa API ignora los parámetros de búsqueda
  por palabra clave y solo devuelve los avisos más recientes (máx. 20 por
  página), así que ahora se paginan ~200 avisos recientes con `offset` y
  se filtra localmente por la query, como ya hacía el resto del filtro.
- ✅ **Bug de "company" vacío en Computrabajo, encontrado y arreglado**: pasaba
  en avisos anónimos (Computrabajo muestra el texto "Importante empresa del
  sector" en vez del nombre) o publicados por consultoras que no linkean su
  perfil (ej. "Hand Selection") — en esos casos el nombre viene como texto
  suelto sin ningún link, y el selector solo buscaba links. Ahora hay un
  último fallback que toma el texto completo del párrafo de la empresa.
  Verificado con un caso real que antes quedaba vacío (oferta de Cipolletti,
  ahora muestra "Importante empresa del sector").

## v1.1 — arreglos después de la primera corrida real

Tu primera corrida con tu CV real funcionó muy bien en lo central (scores
80-90/100, explicaciones coherentes). Esto es lo que se arregló:

- ✅ **Queries en inglés para portales tech en inglés**: RemoteOK, Jobicy y
  WeWorkRemotely daban 0 resultados porque buscaban en español. Ahora el
  clasificador de CV genera también `search_queries_en` (solo si tu área es
  tech) y esas fuentes usan esas queries en inglés.
- ✅ **Bug de "Postular" como nombre de empresa**: en Computrabajo, a veces
  el campo empresa mostraba el texto del botón "Postular" en vez del
  nombre real. Corregido — ahora descarta esos textos y busca el próximo
  candidato válido.
- ✅ **Deduplicación mejorada**: antes solo deduplicaba por URL exacta, así
  que la misma oferta con distinto hash de tracking aparecía repetida
  varias veces en el top. Ahora también deduplica por título+empresa
  normalizados.
- 🔧 **Pendiente, necesita datos en vivo**: Multitrabajos y Konzerta seguían
  en 0 resultados, y Himalayas tira 404. Agregué `debug_sources.py` — un
  script de diagnóstico que corré una sola vez y me pasás la salida
  completa, así te doy el fix exacto sin tener que adivinar selectores.

### Corré el diagnóstico así:
```
python debug_sources.py
```
Copiá TODO lo que imprime en la consola y pasámelo.

---


Esto es la evolución del "Observatorio IT Junior": ahora el sistema lee
CUALQUIER CV (no solo IT), entiende automáticamente de qué rubro es la
persona, busca en varios portales de empleo, y arma un ranking explicado
usando IA — no keywords.

## Qué se construyó

```
CV (PDF o texto)
     │
     ▼
cv_profile.py ──► Groq lee el CV y devuelve:
     │              área, si es tech o no, seniority, skills, 
     │              y 3-5 términos de búsqueda para portales
     ▼
pipeline.py ──► corre las búsquedas en los portales correspondientes
     │            (generales siempre + tech solo si is_tech=true)
     ▼
semantic_match.py ──► ETAPA 1: embeddings, filtra por cercanía de
     │                          significado (rápido y gratis)
     │                ETAPA 2: IA lee CV + oferta de las finalistas
     │                          y explica el match de verdad
     ▼
data/resultados_<cv>.json y .csv
```

## Portales conectados

**Generales (siempre, cualquier rubro):**
- Computrabajo (ya lo tenías, migrado a la interfaz nueva) — ✅ funciona bien
- Jooble — ✅ activo desde el 13/08/2026. Metabuscador (junta avisos de
  muchos portales), apuntado a `ar.jooble.org`, así que trae ofertas
  argentinas de cualquier rubro. **Ojo con el cupo**: el plan gratuito son
  500 consultas *en total, de por vida* (no por mes), y cada CV que
  alguien sube gasta ~5 — o sea alcanza para unos 100 CVs. Cuando se
  agote, la fuente va a devolver 0 sin romper nada, pero conviene tenerlo
  en el radar. Detalle en `sources/jooble.py`.
- ~~Multitrabajos~~ y ~~Konzerta~~ — ❌ dadas de baja (10/08/2026): son de
  Ecuador y Panamá respectivamente, no de Argentina. Ver changelog v1.2.

**Vertical tech (solo si el CV es de IT/tech):**
- RemoteOK, Jobicy, Himalayas, WeWorkRemotely — todos con API/RSS oficial,
  más estables que el scraping HTML. Himalayas arreglado en v1.2.

No se sumó Clarín Empleos: no pude confirmar si comparte infraestructura
con Zonajobs/Bumeran (que decidimos evitar). Antes de sumarlo habría que
verificarlo.

## ⚠️ Importante — qué falta probar

Mi entorno de trabajo no tiene salida a internet hacia estos portales,
así que armé todo con buenas prácticas pero **sin poder probar en vivo**
contra los sitios reales. Lo que SÍ probé y funciona:

- El CV se lee bien (PDF y texto), en los dos idiomas de prueba (tu CV
  real + un CV ficticio de ventas, para confirmar que generaliza)
- Toda la orquestación (clasificar → buscar → rankear → guardar) corre
  sin errores con datos simulados
- Los 7 conectores de portales importan y tienen la estructura correcta

Lo que falta validar en tu compu, con internet real:
- Que Groq devuelva el JSON esperado del CV (necesita tu GROQ_API_KEY)
- Que los scrapers de Multitrabajos y Konzerta encuentren las tarjetas de
  ofertas (si no, van a imprimir un `[WARN]` claro para poder ajustar el
  selector — mismo patrón de diagnóstico que ya tenía tu scraper de
  Computrabajo)
- Que las APIs de RemoteOK/Jobicy/Himalayas/WWR respondan con el formato
  esperado

Es normal que la primera corrida real tenga 1-2 ajustes de este tipo —
te vas a dar cuenta enseguida por los mensajes en la consola, y me los
pasás para que los arregle.

## Cómo correrlo (copiá y pegá, no hace falta editar nada)

1. Instalá las dependencias:
```
pip install -r requirements.txt
```
(La primera vez va a bajar el modelo de embeddings, ~400MB, tarda unos minutos)

2. Creá tu archivo `.env` a partir de `.env.example` y poné tu `GROQ_API_KEY`
   (gratis en console.groq.com)

3. Corré el motor con tu CV:
```
python pipeline.py test_cvs/cv_marcos.txt
```

4. Para probar que generaliza a otro rubro:
```
python pipeline.py test_cvs/cv_ventas.txt
```

5. Para usar tu CV real en PDF en vez del .txt de prueba, copiá el PDF a
   la carpeta del proyecto y corré:
```
python pipeline.py tu_cv.pdf
```

Los resultados quedan en `data/resultados_<nombre>.json` y `.csv`.

## Qué NO es parte de esta fase (a propósito)

Nada de web, login, membresía, Mercado Pago, ni branding — eso es Fase 2+
como charlamos. Esto es el "cerebro" nomás, corriendo por consola.
