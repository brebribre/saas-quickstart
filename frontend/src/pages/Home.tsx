import React from 'react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  Chrome, 
  FileText, 
  FileCheck, 
  BarChart3,
  Sparkles,
  Clock,
  CheckCircle2,
  Bot
} from 'lucide-react';
import Layout from '@/components/layout/Layout';
import { cn } from "@/lib/utils";
import { motion, useReducedMotion } from 'framer-motion';

const Home = () => {
  // Respect user's reduced motion preferences
  const shouldReduceMotion = useReducedMotion();

  const features = [
    {
      title: "Ekstensi Chrome Pintar",
      description: "Isi formulir lamaran kerja secara otomatis dengan satu klik. Bekerja di berbagai situs lowongan kerja dan menyesuaikan data untuk setiap lamaran.",
      icon: Chrome,
      highlights: ["Deteksi formulir otomatis", "Isi dengan satu klik", "Pemetaan data kustom", "Dukungan multi-situs"]
    },
    {
      title: "Generator Surat Lamaran AI",
      description: "Buat surat lamaran yang dipersonalisasi dalam hitungan detik menggunakan AI. Disesuaikan dengan setiap lowongan kerja dan pengalaman Anda.",
      icon: Bot,
      highlights: ["Konten sesuai lowongan", "Nada profesional", "Generasi cepat", "Mudah dikustomisasi"]
    },
    {
      title: "Pembuat CV Profesional",
      description: "Buat CV yang ramah ATS dengan template modern. Tonjolkan keterampilan dan pengalaman Anda secara efektif.",
      icon: FileCheck,
      highlights: ["Optimasi ATS", "Template modern", "Fokus keterampilan", "Mudah diperbarui"]
    },
    {
      title: "Pelacakan Lamaran",
      description: "Lacak lamaran kerja Anda, atur pengingat, dan analisis tingkat keberhasilan lamaran Anda.",
      icon: BarChart3,
      highlights: ["Pelacakan status", "Analitik", "Pengingat", "Wawasan progres"]
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: shouldReduceMotion ? 0 : 10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  return (
    <Layout>
      {/* Hero Section / Jumbotron */}
      <div className="relative py-20 md:py-32 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-[hsl(var(--primary))]/-5 via-[hsl(var(--background))] to-[hsl(var(--background))] pointer-events-none" aria-hidden="true" />
        
        <div className="relative max-w-5xl mx-auto px-4 sm:px-6">
          <motion.div 
            className="text-center"
            initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              <motion.span 
                className="bg-clip-text text-transparent bg-gradient-to-r from-[hsl(var(--primary))] to-[hsl(var(--primary))]"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                Stratigo
              </motion.span>
              <span className="text-[hsl(var(--foreground))]"> - Asisten Pencarian Kerja Anda</span>
            </h1>
            <p className="text-xl md:text-2xl text-[hsl(var(--muted-foreground))] max-w-3xl mx-auto mb-10">
              Lamar lebih cerdas, bukan lebih keras. Otomatiskan lamaran kerja Anda, buat surat lamaran yang dipersonalisasi, 
              dan buat CV yang mengesankan dengan alat cerdas kami.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="font-medium">
                <Link to="/register">
                  Mulai Gratis
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="font-medium">
                <Link to="/login">
                  Masuk
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-[hsl(var(--muted))]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <motion.div 
            className="text-center mb-12"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.3 }}
          >
            <h2 className="text-3xl font-bold text-[hsl(var(--foreground))]">
              Perangkat Lengkap untuk Lamaran Kerja Anda
            </h2>
            <p className="mt-4 text-lg text-[hsl(var(--muted-foreground))]">
              Semua yang Anda butuhkan untuk mengefisienkan pencarian kerja dalam satu tempat
            </p>
          </motion.div>

          <motion.div 
            className="grid sm:grid-cols-2 gap-8"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
          >
            {features.map((feature, index) => (
              <motion.div 
                key={index}
                variants={itemVariants}
                whileHover={{ scale: 1.01 }}
                className="bg-[hsl(var(--background))] rounded-xl p-8 shadow-lg border border-[hsl(var(--border))] flex flex-col"
              >
                <div className="flex items-center gap-4 mb-6">
                  <motion.div 
                    className="p-3 rounded-lg bg-[hsl(var(--primary)/0.1)]"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <feature.icon className="h-8 w-8 text-[hsl(var(--primary))]" />
                  </motion.div>
                  <h3 className="font-semibold text-xl text-[hsl(var(--foreground))]">
                    {feature.title}
                  </h3>
                </div>
                
                <p className="text-[hsl(var(--muted-foreground))] mb-4">
                  {feature.description}
                </p>

                <div className="mt-auto">
                  <div className="border-t border-[hsl(var(--border))] pt-4">
                    <ul className="space-y-2">
                      {feature.highlights.map((highlight, i) => (
                        <li 
                          key={i} 
                          className="flex items-center gap-2 text-sm text-[hsl(var(--foreground))]"
                        >
                          <CheckCircle2 className="h-4 w-4 text-[hsl(var(--primary))]" />
                          {highlight}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="py-16 bg-[hsl(var(--background))]">
        <motion.div 
          className="max-w-5xl mx-auto px-4 sm:px-6 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.3 }}
        >
          <h2 className="text-3xl font-bold mb-6 text-[hsl(var(--foreground))]">Siap mempermudah pencarian kerja Anda?</h2>
          <p className="text-[hsl(var(--muted-foreground))] mb-8 max-w-2xl mx-auto">
            Bergabung dengan ribuan pencari kerja yang menghemat waktu dan mendapatkan lebih banyak wawancara dengan 
            alat lamaran cerdas Stratigo. Mulai pencarian kerja efisien Anda hari ini - gratis!
          </p>
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Button asChild size="lg" className="font-medium">
              <Link to="/register">
                Mulai Melamar Lebih Cerdas
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default Home; 