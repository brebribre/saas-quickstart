import React from "react";
import { cn } from "@/lib/utils";
import { 
  FolderKanban, 
  LogOut,
  User,
  Moon,
  Sun,
  Menu,
  Home
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";

interface NavbarProps {
  className?: string;
}

const Navbar = ({ className }: NavbarProps) => {
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

  const navItems = [
    { label: "Home", href: "/", icon: Home },
    { label: "Dashboard", href: "/dashboard", icon: FolderKanban }
  ];

  // Custom register button class based on theme
  const registerButtonClass = theme === 'dark' 
    ? "bg-white text-black hover:bg-white/90" 
    : "bg-black text-white hover:bg-black/90";

  return (
    <nav className={cn(
      "fixed top-0 left-0 right-0 z-50 flex h-16 items-center border-b border-[hsl(var(--border))] bg-[hsl(var(--background))] px-4 shadow-sm",
      className
    )}>
      <div className="flex w-full items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <span className="text-3xl font-bold font-league-spartan tracking-tight">stratigo</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-4">
          {navItems.map((item) => (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                "flex items-center gap-2 px-3 py-2 text-sm font-medium transition-colors hover:text-[hsl(var(--primary))]",
                currentPath === item.href ? "text-[hsl(var(--primary))]" : "text-[hsl(var(--foreground))]"
              )}
            >
              <item.icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          ))}
        </div>

        {/* Right side actions */}
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>

          {/* User Profile or Login/Register Buttons */}
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                  <Avatar className="h-9 w-9">
                    <AvatarFallback className="bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]">
                      {avatarFallback}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>
                  <div className="flex flex-col">
                    <span>{user?.name || "User"}</span>
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">{user?.email || ""}</span>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Logout</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => navigate('/login')}
              >
                Login
              </Button>
              <Button 
                className={cn("transition-colors", registerButtonClass)}
                size="sm"
                onClick={() => navigate('/register')}
              >
                Register
              </Button>
            </div>
          )}

          {/* Mobile Menu */}
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="bg-[hsl(var(--background))]">
              <div className="flex flex-col gap-4 py-4">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    to={item.href}
                    className={cn(
                      "flex items-center gap-2 px-3 py-2 text-sm font-medium transition-colors hover:text-[hsl(var(--primary))]",
                      currentPath === item.href ? "text-[hsl(var(--primary))]" : "text-[hsl(var(--foreground))]"
                    )}
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                ))}
                
                {/* Login/Register buttons for mobile when not logged in */}
                {!user && (
                  <div className="flex flex-col gap-2 mt-4 px-3">
                    <Button 
                      variant="outline" 
                      className="w-full justify-start"
                      onClick={() => navigate('/login')}
                    >
                      <User className="mr-2 h-4 w-4" />
                      Login
                    </Button>
                    <Button 
                      className={cn("w-full justify-start transition-colors", registerButtonClass)}
                      onClick={() => navigate('/register')}
                    >
                      Register
                    </Button>
                  </div>
                )}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 