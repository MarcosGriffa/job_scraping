import Link from "next/link";
import type { ReactNode } from "react";

type Variant = "solid" | "outline";

const base =
  "inline-flex items-center justify-center gap-2 rounded-full px-6 py-3 font-bold text-sm transition-colors";

const variants: Record<Variant, string> = {
  solid: "bg-terracota text-white hover:bg-terracota-dark",
  outline: "border-2 border-terracota text-terracota hover:bg-terracota hover:text-white",
};

export function PillButton({
  href,
  children,
  variant = "solid",
  className = "",
}: {
  href: string;
  children: ReactNode;
  variant?: Variant;
  className?: string;
}) {
  return (
    <Link href={href} className={`${base} ${variants[variant]} ${className}`}>
      {children}
    </Link>
  );
}
