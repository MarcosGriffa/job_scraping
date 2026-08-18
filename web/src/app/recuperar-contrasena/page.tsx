"use client";

import { useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

export default function RecuperarContrasenaPage() {
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    const supabase = createClient();
    // Pasa por /auth/callback primero (mismo canje de código que login con
    // Google o confirmación de mail) y de ahí sigue a /actualizar-contrasena
    // ya con la sesión puesta — así no se duplica esa lógica acá.
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent("/actualizar-contrasena")}`,
    });
    setEnviando(false);
    if (error) {
      setError(error.message);
      return;
    }
    setEnviado(true);
  }

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
      <Link href="/login" className="mb-8 text-sm font-semibold text-terracota">
        ← Volver a iniciar sesión
      </Link>

      <h1 className="text-3xl font-extrabold text-brown-title">Recuperar contraseña</h1>

      {enviado ? (
        <p className="mt-4 text-brown-body">
          Si <strong className="text-brown-title">{email}</strong> tiene una cuenta, te mandamos un
          link para poner una contraseña nueva. Revisá tu bandeja de entrada.
        </p>
      ) : (
        <>
          <p className="mt-2 text-brown-body">Te mandamos un link a tu mail para elegir una nueva.</p>
          <form onSubmit={enviar} className="mt-8 flex flex-col gap-4">
            <label className="flex flex-col gap-1.5 text-sm font-semibold text-brown-title">
              Mail
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="rounded-xl border border-brown-title/20 bg-white px-4 py-2.5 text-base font-normal text-brown-title outline-none focus:border-olive"
                placeholder="vos@mail.com"
              />
            </label>

            {error && (
              <p className="rounded-2xl border border-terracota/30 bg-terracota-tint/40 px-4 py-3 text-sm font-semibold text-terracota-dark">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={enviando}
              className="mt-1 rounded-full bg-terracota py-3 font-bold text-white transition-colors hover:bg-terracota-dark disabled:cursor-not-allowed disabled:opacity-60"
            >
              {enviando ? "Enviando…" : "Mandar link"}
            </button>
          </form>
        </>
      )}
    </main>
  );
}
