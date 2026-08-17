"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getLatestResults } from "@/lib/api";
import type { JobResult } from "@/lib/types";
import { PillButton } from "./PillButton";
import {
  IconPin,
  IconTech,
  IconCommerce,
  IconHealth,
  IconScience,
  IconAdmin,
  IconMatch,
} from "./illustrations/icons";

/**
 * FeaturedJobs — "Oportunidades destacadas del día".
 *
 * v2 (13/08): conectada a DATOS REALES. Si esta persona (id anónimo en
 * cookie) ya subió un CV, se muestran sus mejores matches reales — los
 * mismos que guarda el pipeline en Supabase — priorizando las ofertas que
 * todavía no marcó como aplicadas. Si nunca subió un CV, se muestran
 * ejemplos ilustrativos claramente rotulados como tales (empresas
 * ficticias "Empresa Ejemplo ..."), nunca datos inventados con apariencia
 * de reales.
 *
 * Nota: el pipeline no extrae salario de los portales, así que en vez del
 * "Salario" del mockup mostramos el puntaje de compatibilidad, que es el
 * dato real que sí tenemos.
 */

const FEATURED_COUNT = 3;

const placeholderJobs = [
  {
    Icon: IconTech,
    iconBg: "bg-terracota",
    role: "Desarrollador/a Full-Stack",
    company: "Empresa Ejemplo Tech",
    location: "Buenos Aires (o remoto)",
  },
  {
    Icon: IconCommerce,
    iconBg: "bg-olive",
    role: "Gerente de Ventas B2B",
    company: "Empresa Ejemplo Comercial",
    location: "Ciudad de México",
  },
  {
    Icon: IconHealth,
    iconBg: "bg-mustard",
    role: "Médico/a — Telemedicina",
    company: "Empresa Ejemplo Salud",
    location: "Remoto",
  },
];

const ICON_BGS = ["bg-terracota", "bg-olive", "bg-mustard"];

function iconForTitle(title: string) {
  const t = title.toLowerCase();
  if (/(salud|enfermer|m[eé]dic|cl[ií]nic|farmac)/.test(t)) return IconHealth;
  if (/(desarroll|program|software|python|data|sistem|full.?stack|backend|frontend|devops)/.test(t)) return IconTech;
  if (/(venta|comercial|retail|atenci[oó]n)/.test(t)) return IconCommerce;
  if (/(biolog|laborator|cient|qu[ií]mic|investigaci)/.test(t)) return IconScience;
  if (/(administra|contab|finanz|gesti[oó]n|planeamiento)/.test(t)) return IconAdmin;
  return IconMatch;
}

export function FeaturedJobs() {
  // undefined = todavía cargando; null = no hay corrida previa
  const [jobs, setJobs] = useState<JobResult[] | null | undefined>(undefined);

  useEffect(() => {
    getLatestResults()
      .then((data) => {
        if (!data || data.results.length === 0) {
          setJobs(null);
          return;
        }
        // Primero las no aplicadas (ya vienen ordenadas por score del pipeline)
        const pending = data.results.filter((r) => !r.applied);
        const pick = (pending.length > 0 ? pending : data.results).slice(0, FEATURED_COUNT);
        setJobs(pick);
      })
      // Si el backend no está corriendo, caemos a los ejemplos sin romper la landing
      .catch(() => setJobs(null));
  }, []);

  const hasReal = Array.isArray(jobs) && jobs.length > 0;

  return (
    <section className="mx-auto max-w-4xl px-6 py-16 md:py-20">
      <h2 className="text-center text-3xl font-extrabold uppercase tracking-wide text-brown-title">
        Oportunidades destacadas del día
      </h2>
      <p className="mx-auto mt-3 max-w-lg text-center text-sm text-brown-body">
        {hasReal
          ? "Tus mejores matches según tu último CV — el ranking completo, con la explicación de cada uno, está en tus resultados."
          : "Ejemplos del tipo de oportunidades que vas a encontrar — tu propio ranking, con ofertas reales, se arma en cuanto subís tu CV."}
      </p>

      <div className="mt-8 flex flex-col gap-4">
        {hasReal
          ? jobs.map((job, i) => {
              const Icon = iconForTitle(job.title);
              return (
                <a
                  key={job.job_id}
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-4 rounded-2xl border border-brown-title/10 bg-white p-5 transition-colors hover:border-terracota/40"
                >
                  <span
                    className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-xl text-white ${ICON_BGS[i % ICON_BGS.length]}`}
                  >
                    <Icon className="h-7 w-7" />
                  </span>
                  <div className="min-w-0">
                    <p className="truncate font-bold text-brown-title">{job.title}</p>
                    <p className="truncate text-sm text-brown-body">{job.company}</p>
                    {job.location && (
                      <p className="mt-0.5 flex items-center gap-1 text-sm text-brown-body">
                        <IconPin className="h-3.5 w-3.5 shrink-0" />
                        <span className="truncate">{job.location}</span>
                      </p>
                    )}
                    {job.score !== undefined && (
                      <p className="mt-0.5 text-sm text-brown-body">
                        <span className="font-bold text-brown-title">Compatibilidad:</span> {job.score}/100
                      </p>
                    )}
                  </div>
                </a>
              );
            })
          : placeholderJobs.map((job) => (
              <div
                key={job.role}
                className="flex items-center gap-4 rounded-2xl border border-brown-title/10 bg-white p-5"
              >
                <span className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-xl text-white ${job.iconBg}`}>
                  <job.Icon className="h-7 w-7" />
                </span>
                <div>
                  <p className="font-bold text-brown-title">{job.role}</p>
                  <p className="text-sm text-brown-body">{job.company}</p>
                  <p className="mt-0.5 flex items-center gap-1 text-sm text-brown-body">
                    <IconPin className="h-3.5 w-3.5" />
                    {job.location}
                  </p>
                </div>
              </div>
            ))}
      </div>

      <div className="mt-8 text-center">
        {hasReal ? (
          <PillButton href="/resultados" variant="outline">
            Ver todos tus matches →
          </PillButton>
        ) : (
          <PillButton href="/subir-cv">Subí tu CV y armá tu ranking →</PillButton>
        )}
      </div>
    </section>
  );
}
