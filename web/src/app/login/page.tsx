import { Suspense } from "react";
import Link from "next/link";
import { AuthForm } from "@/components/AuthForm";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const { error } = await searchParams;

  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
      <Link href="/" className="mb-8 text-sm font-semibold text-terracota">
        ← Volver
      </Link>

      <h1 className="text-3xl font-extrabold text-brown-title">Iniciá sesión</h1>
      <p className="mt-2 text-brown-body">Para ver tus matches y seguir donde dejaste.</p>

      {error && (
        <p className="mt-4 rounded-2xl border border-terracota/30 bg-terracota-tint/40 px-4 py-3 text-sm font-semibold leading-relaxed text-terracota-dark">
          {error}
        </p>
      )}

      <div className="mt-8">
        <Suspense>
          <AuthForm mode="login" />
        </Suspense>
      </div>
    </main>
  );
}
