"use client";

import { useRouter } from "next/navigation";
import { IconMatch } from "./illustrations/icons";

/**
 * SearchBar — barra de búsqueda del hero (vuelve por pedido de Marcos con
 * el mockup completo del 13/08; se había sacado porque el producto no
 * busca por palabra clave). Sigue sin haber búsqueda real detrás: el
 * submit lleva al flujo de subir CV, que es donde de verdad empieza el
 * matching. Cuando exista búsqueda por keyword, se conecta acá.
 */
export function SearchBar() {
  const router = useRouter();

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        router.push("/subir-cv");
      }}
      className="mt-6 flex w-full max-w-xl items-center gap-2 rounded-full border border-brown-title/15 bg-white p-1.5 pl-4"
    >
      <IconMatch className="h-4.5 w-4.5 shrink-0 text-brown-body/60" aria-hidden="true" />
      <input
        type="text"
        placeholder='Busca "Analista de Datos Senior", "Gerente de Ventas", "Ingeniero Agrónomo"...'
        className="w-full min-w-0 bg-transparent text-sm text-brown-title placeholder:text-brown-body/60 focus:outline-none"
      />
      <button
        type="submit"
        className="shrink-0 rounded-full bg-mustard px-5 py-2 text-sm font-bold text-white transition-colors hover:bg-terracota"
      >
        Buscar
      </button>
    </form>
  );
}
