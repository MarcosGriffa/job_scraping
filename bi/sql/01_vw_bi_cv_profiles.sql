-- 01_vw_bi_cv_profiles.sql — Vista de análisis: un CV por fila, con el
-- jsonb "profile" ya aplanado a columnas.
--
-- Cómo correrla (igual que supabase/schema.sql): Supabase Dashboard ->
-- SQL Editor -> New query -> pegar -> Run. Es seguro correrla de nuevo
-- (CREATE OR REPLACE).
--
-- Solo lectura: no crea tablas ni modifica datos, así que no hace falta
-- tocar RLS. Power BI se conecta con las mismas credenciales que ya usa
-- el backend (api/), que saltan RLS por diseño (ver nota en schema.sql).
--
-- Forma parte del modelo de BI documentado en bi/README.md.

create or replace view vw_bi_cv_profiles as
select
  id                                    as cv_id,
  user_id,
  filename,
  profile ->> 'area'                    as area,
  (profile ->> 'is_tech')::boolean      as is_tech,
  profile ->> 'seniority'               as seniority,
  jsonb_array_length(coalesce(profile -> 'skills', '[]'::jsonb)) as cantidad_skills,
  created_at
from cv_profiles;
