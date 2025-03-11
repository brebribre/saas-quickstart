import React, { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const { isLoggedIn } = useAuth();
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setIsSidebarOpen(false);
      }
    };

    // Initial check
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="relative min-h-screen bg-[hsl(var(--background))]">
      {/* Sidebar with mobile overlay */}
      <div className={cn(
        "md:relative fixed inset-0 z-50 bg-background/80 backdrop-blur-sm",
        isSidebarOpen && isMobile ? "block" : "hidden",
        "md:block md:bg-transparent md:backdrop-blur-none"
      )}>
        <Sidebar isOpen={isSidebarOpen} toggle={toggleSidebar} />
      </div>
      
      <main
        className={cn(
          "transition-all duration-300 ease-in-out",
          "min-h-screen",
          "md:ml-16",
          isSidebarOpen && !isMobile ? "md:ml-64" : "ml-0",
          "p-4 md:p-8"
        )}
      >       
        <div className="mx-auto">
          {children}
        </div>
      </main>

      {/* Mobile toggle button */}
      <Button
        variant="outline"
        size="icon"
        className={cn(
          "fixed bottom-4 right-4 h-10 w-10 rounded-full shadow-md md:hidden",
          "bg-primary text-primary-foreground hover:bg-primary/90",
          "border-2 border-background"
        )}
        onClick={toggleSidebar}
      >
        <Menu className="h-4 w-4" />
      </Button>
    </div>
  );
};

export default Layout;
