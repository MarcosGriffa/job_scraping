import { IconMail } from "./illustrations/icons";

export function Contact() {
  return (
    <section id="contacto" className="mx-auto max-w-6xl px-6 py-16 text-center md:py-24">
      <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-olive-tint text-olive-dark">
        <IconMail className="h-8 w-8" />
      </span>
      <h2 className="mt-5 text-3xl font-extrabold text-brown-title">Contacto</h2>
      <p className="mx-auto mt-3 max-w-xl text-brown-body">
        ¿Tenés dudas, sugerencias o encontraste algo que no funciona? Escribinos.
      </p>
      <a
        href="mailto:marquitosgriffa@gmail.com"
        className="mt-6 inline-block rounded-full border-2 border-olive px-6 py-3 text-sm font-bold text-olive hover:bg-olive hover:text-white"
      >
        marquitosgriffa@gmail.com
      </a>
    </section>
  );
}
