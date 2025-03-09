import React from 'react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle } from 'lucide-react';
import Layout from '@/components/layout/Layout';

const Home = () => {
  const features = [
    "Modern UI with Tailwind CSS",
    "Responsive design for all devices",
    "Dark and light mode support",
    "Secure authentication system",
    "Scalable architecture",
    "Built with Vue and shadcn components"
  ];

  return (
    <Layout>
      {/* Hero Section / Jumbotron */}
      <div className="relative py-20 md:py-32 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-background pointer-events-none" aria-hidden="true" />
        
        <div className="relative max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-600">
                Stratigo
              </span>
              <span> - Modern Web Solutions</span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto mb-10">
              Building exceptional digital experiences with cutting-edge technology and thoughtful design.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="font-medium">
                <Link to="/dashboard">
                  Go to Dashboard
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="font-medium">
                <Link to="/login">
                  Login
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Company Description */}
      <div className="py-16 bg-muted/30">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">About Stratigo</h2>
              <p className="text-muted-foreground mb-6">
                Stratigo is a forward-thinking technology company specializing in creating modern, 
                user-friendly web applications. We combine technical expertise with creative design 
                to deliver solutions that not only meet but exceed our clients' expectations.
              </p>
              <p className="text-muted-foreground mb-6">
                Our team of experienced developers and designers work collaboratively to build 
                scalable, maintainable, and beautiful applications that help businesses thrive 
                in the digital landscape.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-primary" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-background rounded-lg p-6 shadow-lg border">
              <h3 className="text-2xl font-bold mb-4">Our Technology Stack</h3>
              <p className="mb-4">
                We use the latest technologies to build robust and scalable applications:
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="font-semibold mb-2">Frontend</h4>
                  <ul className="space-y-1 text-sm">
                    <li>Vue.js</li>
                    <li>Tailwind CSS</li>
                    <li>shadcn components</li>
                    <li>TypeScript</li>
                  </ul>
                </div>
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="font-semibold mb-2">Backend</h4>
                  <ul className="space-y-1 text-sm">
                    <li>Node.js</li>
                    <li>Express</li>
                    <li>PostgreSQL</li>
                    <li>Supabase</li>
                  </ul>
                </div>
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="font-semibold mb-2">DevOps</h4>
                  <ul className="space-y-1 text-sm">
                    <li>Docker</li>
                    <li>GitHub Actions</li>
                    <li>Netlify</li>
                    <li>Vercel</li>
                  </ul>
                </div>
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="font-semibold mb-2">Tools</h4>
                  <ul className="space-y-1 text-sm">
                    <li>Figma</li>
                    <li>VS Code</li>
                    <li>Git</li>
                    <li>Postman</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="py-16 bg-background">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to get started?</h2>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join us today and experience the difference of working with a team that's passionate about creating exceptional digital experiences.
          </p>
          <Button asChild size="lg" className="font-medium">
            <Link to="/register">
              Create an Account
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>
    </Layout>
  );
};

export default Home; 