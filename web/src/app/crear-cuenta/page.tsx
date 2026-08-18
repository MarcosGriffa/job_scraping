import { Suspense } from "react";
import Link from "next/link";
import { AuthForm } from "@/components/AuthForm";

export default function CrearCuentaPage() {
  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
      <Link href="/" className="mb-8 text-sm font-semibold text-terracota">
        ← Volver
      </Link>

      <h1 className="text-3xl font-extrabold text-brown-title">Creá tu cuenta</h1>
      <p className="mt-2 text-brown-body">
        La necesitás para subir tu CV y ver tus matches — así podés entrar desde cualquier
        dispositivo y no perdés nada.
      </p>

      <div className="mt-8">
        <Suspense>
          <AuthForm mode="signup" />
        </Suspense>
      </div>
    </main>
  );
}
