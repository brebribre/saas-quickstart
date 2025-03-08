import React, { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(() => {
    // Initialize from localStorage or default to true
    const savedState = localStorage.getItem('sidebarOpen');
    return savedState !== null ? savedState === 'true' : true;
  });
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const { isLoggedIn } = useAuth();
  const location = useLocation();
  
  // Save sidebar state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('sidebarOpen', isSidebarOpen.toString());
  }, [isSidebarOpen]);
  
  // Close mobile sidebar when location changes
  useEffect(() => {
    setIsMobileSidebarOpen(false);
  }, [location.pathname]);
  
  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };
  
  const toggleMobileSidebar = () => {
    setIsMobileSidebarOpen(prev => !prev);
  };

  return (
    <div className="relative min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <Sidebar 
        isOpen={isSidebarOpen} 
        toggle={toggleSidebar} 
        showLogo={true}
        className="hidden md:block top-0"
      />
      
      {/* Mobile Sidebar Toggle Button */}
      <Button
        variant="outline"
        size="icon"
        onClick={toggleMobileSidebar}
        className="fixed bottom-4 right-4 z-50 rounded-full shadow-lg md:hidden"
        aria-label="Toggle mobile sidebar"
      >
        {isMobileSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>
      
      {/* Mobile Sidebar */}
      {isMobileSidebarOpen && (
        <Sidebar 
          isOpen={true} // Always fully open on mobile
          toggle={toggleMobileSidebar} 
          showLogo={true}
          className="md:hidden w-64 pb-safe z-40 top-0" // Show on mobile, hide on desktop
        />
      )}
      
      <main
        className={cn(
          "py-4 px-4 transition-all duration-300 ease-in-out",
          // Only apply margin on desktop
          isSidebarOpen ? "md:ml-64" : "md:ml-16",
          "mt-0",
          // Add bottom padding on mobile to prevent content from being covered by browser navigation bar
          "pb-20 md:pb-4"
        )}
      >       
        <div className="mx-auto">
          {children}
        </div>
      </main>
      
      {/* Overlay for mobile */}
      {isMobileSidebarOpen && (
        <div 
          className="fixed inset-0 z-30 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={toggleMobileSidebar}
        />
      )}
    </div>
  );
};

export default Layout;
