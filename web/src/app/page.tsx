import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";
import { FeaturedJobs } from "@/components/FeaturedJobs";
import { Testimonials } from "@/components/Testimonials";
import { WorldMapSection } from "@/components/WorldMapSection";
import { Contact } from "@/components/Contact";
import { Footer } from "@/components/Footer";

// Orden según el mockup completo de Marcos (13/08): hero con búsqueda →
// cómo funciona → oportunidades del día → historias de éxito → alcance
// global → contacto → footer navy. La sección "Destacados" vieja quedó
// reemplazada por FeaturedJobs.
export default function Home() {
  return (
    <>
      <Header />
      <main className="flex-1">
        <Hero />
        <HowItWorks />
        <FeaturedJobs />
        <Testimonials />
        <WorldMapSection />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
