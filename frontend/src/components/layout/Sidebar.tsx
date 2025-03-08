import React from "react";
import { cn } from "@/lib/utils";
import { 
  FolderKanban, 
  ChevronLeft,
  ChevronRight,
  LogOut,
  User,
  Moon,
  Sun
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface SidebarProps {
  isOpen: boolean;
  toggle: () => void;
  showLogo?: boolean;
  className?: string;
}

interface SidebarItemProps {
  icon: React.ElementType;
  label: string;
  href: string;
  isActive?: boolean;
  collapsed?: boolean;
}

const SidebarItem = ({ icon: Icon, label, href, isActive, collapsed = false }: SidebarItemProps) => {
  if (collapsed) {
    return (
      <TooltipProvider>
        <Tooltip delayDuration={0}>
          <TooltipTrigger asChild>
            <Link
              to={href}
              className={cn(
                "flex items-center justify-center rounded-md p-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
                isActive ? "bg-accent text-accent-foreground" : "transparent"
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="sr-only">{label}</span>
            </Link>
          </TooltipTrigger>
          <TooltipContent side="right">
            <p>{label}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <Link
      to={href}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
        isActive ? "bg-accent text-accent-foreground" : "transparent"
      )}
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </Link>
  );
};

const Sidebar = ({ isOpen, toggle, showLogo = false, className }: SidebarProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const currentPath = location.pathname;
  
  // Memoize the user initial to prevent unnecessary re-renders
  const userInitial = React.useMemo(() => {
    if (user?.name && user.name.trim()) {
      return user.name.charAt(0).toUpperCase();
    }
    return null;
  }, [user?.name]);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  // Memoize the avatar fallback content
  const avatarFallback = React.useMemo(() => {
    if (userInitial) {
      return userInitial;
    }
    return <User className="h-4 w-4" />;
  }, [userInitial]);

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-20 flex h-full flex-col border-r border-[hsl(var(--border))] bg-[hsl(var(--background))] shadow-md transition-all duration-300 ease-in-out",
        isOpen ? "w-64" : "w-16",
        className
      )}
    >
      <div className="flex h-full flex-col px-3 py-4">
        {showLogo && (
          <div className="flex items-center justify-between">
            {isOpen ? (
              <div className="flex items-center gap-2">
                <span className="text-3xl font-bold font-league-spartan tracking-tight">stratigo</span>
              </div>
            ) : (
              <div></div>
            )}
            <Button variant="ghost" size="icon" onClick={toggle} className="h-8 w-8">
              {isOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </Button>
          </div>
        )}
        
        <div className="mt-8 space-y-2">
          <SidebarItem 
            icon={FolderKanban}
            label="Dashboard" 
            href="/dashboard" 
            isActive={currentPath === "/dashboard"} 
            collapsed={!isOpen}
          />
        </div>
        
        <div className="mt-8 space-y-2">
          {isOpen ? (
            <Button
              variant="ghost"
              className="w-full justify-start px-3"
              onClick={toggleTheme}
            >
              {theme === 'dark' ? (
                <Sun className="mr-2 h-4 w-4" />
              ) : (
                <Moon className="mr-2 h-4 w-4" />
              )}
              {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
            </Button>
          ) : (
            <TooltipProvider>
              <Tooltip delayDuration={0}>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleTheme}
                    aria-label={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                  >
                    {theme === 'dark' ? (
                      <Sun className="h-4 w-4" />
                    ) : (
                      <Moon className="h-4 w-4" />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
        
        {showLogo && user && (
          <div className="mt-auto">
            <Separator className="my-4" />
            {isOpen ? (
              <div className="flex flex-col space-y-4">
                <div className="flex items-center space-x-3 rounded-md px-3 py-2">
                  <Avatar className="h-9 w-9">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {avatarFallback}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{user?.name || "User"}</span>
                    <span className="text-xs text-muted-foreground">{user?.email || ""}</span>
                  </div>
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="justify-start mb-2"
                  onClick={handleLogout}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              </div>
            ) : (
              <div className="flex flex-col items-center space-y-4 mb-2">
                <TooltipProvider>
                  <Tooltip delayDuration={0}>
                    <TooltipTrigger asChild>
                      <Avatar className="h-9 w-9">
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          {avatarFallback}
                        </AvatarFallback>
                      </Avatar>
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      <p>{user?.name || "User"}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                
                <TooltipProvider>
                  <Tooltip delayDuration={0}>
                    <TooltipTrigger asChild>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={handleLogout}
                        aria-label="Logout"
                      >
                        <LogOut className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      <p>Logout</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
