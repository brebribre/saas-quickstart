import React, { createContext, useContext, useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Session, User } from "@supabase/supabase-js";
import { toast } from "sonner";

interface AuthUser {
  name?: string;
  email: string;
  id: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isLoggedIn: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  session: Session | null;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session);
        setIsLoggedIn(!!session);
        if (session?.user) {
          console.log("Auth state change - user metadata:", session.user.user_metadata);
          const userName = session.user.user_metadata?.name || 
                          session.user.user_metadata?.full_name || 
                          session.user.user_metadata?.preferred_username || "";
          console.log("Setting user name to:", userName);
          
          setUser({
            id: session.user.id,
            email: session.user.email || "",
            name: userName
          });
        } else {
          setUser(null);
        }
        setLoading(false);
      }
    );

    // Initial session check
    const initializeAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setSession(session);
      setIsLoggedIn(!!session);
      if (session?.user) {
        const userName = session.user.user_metadata?.name || 
                        session.user.user_metadata?.full_name || 
                        session.user.user_metadata?.preferred_username || "";
        setUser({
          id: session.user.id,
          email: session.user.email || "",
          name: userName
        });
      }
      setLoading(false);
    };

    initializeAuth();

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        throw error;
      }

      return;
    } catch (error: any) {
      toast.error("Login failed", {
        description: error.message || "Please check your credentials and try again."
      });
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name,
          },
        },
      });

      if (error) {
        throw error;
      }

      if (data.user) {
        toast.success("Registration successful", {
          description: "Please check your email to confirm your account."
        });
      }

      return;
    } catch (error: any) {
      toast.error("Registration failed", {
        description: error.message || "Please try again with different credentials."
      });
      throw error;
    }
  };

  const loginWithGoogle = async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      });

      if (error) {
        throw error;
      }

      return;
    } catch (error: any) {
      toast.error("Google login failed", {
        description: error.message || "Please try again later."
      });
      throw error;
    }
  };

  const logout = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) {
        throw error;
      }

      toast.success("Logged out successfully");
    } catch (error: any) {
      toast.error("Logout failed", {
        description: error.message || "Please try again."
      });
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoggedIn, login, register, loginWithGoogle, logout, session }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
