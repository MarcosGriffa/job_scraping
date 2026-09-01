-- 03_vw_bi_ofertas.sql — Vista de análisis: una fila por cada oferta
-- evaluada en cada búsqueda (explota el array jsonb "results" de
-- match_results), cruzada con applied_jobs para saber si esa oferta
-- terminó realmente aplicada.
--
-- OJO: el campo "applied" que viaja DENTRO del jsonb de match_results
-- no sirve para esto — se escribe una sola vez al guardar la búsqueda
-- (siempre en false, ver api/matching.py) y solo se "parcha" al vuelo
-- cuando la API lo lee, sin persistirse. La fuente de verdad del estado
-- real es la tabla applied_jobs, que sí registra el evento con fecha.
-- Por eso esta vista hace el LEFT JOIN en vez de leer el campo del jsonb.
--
-- Cómo correrla: igual que las otras dos — SQL Editor de Supabase,
-- pegar, Run. Seguro correrla de nuevo.
--
-- Forma parte del modelo de BI documentado en bi/README.md.

create or replace view vw_bi_ofertas as
select
  mr.id                    as match_id,
  mr.user_id               as user_id,
  mr.cv_id                 as cv_id,
  mr.created_at            as fecha_busqueda,
  oferta ->> 'job_id'      as job_id,
  oferta ->> 'title'       as titulo,
  oferta ->> 'company'     as empresa,
  oferta ->> 'location'    as ubicacion,
  oferta ->> 'source'      as fuente,
  -- similarity nace como similitud coseno 0-1 (ver semantic_match.py), pero
  -- se expone en escala 0-100 igual que score, por dos razones:
  --   1. Deja las dos métricas del pipeline en la MISMA unidad, así el
  --      gráfico de dispersión "similarity vs score" se lee directo: los
  --      dos ejes van de 0 a 100 y la diagonal es "coinciden".
  --   2. Evita un decimal 0-1 que, exportado a CSV, cualquier herramienta
  --      con configuración regional española interpreta mal (lee el punto
  --      de "0.6511" como separador de miles y entiende 6511).
  round((oferta ->> 'similarity')::numeric * 100) as similarity,
  (oferta ->> 'score')::numeric      as score,
  jsonb_array_length(coalesce(oferta -> 'matches', '[]'::jsonb)) as cantidad_matches,
  jsonb_array_length(coalesce(oferta -> 'gaps', '[]'::jsonb))    as cantidad_gaps,
  coalesce(aj.applied, false) as aplicada,
  aj.applied_at               as aplicada_en
from match_results mr,
     jsonb_array_elements(mr.results) as oferta
left join applied_jobs aj
  on aj.user_id = mr.user_id
 and aj.job_id  = oferta ->> 'job_id'
where oferta ->> 'score' is not null;
