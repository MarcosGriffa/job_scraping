"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import { IconGoogle, IconMail } from "./illustrations/icons";

// Traducciones de los mensajes de error más comunes de Supabase Auth — el
// resto se muestra tal cual vino (mejor un inglés ocasional que nada).
function traducirError(msg: string): string {
  if (/invalid login credentials/i.test(msg)) return "Mail o contraseña incorrectos.";
  if (/user already registered/i.test(msg)) return "Ya existe una cuenta con ese mail. Iniciá sesión.";
  if (/email not confirmed/i.test(msg)) return "Todavía no confirmaste tu mail. Revisá tu bandeja de entrada.";
  if (/password should be at least/i.test(msg)) return "La contraseña tiene que tener al menos 6 caracteres.";
  if (/unable to validate email/i.test(msg)) return "Ese mail no parece válido.";
  return msg;
}

export function AuthForm({ mode }: { mode: "login" | "signup" }) {
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") || "/";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [cargando, setCargando] = useState<"mail" | "google" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mailEnviado, setMailEnviado] = useState(false);

  async function conGoogle() {
    setError(null);
    setCargando("google");
    const supabase = createClient();
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}` },
    });
    if (error) {
      setError(traducirError(error.message));
      setCargando(null);
    }
    // si no hay error, el navegador ya está siendo redirigido a Google
  }

  async function conMail(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setCargando("mail");
    const supabase = createClient();

    if (mode === "signup") {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}` },
      });
      if (error) {
        setError(traducirError(error.message));
        setCargando(null);
        return;
      }
      setMailEnviado(true);
      setCargando(null);
      return;
    }

    // login
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setError(traducirError(error.message));
      setCargando(null);
      return;
    }
    router.push(next);
    router.refresh();
  }

  if (mailEnviado) {
    return (
      <div className="text-center">
        <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-olive-tint text-olive-dark">
          <IconMail className="h-7 w-7" />
        </span>
        <h2 className="mt-4 text-xl font-extrabold text-brown-title">Revisá tu mail</h2>
        <p className="mt-2 text-sm text-brown-body">
          Te mandamos un link a <strong className="text-brown-title">{email}</strong> para confirmar tu cuenta.
          Apenas lo abras, seguís justo donde estabas.
        </p>
      </div>
    );
  }

  return (
    <div>
      <button
        type="button"
        onClick={conGoogle}
        disabled={cargando !== null}
        className="flex w-full items-center justify-center gap-3 rounded-full border-2 border-brown-title/15 bg-white py-3 font-bold text-brown-title transition-colors hover:bg-cream-soft disabled:cursor-not-allowed disabled:opacity-60"
      >
        <IconGoogle className="h-5 w-5" />
        Continuar con Google
      </button>

      <div className="my-5 flex items-center gap-3 text-xs font-semibold text-brown-body/60">
        <span className="h-px flex-1 bg-brown-title/10" />O
        <span className="h-px flex-1 bg-brown-title/10" />
      </div>

      <form onSubmit={conMail} className="flex flex-col gap-4">
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

        <label className="flex flex-col gap-1.5 text-sm font-semibold text-brown-title">
          Contraseña
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

        {mode === "login" && (
          <Link href="/recuperar-contrasena" className="-mt-2 self-end text-xs font-semibold text-terracota">
            ¿Olvidaste tu contraseña?
          </Link>
        )}

        {error && (
          <p className="rounded-2xl border border-terracota/30 bg-terracota-tint/40 px-4 py-3 text-sm font-semibold leading-relaxed text-terracota-dark">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={cargando !== null}
          className="mt-1 rounded-full bg-terracota py-3 font-bold text-white transition-colors hover:bg-terracota-dark disabled:cursor-not-allowed disabled:opacity-60"
        >
          {cargando === "mail" ? "Un momento…" : mode === "signup" ? "Crear cuenta" : "Iniciar sesión"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-brown-body">
        {mode === "signup" ? (
          <>
            ¿Ya tenés cuenta?{" "}
            <Link href={`/login?next=${encodeURIComponent(next)}`} className="font-bold text-terracota">
              Iniciá sesión
            </Link>
          </>
        ) : (
          <>
            ¿No tenés cuenta?{" "}
            <Link href={`/crear-cuenta?next=${encodeURIComponent(next)}`} className="font-bold text-terracota">
              Creá una
            </Link>
          </>
        )}
      </p>

      {mode === "signup" && (
        <p className="mt-4 text-center text-xs text-brown-body/70">
          Al crear tu cuenta aceptás nuestra{" "}
          <Link href="/privacidad" className="font-semibold text-brown-body underline">
            Política de Privacidad
          </Link>
          .
        </p>
      )}
    </div>
  );
}
