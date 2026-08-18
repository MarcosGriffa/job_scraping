"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

// Llegar acá con sesión activa es lo esperado: pasó antes por
// /auth/callback, que ya canjeó el link del mail por una sesión real.
export default function ActualizarContrasenaPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [listo, setListo] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function guardar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setGuardando(true);
    const supabase = createClient();
    const { error } = await supabase.auth.updateUser({ password });
    setGuardando(false);
    if (error) {
      setError(error.message);
      return;
    }
    setListo(true);
    setTimeout(() => router.push("/"), 1800);
  }

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
      <h1 className="text-3xl font-extrabold text-brown-title">Nueva contraseña</h1>

      {listo ? (
        <p className="mt-4 text-brown-body">Listo, ya está actualizada. Te llevamos al inicio…</p>
      ) : (
        <>
          <p className="mt-2 text-brown-body">Elegí una contraseña nueva para tu cuenta.</p>
          <form onSubmit={guardar} className="mt-8 flex flex-col gap-4">
            <label className="flex flex-col gap-1.5 text-sm font-semibold text-brown-title">
              Contraseña nueva
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="rounded-xl border border-brown-title/20 bg-white px-4 py-2.5 text-base font-normal text-brown-title outline-none focus:border-olive"
                placeholder="••••••••"
              />
            </label>

            {error && (
              <p className="rounded-2xl border border-terracota/30 bg-terracota-tint/40 px-4 py-3 text-sm font-semibold text-terracota-dark">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={guardando}
              className="mt-1 rounded-full bg-terracota py-3 font-bold text-white transition-colors hover:bg-terracota-dark disabled:cursor-not-allowed disabled:opacity-60"
            >
              {guardando ? "Guardando…" : "Guardar contraseña"}
            </button>
          </form>
        </>
      )}
    </main>
  );
}
