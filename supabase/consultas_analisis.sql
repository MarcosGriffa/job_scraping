-- consultas_analisis.sql — "recetas" para el SQL Editor de Supabase.
--
-- Cómo usarlas (una vez por consulta):
--   1. Supabase Dashboard -> SQL Editor -> New query
--   2. Pegar UNA de las consultas de abajo (son 3, independientes)
--   3. Run
--   4. Botón "Save query" (arriba a la derecha) para guardarla como
--      favorita — después aparece en la lista de la izquierda y se
--      vuelve a correr con un clic, sin pegar nada de nuevo.
--
-- No hace falta entender el SQL para usarlas — están comentadas para
-- quien quiera mirar, pero alcanza con copiar/pegar/Run.


-- ════════════════════════════════════════════════════════════════
-- 1) RUBROS MÁS COMUNES
-- Cuenta cuántos CVs se clasificaron en cada área (Data/Analytics,
-- Ventas, Salud, etc.), de más a menos común.
-- ════════════════════════════════════════════════════════════════
select
  profile ->> 'area' as rubro,
  count(*)            as cantidad_de_cvs
from cv_profiles
where profile ->> 'area' is not null
group by rubro
order by cantidad_de_cvs desc;


-- ════════════════════════════════════════════════════════════════
-- 2) BÚSQUEDAS POR DÍA
-- Cuántas veces se corrió el matching completo (subida de CV) cada
-- día — el pulso de uso del sitio, día a día.
-- ════════════════════════════════════════════════════════════════
select
  date(created_at) as dia,
  count(*)          as busquedas
from match_results
group by dia
order by dia desc;


-- ════════════════════════════════════════════════════════════════
-- 3) PROMEDIO DE SCORE (puntaje de compatibilidad)
-- Cada búsqueda guarda hasta 10 ofertas, cada una con su puntaje
-- 0-100. Esta consulta "abre" esa lista y promedia todos los
-- puntajes de todas las búsquedas juntas — sirve para ver si, en
-- general, el matching encuentra ofertas bien compatibles o no.
-- ════════════════════════════════════════════════════════════════
select
  round(avg((oferta ->> 'score')::numeric), 1) as promedio_score,
  count(*)                                      as ofertas_consideradas
from match_results,
     jsonb_array_elements(results) as oferta
where oferta ->> 'score' is not null;


-- ────────────────────────────────────────────────────────────────
-- Bonus (no pedida, pero natural combinación de las dos primeras):
-- promedio de score POR rubro, para ver si el matching funciona
-- mejor en algunas áreas que en otras.
-- ────────────────────────────────────────────────────────────────
-- select
--   cv.profile ->> 'area'                          as rubro,
--   round(avg((oferta ->> 'score')::numeric), 1)    as promedio_score,
--   count(*)                                        as ofertas
-- from match_results mr
-- join cv_profiles cv on cv.id = mr.cv_id,
--      jsonb_array_elements(mr.results) as oferta
-- where oferta ->> 'score' is not null
-- group by rubro
-- order by promedio_score desc;
