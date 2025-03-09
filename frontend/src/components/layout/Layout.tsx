import React from "react";
import Navbar from "./Navbar";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { useLocation } from "react-router-dom";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const { isLoggedIn } = useAuth();
  const location = useLocation();

  return (
    <div className="relative min-h-screen bg-[hsl(var(--background))]">
      {/* Navbar */}
      <Navbar />
      
      <main
        className={cn(
          "pt-20 px-4 pb-8 transition-all duration-300 ease-in-out",
          "max-w-7xl mx-auto"
        )}
      >       
        <div className="mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
