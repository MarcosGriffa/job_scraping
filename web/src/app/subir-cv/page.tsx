"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { uploadCvAndMatch } from "@/lib/api";
import { IconUpload } from "@/components/illustrations/icons";

const LOADING_MESSAGES = [
  "Leyendo tu CV...",
  "Entendiendo tu perfil y tu rubro...",
  "Buscando ofertas en varios portales...",
  "Analizando qué tan bien matcheás con cada una...",
  "Ya casi, preparando tu ranking...",
];

export default function SubirCvPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messageIndex, setMessageIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setMessageIndex((i) => Math.min(i + 1, LOADING_MESSAGES.length - 1));
    }, 6000);
    return () => clearInterval(interval);
  }, [loading]);

  function pickFile(f: File | null) {
    setError(null);
    if (f && !/\.(pdf|txt)$/i.test(f.name)) {
      setError("Subí un archivo PDF o .txt.");
      return;
    }
    setFile(f);
  }

  async function handleSubmit() {
    if (!file) {
      setError("Primero elegí tu CV.");
      return;
    }
    setError(null);
    setLoading(true);
    setMessageIndex(0);
    try {
      await uploadCvAndMatch(file);
      router.push("/resultados");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Algo salió mal. Probá de nuevo.");
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
        <div className="h-14 w-14 animate-spin rounded-full border-4 border-mustard border-t-transparent" />
        <p className="text-lg font-bold text-brown-title">{LOADING_MESSAGES[messageIndex]}</p>
        <p className="max-w-sm text-sm text-brown-body">
          Puede tardar un minuto o dos — estamos buscando en varios portales a la vez y
          dejando que la IA lea cada oferta con atención.
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-xl flex-1 flex-col justify-center px-6 py-16">
      <Link href="/" className="mb-8 text-sm font-semibold text-terracota">
        ← Volver
      </Link>

      <h1 className="text-3xl font-extrabold text-brown-title">Subí tu CV</h1>
      <p className="mt-2 text-brown-body">
        En PDF o texto. Lo leemos, entendemos tu perfil y buscamos las ofertas que mejor
        matchean con vos.
      </p>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          pickFile(e.dataTransfer.files?.[0] ?? null);
        }}
        onClick={() => inputRef.current?.click()}
        className={`mt-8 flex cursor-pointer flex-col items-center justify-center gap-3 rounded-3xl border-2 border-dashed p-12 text-center transition-colors ${
          dragOver ? "border-terracota bg-cream-soft" : "border-brown-title/25 bg-white"
        }`}
      >
        <IconUpload className="h-8 w-8 text-terracota" aria-label="Subir archivo" />
        {file ? (
          <p className="font-bold text-brown-title">{file.name}</p>
        ) : (
          <>
            <p className="font-bold text-brown-title">Arrastrá tu CV acá</p>
            <p className="text-sm text-brown-body">o hacé clic para elegirlo (PDF o .txt)</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt"
          className="hidden"
          onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {error && (
        <p className="mt-4 rounded-2xl border border-terracota/30 bg-terracota-tint/40 px-4 py-3 text-sm font-semibold leading-relaxed text-terracota-dark">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={handleSubmit}
        disabled={!file}
        className="mt-8 w-full rounded-full bg-terracota py-3 font-bold text-white transition-colors hover:bg-terracota-dark disabled:cursor-not-allowed disabled:opacity-40"
      >
        Buscar mi match
      </button>
    </main>
  );
}
