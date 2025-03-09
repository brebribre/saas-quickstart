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
      title: "Smart Chrome Extension",
      description: "Automatically fill out job applications with one click. Works across multiple job sites and customizes data for each application.",
      icon: Chrome,
      highlights: ["Form auto-detection", "One-click fill", "Custom mappings", "Multi-site support"]
    },
    {
      title: "AI Cover Letter Generator",
      description: "Create personalized cover letters in seconds using AI. Tailored to each job posting and your experience.",
      icon: Bot,
      highlights: ["Job-specific content", "Professional tone", "Quick generation", "Easy customization"]
    },
    {
      title: "Professional CV Builder",
      description: "Build ATS-friendly resumes with modern templates. Highlight your skills and experience effectively.",
      icon: FileCheck,
      highlights: ["ATS-optimized", "Modern templates", "Skills focus", "Easy updates"]
    },
    {
      title: "Application Tracking",
      description: "Track your job applications, set reminders, and analyze your application success rate.",
      icon: BarChart3,
      highlights: ["Status tracking", "Analytics", "Reminders", "Progress insights"]
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
              <span className="text-[hsl(var(--foreground))]"> - Your Job Search Ally</span>
            </h1>
            <p className="text-xl md:text-2xl text-[hsl(var(--muted-foreground))] max-w-3xl mx-auto mb-10">
              Apply smarter, not harder. Automate your job applications, create personalized cover letters, 
              and build stunning resumes with our intelligent tools.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="font-medium">
                <Link to="/register">
                  Get Started Free
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="font-medium">
                <Link to="/login">
                  Sign In
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
              Your Complete Job Application Toolkit
            </h2>
            <p className="mt-4 text-lg text-[hsl(var(--muted-foreground))]">
              Everything you need to streamline your job search in one place
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
          <h2 className="text-3xl font-bold mb-6 text-[hsl(var(--foreground))]">Ready to simplify your job search?</h2>
          <p className="text-[hsl(var(--muted-foreground))] mb-8 max-w-2xl mx-auto">
            Join thousands of job seekers who are saving time and getting more interviews with Stratigo's 
            intelligent application tools. Start your efficient job search today - it's free!
          </p>
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Button asChild size="lg" className="font-medium">
              <Link to="/register">
                Start Applying Smarter
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