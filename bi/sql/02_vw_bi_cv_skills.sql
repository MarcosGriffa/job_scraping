-- 02_vw_bi_cv_skills.sql — Vista de análisis: una fila por cada skill de
-- cada CV (explota el array jsonb "profile.skills"). Sirve para rankear
-- las skills más comunes entre los CVs subidos.
--
-- Cómo correrla: igual que 01_vw_bi_cv_profiles.sql — SQL Editor de
-- Supabase, pegar, Run. Seguro correrla de nuevo.
--
-- Forma parte del modelo de BI documentado en bi/README.md.

create or replace view vw_bi_cv_skills as
select
  cv.id      as cv_id,
  cv.user_id as user_id,
  skill.value as skill
from cv_profiles cv,
     jsonb_array_elements_text(coalesce(cv.profile -> 'skills', '[]'::jsonb)) as skill(value);
